import requests
import base64
import os
import json

def test_ocr():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not set")
        return

    # Load sample image (tractor.jpg or invoice.jpg)
    # We'll use a dummy small image if file not found, but better to use real one
    image_path = "data/media/invoice.jpg"
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found")
        return

    with open(image_path, "rb") as f:
        payload = f.read()

    api_url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    print(f"Calling {api_url[:40]}...")

    b64_image = base64.b64encode(payload).decode("utf-8")
    body = {
        "requests": [
            {
                "image": {"content": b64_image},
                "features": [{"type": "DOCUMENT_TEXT_DETECTION"}]
            }
        ]
    }

    try:
        resp = requests.post(api_url, json=body, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_ocr()
