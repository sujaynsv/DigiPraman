"""Mock Verification Services for Jury Defense (Simulating Ext. APIs)."""

from typing import Dict, Optional
from app.services.mock_data import STATE_CODES, VALID_GST_INVOICES, SANCTIONED_LOANS

class VerificationService:
    """
    Simulates Government GST and Core Banking connections.
    In a real production system, these would be REST/gRPC calls to external gateways.
    For the Hackathon, we check against a local 'Source of Truth'.
    """

    # --- MOCK DATABASES ---
    
    import re

    # Regex for India GSTIN (15 chars)
    # 2 digits + 5 letters + 4 digits + 1 letter + 1 char + Z + 1 char
    GST_REGEX = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

    # Valid State Codes (2025 List subset)
    STATE_CODES = STATE_CODES

    # 1. GST Portal Mock (Valid Invoices)
    # Updated with Valid GSTINs
    VALID_GST_INVOICES = VALID_GST_INVOICES

    # 2. Bank Core System Mock (Sanctioned Loans)
    # Maps Applicant ID -> Asset Type they are allowed to buy
    SANCTIONED_LOANS = SANCTIONED_LOANS

    @classmethod
    def validate_gstin_structure(cls, gstin: str) -> Dict[str, object]:
        """Checks Regex, Length, and State Code."""
        if not gstin or len(gstin) != 15:
            return {"valid": False, "error": "Invalid Length (Must be 15 chars)"}
        
        # 1. Regex Check (Structure)
        if not cls.GST_REGEX.match(gstin):
            return {"valid": False, "error": "Invalid Format (Regex mismatch)"}
            
        # 2. State Code Check
        state_code = gstin[:2]
        if state_code not in cls.STATE_CODES:
            return {"valid": False, "error": f"Invalid State Code '{state_code}'"}
            
        return {"valid": True, "state": cls.STATE_CODES[state_code]}

    @classmethod
    def verify_gst_invoice(cls, invoice_number: Optional[str], declared_gstin: Optional[str] = None) -> Dict[str, object]:
        """
        Simulates calling GSTN API.
        Now validates the GSTIN structure too.
        """
        validation = {"gstin_valid": False, "structure_error": None}
        
        # If a GSTIN is provided, validate it first
        if declared_gstin:
            struct_check = cls.validate_gstin_structure(declared_gstin)
            if not struct_check["valid"]:
                return {
                    "verified": False,
                    "reason": f"Invalid GSTIN: {struct_check['error']}",
                    "structure_check": struct_check
                }
            validation = {"gstin_valid": True, "state": struct_check["state"]}

        if not invoice_number:
            return {"verified": False, "reason": "No Invoice Number extracted"}
        
        inv_key = invoice_number.strip().upper()
        
        if inv_key in cls.VALID_GST_INVOICES:
            record = cls.VALID_GST_INVOICES[inv_key]
            
            # CRITICAL: If the found record has NO GSTIN (Unregistered Vendor), we must flag it.
            if record.get("gstin") is None:
                return {
                    "verified": False,
                    "reason": "Invoice Found, but Vendor is NOT GST Registered (No GSTIN)",
                    "registered_data": record
                }

            # If validated GSTIN provided, check if it matches the record
            if declared_gstin and declared_gstin != record["gstin"]:
                 return {
                    "verified": False, 
                    "reason": f"Invoice found but GSTIN mismatch! Expected {record['gstin']}",
                    "registered_data": record
                 }

            return {
                "verified": True,
                "reason": "Matched with GSTN Records",
                "gstin_validation": validation,
                "registered_data": record
            }
        
        return {
            "verified": False,
            "reason": f"Invoice {inv_key} NOT found in GST Government DB"
        }

    @classmethod
    def verify_bank_sanction(cls, applicant_id: str, declared_asset: str) -> Dict[str, object]:
        """
        Simulates calling Bank Core Banking System (CBS).
        Check if this applicant is actually approved for this asset.
        """
        if applicant_id not in cls.SANCTIONED_LOANS:
            return {
                "match": False,
                "reason": "Applicant has no active loan sanctions"
            }
        
        loan_record = cls.SANCTIONED_LOANS[applicant_id]
        expected_asset = loan_record["allowed_asset"].lower()
        actual_asset = (declared_asset or "").lower()

        # Simple string match (e.g. "tractor" in "mahindra tractor")
        if expected_asset in actual_asset or actual_asset in expected_asset:
            return {
                "match": True,
                "reason": "Matches Sanction Advice",
                "sanction_details": loan_record
            }
        
        return {
            "match": False,
            "reason": f"Sanction Deviation: Approved for '{expected_asset}', but bought '{actual_asset}'"
        }
