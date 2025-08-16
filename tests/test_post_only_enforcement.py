"""
Tests for POST_ONLY flag enforcement - only real safety tests, no theater.

These tests verify actual functionality of the enforce_post_only utility function
and flag preservation logic. Mock-based tests that don't verify real behavior
have been removed.
"""

import unittest

from bfxapi._utils.post_only_enforcement import enforce_post_only
from bfxapi.constants.order_flags import POST_ONLY


class TestPostOnlyUtility(unittest.TestCase):
    """Test the enforce_post_only utility function with real operations."""

    def test_enforce_post_only_with_none(self):
        """Test that None is handled correctly."""
        result = enforce_post_only(None)
        self.assertEqual(result, POST_ONLY)

    def test_enforce_post_only_with_zero(self):
        """Test that 0 returns POST_ONLY."""
        result = enforce_post_only(0)
        self.assertEqual(result, POST_ONLY)

    def test_enforce_post_only_with_existing_flags(self):
        """Test that existing flags are preserved while adding POST_ONLY."""
        # Test with a different flag (e.g., HIDDEN = 64)
        HIDDEN = 64
        result = enforce_post_only(HIDDEN)
        self.assertEqual(result, POST_ONLY | HIDDEN)
        self.assertEqual(result, 4096 | 64)  # Should be 4160

    def test_enforce_post_only_idempotent(self):
        """Test that applying enforce_post_only twice doesn't change the result."""
        result1 = enforce_post_only(0)
        result2 = enforce_post_only(result1)
        self.assertEqual(result1, result2)
        self.assertEqual(result2, POST_ONLY)

    def test_enforce_post_only_with_max_flags(self):
        """Test with maximum possible flag values to ensure no overflow."""
        # Test with a very large flag value (all bits except sign bit)
        MAX_FLAG = 2**31 - 1  # Maximum positive int32
        result = enforce_post_only(MAX_FLAG)
        
        # POST_ONLY should still be set
        self.assertTrue(result & POST_ONLY)
        # All original bits should be preserved
        self.assertEqual(result, MAX_FLAG | POST_ONLY)
        
        # Test with common maximum flag combinations
        ALL_COMMON_FLAGS = 64 | 1024 | 2048 | 4096 | 8192  # Multiple flags
        result = enforce_post_only(ALL_COMMON_FLAGS)
        self.assertTrue(result & POST_ONLY)
        self.assertEqual(result, ALL_COMMON_FLAGS)  # POST_ONLY already included

    def test_market_order_rejected(self):
        """Test that MARKET orders are rejected with clear error message."""
        # Test basic MARKET order
        with self.assertRaises(ValueError) as cm:
            enforce_post_only(0, order_type="MARKET")
        
        error_msg = str(cm.exception)
        self.assertIn("incompatible with POST_ONLY", error_msg)
        self.assertIn("LIMIT order", error_msg)
        
        # Test various market order formats
        market_types = ["MARKET", "EXCHANGE MARKET", "FOK MARKET", "IOC MARKET", "market", "Market"]
        for order_type in market_types:
            with self.assertRaises(ValueError) as cm:
                enforce_post_only(0, order_type=order_type)
            self.assertIn("incompatible", str(cm.exception))
    
    def test_limit_orders_accepted(self):
        """Test that LIMIT orders are accepted."""
        limit_types = ["LIMIT", "EXCHANGE LIMIT", "FOK LIMIT", "IOC LIMIT", "limit", "Limit"]
        for order_type in limit_types:
            # Should not raise any exception
            result = enforce_post_only(0, order_type=order_type)
            self.assertEqual(result, POST_ONLY)
            
            # Also test with existing flags
            result = enforce_post_only(64, order_type=order_type)
            self.assertEqual(result, POST_ONLY | 64)


