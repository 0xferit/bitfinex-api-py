from typing import Optional

from bfxapi.constants.order_flags import POST_ONLY


def enforce_post_only(flags: Optional[int]) -> int:
    """
    Ensure POST_ONLY flag is set, preserving other flags.

    Args:
        flags: Existing flags value (can be None)

    Returns:
        Flags value with POST_ONLY bit set
    """
    return POST_ONLY | (flags if flags is not None else 0)
