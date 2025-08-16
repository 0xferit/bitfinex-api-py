from typing import Optional

from bfxapi.constants.order_flags import POST_ONLY


def enforce_post_only(flags: Optional[int], order_type: Optional[str] = None) -> int:
    """
    Ensure POST_ONLY flag is set, preserving other flags.
    
    Validates that order type is compatible with POST_ONLY.

    Args:
        flags: Existing flags value (can be None)
        order_type: Order type string (optional, for validation)

    Returns:
        Flags value with POST_ONLY bit set
        
    Raises:
        ValueError: If order type is incompatible with POST_ONLY
    """
    # Validate order type if provided
    if order_type:
        # Normalize order type for comparison
        normalized_type = order_type.upper()
        
        # Check for MARKET order types (incompatible with POST_ONLY)
        if 'MARKET' in normalized_type:
            raise ValueError(
                f"Order type '{order_type}' is incompatible with POST_ONLY enforcement. "
                "POST_ONLY only works with limit-style orders. "
                "This fork enforces POST_ONLY on all orders for safety. "
                "Please use a LIMIT order type instead."
            )
    
    return POST_ONLY | (flags if flags is not None else 0)
