from decimal import Decimal
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union

from bfxapi.constants.order_flags import POST_ONLY

_Handler = Callable[[str, Any], Awaitable[None]]


class BfxWebSocketInputs:
    def __init__(self, handle_websocket_input: _Handler) -> None:
        self.__handle_websocket_input = handle_websocket_input

    async def submit_order(
        self,
        type: str,
        symbol: str,
        amount: Union[str, float, Decimal],
        price: Union[str, float, Decimal],
        *,
        lev: Optional[int] = None,
        price_trailing: Optional[Union[str, float, Decimal]] = None,
        price_aux_limit: Optional[Union[str, float, Decimal]] = None,
        price_oco_stop: Optional[Union[str, float, Decimal]] = None,
        gid: Optional[int] = None,
        cid: Optional[int] = None,
        flags: Optional[int] = None,
        tif: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Submit a new order (ALWAYS post-only)."""
        # FORCE POST_ONLY flag - no exceptions
        flags = POST_ONLY | (flags or 0)
        
        await self.__handle_websocket_input(
            "on",
            {
                "type": type,
                "symbol": symbol,
                "amount": amount,
                "price": price,
                "lev": lev,
                "price_trailing": price_trailing,
                "price_aux_limit": price_aux_limit,
                "price_oco_stop": price_oco_stop,
                "gid": gid,
                "cid": cid,
                "flags": flags,  # ALWAYS has POST_ONLY
                "tif": tif,
                "meta": meta,
            },
        )

    async def update_order(
        self,
        id: int,
        *,
        amount: Optional[Union[str, float, Decimal]] = None,
        price: Optional[Union[str, float, Decimal]] = None,
        cid: Optional[int] = None,
        cid_date: Optional[str] = None,
        gid: Optional[int] = None,
        flags: Optional[int] = None,
        lev: Optional[int] = None,
        delta: Optional[Union[str, float, Decimal]] = None,
        price_aux_limit: Optional[Union[str, float, Decimal]] = None,
        price_trailing: Optional[Union[str, float, Decimal]] = None,
        tif: Optional[str] = None,
    ) -> None:
        """Update an existing order (ALWAYS maintains POST_ONLY)."""
        # ALWAYS include POST_ONLY, even if flags not provided
        # This prevents bypass through flag-less updates
        if flags is not None:
            flags = POST_ONLY | flags
        else:
            # Force POST_ONLY even when no flags specified
            flags = POST_ONLY
        
        await self.__handle_websocket_input(
            "ou",
            {
                "id": id,
                "amount": amount,
                "price": price,
                "cid": cid,
                "cid_date": cid_date,
                "gid": gid,
                "flags": flags,  # Always has value now
                "lev": lev,
                "delta": delta,
                "price_aux_limit": price_aux_limit,
                "price_trailing": price_trailing,
                "tif": tif,
            },
        )

    async def cancel_order(
        self,
        *,
        id: Optional[int] = None,
        cid: Optional[int] = None,
        cid_date: Optional[str] = None,
    ) -> None:
        await self.__handle_websocket_input(
            "oc", {"id": id, "cid": cid, "cid_date": cid_date}
        )

    async def cancel_order_multi(
        self,
        *,
        id: Optional[List[int]] = None,
        cid: Optional[List[Tuple[int, str]]] = None,
        gid: Optional[List[int]] = None,
        all: Optional[bool] = None,
    ) -> None:
        await self.__handle_websocket_input(
            "oc_multi", {"id": id, "cid": cid, "gid": gid, "all": all}
        )

    async def submit_funding_offer(
        self,
        type: str,
        symbol: str,
        amount: Union[str, float, Decimal],
        rate: Union[str, float, Decimal],
        period: int,
        *,
        flags: Optional[int] = None,
    ) -> None:
        """Submit a funding offer (ALWAYS post-only)."""
        # FORCE POST_ONLY flag - no exceptions
        flags = POST_ONLY | (flags or 0)
        
        await self.__handle_websocket_input(
            "fon",
            {
                "type": type,
                "symbol": symbol,
                "amount": amount,
                "rate": rate,
                "period": period,
                "flags": flags,  # ALWAYS has POST_ONLY
            },
        )

    async def cancel_funding_offer(self, id: int) -> None:
        await self.__handle_websocket_input("foc", {"id": id})

    async def calc(self, *args: str) -> None:
        await self.__handle_websocket_input("calc", list(map(lambda arg: [arg], args)))
