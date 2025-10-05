import decimal
import hashlib
from app.settings import settings


def calculate_signature(*args) -> str:
    """Create signature MD5."""
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()


def verify_payment_signature(
    out_sum: decimal.Decimal,
    invoice_id: int,
    signature_value: str,
    **custom_params
) -> bool:
    """Verify payment signature from Robokassa callback."""
    if not settings.ROBOKASSA_PASSWORD2:
        raise ValueError("Robokassa password2 not configured")
    
    merchant_password_2 = settings.ROBOKASSA_PASSWORD2
    
    # Sort custom parameters
    custom_params_str = ':'.join(f"{k}={v}" for k, v in sorted(custom_params.items()))
    
    expected_signature = calculate_signature(
        out_sum,
        invoice_id,
        merchant_password_2,
        custom_params_str
    )
    
    return expected_signature.upper() == signature_value.upper()