class TestIntegrationScenarios(unittest.TestCase):
    """Test complex integration scenarios with real flag operations."""

    def test_none_flags_handling_across_layers(self):
        """Test that None flags are properly handled without TypeErrors."""
        # This test ensures the fix for the TypeError bug is working

        # Test utility function
        result = enforce_post_only(None)
        self.assertEqual(result, POST_ONLY)

        # Test with actual flag values
        result = enforce_post_only(0)
        self.assertEqual(result, POST_ONLY)

        result = enforce_post_only(64)  # HIDDEN flag
        self.assertEqual(result, POST_ONLY | 64)

    def test_flag_preservation(self):
        """Test that other flags are preserved when adding POST_ONLY."""
        HIDDEN = 64
        REDUCE_ONLY = 1024

        # Test single flag preservation
        result = enforce_post_only(HIDDEN)
        self.assertTrue(result & POST_ONLY)
        self.assertTrue(result & HIDDEN)

        # Test multiple flags preservation
        combined = HIDDEN | REDUCE_ONLY
        result = enforce_post_only(combined)
        self.assertTrue(result & POST_ONLY)
        self.assertTrue(result & HIDDEN)
        self.assertTrue(result & REDUCE_ONLY)

    def test_post_only_already_set(self):
        """Test that POST_ONLY flag is idempotent."""
        # If POST_ONLY is already set, it should remain set
        flags_with_post_only = POST_ONLY | 64
        result = enforce_post_only(flags_with_post_only)
        self.assertEqual(result, flags_with_post_only)


class TestIntegrationPostOnly(unittest.IsolatedAsyncioTestCase):
    """Integration tests that verify POST_ONLY is added through the call path."""
    
    def test_middleware_integration(self):
        """Test that middleware adds POST_ONLY to order endpoints."""
        from unittest.mock import MagicMock, patch
        from bfxapi.rest._interface.middleware import Middleware
        import json
        
        # Mock only at the HTTP boundary
        with patch('bfxapi.rest._interface.middleware.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = []
            mock_post.return_value = mock_response
            
            middleware = Middleware("https://api.bitfinex.com", "key", "secret")
            
            # Submit order without flags
            middleware.post("auth/w/order/submit", body={
                "type": "EXCHANGE LIMIT",
                "symbol": "tBTCUSD",
                "amount": 0.01,
                "price": 50000
            })
            
            # Verify the actual JSON sent includes POST_ONLY
            actual_body = json.loads(mock_post.call_args[1]['data'])
            self.assertEqual(actual_body['flags'], 4096)
            
            # Test update order also adds POST_ONLY
            middleware.post("auth/w/order/update", body={
                "id": 12345,
                "amount": 0.02
            })
            
            actual_body = json.loads(mock_post.call_args[1]['data'])
            self.assertEqual(actual_body['flags'], 4096)
    
    async def test_websocket_update_order_integration(self):
        """Test that WebSocket update_order enforces POST_ONLY flag."""
        from unittest.mock import AsyncMock, MagicMock, patch
        from bfxapi.websocket._client.bfx_websocket_inputs import BfxWebSocketInputs
        
        # Mock the WebSocket client
        mock_client = MagicMock()
        mock_client._BfxWebSocketClient__bucket = MagicMock()
        mock_client._BfxWebSocketClient__bucket.put = AsyncMock()
        
        inputs = BfxWebSocketInputs(mock_client)
        
        # Patch the private method to be async
        with patch.object(inputs, '_BfxWebSocketInputs__handle_websocket_input', new_callable=AsyncMock) as mock_handle:
            # Test update_order without flags
            await inputs.update_order(
                id=123456,
                price=51000,
                flags=None
            )
            
            # Verify POST_ONLY was added
            mock_handle.assert_called_once()
            call_args = mock_handle.call_args
            self.assertEqual(call_args[0][0], "ou")  # update order command
            payload = call_args[0][1]
            self.assertEqual(payload["flags"], 4096)  # POST_ONLY enforced
            
            # Reset and test with existing flags
            mock_handle.reset_mock()
            await inputs.update_order(
                id=123456,
                price=52000,
                flags=64  # HIDDEN
            )
            
            call_args = mock_handle.call_args
            payload = call_args[0][1]
            self.assertEqual(payload["flags"], 4096 | 64)  # Both flags preserved
            
    async def test_websocket_submit_order_integration(self):
        """Test that WebSocket submit_order adds POST_ONLY through the call path."""
        from bfxapi.websocket._client.bfx_websocket_inputs import BfxWebSocketInputs
        
        # Create a mock that captures the actual data sent
        sent_data = {}
        
        async def capture_handler(event, data):
            sent_data['event'] = event
            sent_data['data'] = data
            
        inputs = BfxWebSocketInputs(capture_handler)
        
        # Submit order without flags
        await inputs.submit_order(
            type="EXCHANGE LIMIT",
            symbol="tBTCUSD",
            amount=0.01,
            price=50000
        )
        
        # Verify POST_ONLY was added
        self.assertEqual(sent_data['event'], 'on')
        self.assertEqual(sent_data['data']['flags'], 4096)


if __name__ == "__main__":
    unittest.main()