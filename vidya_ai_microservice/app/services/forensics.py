
import re
import io
import logging
from typing import List, Dict, Tuple, Any
import numpy as np
from PIL import Image
import cv2
import piexif

# Setup logging
logger = logging.getLogger(__name__)

# Try importing Tesseract, but we might fallback or use Google Vision data in future refactors
try:
    import pytesseract
except ImportError:
    pytesseract = None
    logger.warning("pytesseract not found. Forensic OCR might fail if not using external data.")

class ForensicService:
    """
    Service to detect fake/forged invoices using:
    1. Metadata Forensics (EXIF, Software traces)
    2. Visual Heuristics (Blur, Logo detection, Formatting)
    3. Logical Checks (Arithmetic, Missing fields)
    """

    def __init__(self):
        pass

    def _load_image(self, image_data: bytes) -> Image.Image:
        return Image.open(io.BytesIO(image_data)).convert("RGB")

    def _image_to_numpy(self, img: Image.Image) -> np.ndarray:
        return np.array(img)[:, :, ::-1]  # RGB -> BGR for cv2

    def _ocr_with_boxes(self, img: Image.Image) -> Tuple[str, List[Dict]]:
        """
        Returns full OCR text and a list of text boxes.
        Uses Tesseract if available.
        TODO: In production, pass Google Vision bounds here to avoid Tesseract dependency.
        """
        if not pytesseract:
            logger.warning("pytesseract module not missing, skipping OCR.")
            return "", []
        
        # Check if tesseract is actually installed in PATH (Windows often missing it)
        try:
            # Simple check or just let it fail fast
            # We wrap the actual call in specific try/except to catch "FileNotFoundError" which pytesseract raises
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        except Exception:
            # Most likely "tesseract is not installed or it's not in your PATH"
            logger.warning("Tesseract binary not found. Skipping Forensic OCR.")
            return "", []

        try:
            n = len(data['text'])
            boxes = []
            full_text = []
            for i in range(n):
                txt = data['text'][i].strip()
                if txt:
                    boxes.append({
                        'text': txt,
                        'left': int(data['left'][i]),
                        'top': int(data['top'][i]),
                        'width': int(data['width'][i]),
                        'height': int(data['height'][i]),
                        'conf': float(data['conf'][i]) if data['conf'][i] != '-1' else -1.0
                    })
                    full_text.append(txt)
            return " ".join(full_text), boxes
        except Exception as e:
            logger.error(f"Tesseract OCR processing error: {e}")
            return "", []

    def _check_metadata(self, image_data: bytes, ocr_text: str) -> Dict:
        """Comparing EXIF creation date vs Printed Date."""
        res = {'exif_present': False, 'exif_datetime': None, 'exif_software': None, 'date_mismatch': False}
        try:
            exif_dict = piexif.load(image_data)
            # DateTimeOriginal
            if "Exif" in exif_dict and piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
                dt_bytes = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]
                dt = dt_bytes.decode('utf-8') if isinstance(dt_bytes, bytes) else dt_bytes
                res['exif_present'] = True
                res['exif_datetime'] = dt
            
            # Software tag (e.g., Photoshop)
            if "0th" in exif_dict and piexif.ImageIFD.Software in exif_dict['0th']:
                sw = exif_dict['0th'][piexif.ImageIFD.Software]
                res['exif_software'] = sw.decode('utf-8') if isinstance(sw, bytes) else sw
                res['exif_present'] = True
                
        except Exception:
            pass # No EXIF or error

        # Look for date in OCR
        date_patterns = [
            r'(\d{4}[-/]\d{2}[-/]\d{2})',
            r'(\d{2}[-/]\d{2}[-/]\d{4})',
            r'([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})'
        ]
        found_date = None
        for p in date_patterns:
            m = re.search(p, ocr_text)
            if m:
                found_date = m.group(1)
                break

        if res['exif_datetime'] and found_date:
            try:
                exif_dt = res['exif_datetime'].split(' ')[0].replace(':', '-')
                fd = found_date.replace('/', '-')
                # Compare Logic
                if len(fd.split('-')[0]) == 4:
                    found_norm = fd
                else: 
                    d, m, y = fd.split('-')
                    found_norm = f"{y}-{m}-{d}"
                
                if exif_dt != found_norm:
                    res['date_mismatch'] = True
            except Exception:
                pass
        
        return res

    def _check_blur_and_scaling(self, np_img: np.ndarray) -> Dict:
        gray = cv2.cvtColor(np_img, cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        var = lap.var()
        
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude = np.abs(fshift)
        h, w = magnitude.shape
        center_h, center_w = h // 2, w // 2
        low_radius = min(h, w) // 8
        y, x = np.ogrid[:h, :w]
        mask_low = (y - center_h)**2 + (x - center_w)**2 <= low_radius**2
        low_energy = magnitude[mask_low].sum()
        high_energy = magnitude.sum() - low_energy
        high_low_ratio = high_energy / (low_energy + 1e-8)
        
        return {'lap_var': float(var), 'high_low_ratio': float(high_low_ratio)}

    def _detect_logo_region(self, np_img: np.ndarray) -> bool:
        h, w, _ = np_img.shape
        top_area = np_img[0:int(h*0.18), int(w*0.1):int(w*0.9)]
        gray = cv2.cvtColor(top_area, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        nonwhite_ratio = 1.0 - (cv2.countNonZero(th) / (th.size) + 1e-8)
        return nonwhite_ratio > 0.02

    def _check_formatting(self, boxes: List[Dict]) -> Dict:
        res = {'font_variation_score': 0.0, 'alignment_variation': 0.0, 'missing_sections': []}
        if not boxes:
            res['font_variation_score'] = 1.0
            res['alignment_variation'] = 1.0
            res['missing_sections'] = ['merchant', 'total']
            return res

        heights = [b['height'] for b in boxes]
        if len(heights) >= 2:
            mean_h = np.mean(heights)
            std_h = np.std(heights)
            res['font_variation_score'] = float(std_h / (mean_h + 1e-8))

        rows = {}
        for b in boxes:
            top = b['top']
            key = top // 8
            rows.setdefault(key, []).append(b)
        
        hor_variances = []
        for row in rows.values():
            xs = [r['left'] for r in row]
            if len(xs) > 1:
                hor_variances.append(np.std(xs))
        
        res['alignment_variation'] = float(np.mean(hor_variances)) if hor_variances else 0.0

        full_text = " ".join([b['text'] for b in boxes]).lower()
        for kw in ['total', 'subtotal', 'tax', 'gst', 'merchant', 'invoice', 'date']:
            if kw not in full_text:
                res['missing_sections'].append(kw)
        
        return res

    def _check_arithmetic(self, ocr_text: str) -> Dict:
        cand = re.findall(r'(?:(?:₹|\$|rs\.?)\s*)?((?:\d{1,3}(?:,\d{3})*|\d+)(?:\.\d{1,2})?)', ocr_text.replace('O','0'))
        amounts = []
        for c in cand:
            try:
                v = float(c.replace(',', ''))
                if v > 0 and v < 10_000_000:
                    amounts.append(v)
            except:
                pass
        
        amounts = sorted(amounts)
        res = {'found_total_match': False, 'best_total': None, 'amount_count': len(amounts)}
        if not amounts:
            return res
            
        printed_total = amounts[-1]
        sum_items = sum(amounts[:-1])
        
        if sum_items > 0 and abs(sum_items - printed_total) / (printed_total + 1e-8) < 0.03:
            res['found_total_match'] = True
            res['best_total'] = printed_total
        else:
            # Subset sum check
            from itertools import combinations
            found = False
            best_t = None
            for r in range(1, min(6, len(amounts))):
                for comb in combinations(amounts[:-1], r):
                    s = sum(comb)
                    diff = abs(s - printed_total)
                    if diff / (printed_total + 1e-8) < 0.03:
                        found = True
                        best_t = s
                        break
                if found:
                    break
            res['found_total_match'] = found
            res['best_total'] = best_t if best_t else printed_total
            
        return res

    def analyze_invoice(self, image_data: bytes) -> Dict[str, Any]:
        """
        Main entry point. Analyzes bytes of an invoice image.
        """
        img = self._load_image(image_data)
        np_img = self._image_to_numpy(img)
        
        # 1. OCR
        ocr_text, boxes = self._ocr_with_boxes(img)
        
        # 2. Checks
        meta = self._check_metadata(image_data, ocr_text)
        blur = self._check_blur_and_scaling(np_img)
        logo = self._detect_logo_region(np_img)
        fmt = self._check_formatting(boxes)
        arithmetic = self._check_arithmetic(ocr_text)
        
        # 3. Score Calc
        score = 0.0
        reasons = []

        # Metadata
        if meta.get('exif_software'):
            s = meta['exif_software'].lower()
            if any(k in s for k in ['photoshop', 'gimp', 'editor']):
                score += 1.8
                reasons.append(f"EXIF software indicates editing: {meta['exif_software']}")
        
        if meta.get('date_mismatch'):
            score += 1.0
            reasons.append("EXIF date mismatch with printed transaction date")

        # Blur
        if blur['lap_var'] < 40:
            score += 0.8
            reasons.append(f"Image looks blurry (laplacian variance {blur['lap_var']:.1f})")
        
        if blur['high_low_ratio'] < 0.5:
            score += 0.6
            reasons.append("Low high-freq content (possible upscaling)")

        # Formatting
        if fmt['font_variation_score'] > 0.6:
            score += 0.8
            reasons.append(f"High font size variance ({fmt['font_variation_score']:.2f})")
            
        if fmt['alignment_variation'] > 20:
            score += 0.9
            reasons.append("Significant alignment variation")

        if len(fmt['missing_sections']) >= 3:
            score += 1.0
            reasons.append(f"Missing sections: {fmt['missing_sections']}")

        # Arithmetic
        if not arithmetic['found_total_match'] and arithmetic['amount_count'] >= 3:
            score += 1.4
            reasons.append("Arithmetic mismatch (Items sum != Total)")

        # Normalize score (Max ~8.0)
        max_possible = 8.0
        normalized = min(score / max_possible, 1.0)
        
        if normalized >= 0.6:
            label = "forged"
        elif normalized >= 0.3:
            label = "suspicious"
        else:
            label = "genuine"

        return {
            "label": label,
            "forensic_score": float(normalized),
            "reasons": reasons,
            "details": {
                "meta": meta,
                "blur": blur,
                "arithmetic": arithmetic
            }
        }
