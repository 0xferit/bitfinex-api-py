"""
Tests for POST_ONLY flag enforcement across all order and funding offer operations.
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from bfxapi._utils.post_only_enforcement import enforce_post_only
from bfxapi.constants.order_flags import POST_ONLY


class TestPostOnlyUtility(unittest.TestCase):
    """Test the enforce_post_only utility function."""

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


class TestRESTEndpointsPostOnly(unittest.TestCase):
    """Test POST_ONLY enforcement in REST endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        from bfxapi.rest._interfaces.rest_auth_endpoints import RestAuthEndpoints

        self.mock_interface = MagicMock()
        # Initialize with a real-looking host, then replace transport with mock
        self.endpoints = RestAuthEndpoints("https://api.bitfinex.com")
        self.endpoints._m = self.mock_interface

    @patch("bfxapi.types.serializers.Order.parse")
    @patch("bfxapi.rest._interfaces.rest_auth_endpoints.enforce_post_only")
    def test_submit_order_enforces_post_only(self, mock_enforce, _mock_order_parse):
        """Test that submit_order enforces POST_ONLY flag."""
        mock_enforce.return_value = POST_ONLY | 64  # Simulating POST_ONLY + HIDDEN
        self.mock_interface.post.return_value = [
            0,
            "on-req",
            None,
            None,
            [],
            None,
            "SUCCESS",
            "",
        ]

        self.endpoints.submit_order(
            type="LIMIT",
            symbol="tBTCUSD",
            amount=0.01,
            price=50000,
            flags=64,  # HIDDEN flag
        )

        # Verify enforce_post_only was called with the provided flags
        mock_enforce.assert_called_once_with(64)

        # Verify the post method was called with enforced flags
        call_args = self.mock_interface.post.call_args
        body = call_args.kwargs["body"]  # Body is passed as keyword argument
        self.assertIn("flags", body)

    @patch("bfxapi.types.serializers.Order.parse")
    @patch("bfxapi.rest._interfaces.rest_auth_endpoints.enforce_post_only")
    def test_update_order_always_enforces_post_only(
        self, mock_enforce, _mock_order_parse
    ):
        """Test that update_order always enforces POST_ONLY and includes flags."""
        mock_enforce.return_value = POST_ONLY
        self.mock_interface.post.return_value = [
            0,
            "ou-req",
            None,
            None,
            [],
            None,
            "SUCCESS",
            "",
        ]

        # Test with flags provided
        self.endpoints.update_order(id=12345, flags=0)
        mock_enforce.assert_called_with(0)

        # Reset
        mock_enforce.reset_mock()
        self.mock_interface.post.reset_mock()

        # Test without flags - still enforces
        self.endpoints.update_order(id=12345, amount=0.02)
        mock_enforce.assert_called_once_with(None)

        # Verify flags field is in the body
        call_args = self.mock_interface.post.call_args
        body = call_args.kwargs["body"]
        self.assertIn("flags", body)

    @patch("bfxapi.types.serializers.FundingOffer.parse")
    @patch("bfxapi.rest._interfaces.rest_auth_endpoints.enforce_post_only")
    def test_submit_funding_offer_does_not_send_flags(
        self, mock_enforce, _mock_fon_parse
    ):
        """Test that submit_funding_offer does not send or enforce flags."""
        self.mock_interface.post.return_value = [
            0,
            "fon-req",
            None,
            None,
            [],
            None,
            "SUCCESS",
            "",
        ]

        self.endpoints.submit_funding_offer(
            type="LIMIT", symbol="fUSD", amount=1000, rate=0.0001, period=2
        )

        mock_enforce.assert_not_called()

        call_args = self.mock_interface.post.call_args
        body = call_args.kwargs["body"]
        self.assertNotIn("flags", body)


class TestMiddlewarePostOnly(unittest.TestCase):
    """Test POST_ONLY enforcement in middleware."""

    @patch("bfxapi.rest._interface.middleware.requests.post")
    @patch("bfxapi.rest._interface.middleware.enforce_post_only")
    def test_middleware_order_submit_enforcement(self, mock_enforce, mock_post):
        """Test middleware enforces POST_ONLY for order/submit endpoint."""
        from bfxapi.rest._interface.middleware import Middleware

        mock_enforce.return_value = POST_ONLY
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_post.return_value = mock_response

        middleware = Middleware("https://api.bitfinex.com", "key", "secret")

        body = {
            "type": "LIMIT",
            "symbol": "tBTCUSD",
            "amount": 0.01,
            "price": 50000,
            "flags": 0,
        }
        middleware.post("auth/w/order/submit", body)

        # Verify enforce_post_only was called
        mock_enforce.assert_called_once_with(0)

    @patch("bfxapi.rest._interface.middleware.requests.post")
    @patch("bfxapi.rest._interface.middleware.enforce_post_only")
    def test_middleware_order_update_enforcement(self, mock_enforce, mock_post):
        """Test middleware enforces POST_ONLY for order/update endpoint always."""
        from bfxapi.rest._interface.middleware import Middleware

        mock_enforce.return_value = POST_ONLY
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_post.return_value = mock_response

        middleware = Middleware("https://api.bitfinex.com", "key", "secret")

        # Test with flags present
        body = {"id": 12345, "amount": 0.02, "flags": 64}
        middleware.post("auth/w/order/update", body)
        mock_enforce.assert_called_once_with(64)

        # Reset mocks
        mock_enforce.reset_mock()

        # Test without flags - should enforce
        body = {"id": 12345, "amount": 0.02}
        middleware.post("auth/w/order/update", body)
        mock_enforce.assert_called_once_with(None)

        # Verify flags field was added
        self.assertIn("flags", body)

    @patch("bfxapi.rest._interface.middleware.requests.post")
    @patch("bfxapi.rest._interface.middleware.enforce_post_only")
    def test_middleware_funding_offer_enforcement(self, mock_enforce, mock_post):
        """Test middleware does not enforce or send flags for funding/offer/submit."""
        from bfxapi.rest._interface.middleware import Middleware

        mock_enforce.return_value = POST_ONLY
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_post.return_value = mock_response

        middleware = Middleware("https://api.bitfinex.com", "key", "secret")

        body = {
            "type": "LIMIT",
            "symbol": "fUSD",
            "amount": 1000,
            "rate": 0.0001,
            "period": 2,
        }
        middleware.post("auth/w/funding/offer/submit", body)

        # Verify enforce_post_only was not called
        mock_enforce.assert_not_called()


class TestWebSocketPostOnly(unittest.IsolatedAsyncioTestCase):
    """Test POST_ONLY enforcement in WebSocket operations."""

    async def test_websocket_inputs_submit_order(self):
        """Test WebSocket inputs submit_order enforces POST_ONLY."""
        from bfxapi.websocket._client.bfx_websocket_inputs import BfxWebSocketInputs

        mock_handler = AsyncMock()
        inputs = BfxWebSocketInputs(mock_handler)

        with patch(
            "bfxapi.websocket._client.bfx_websocket_inputs.enforce_post_only"
        ) as mock_enforce:
            mock_enforce.return_value = POST_ONLY | 64

            await inputs.submit_order(
                type="LIMIT", symbol="tBTCUSD", amount=0.01, price=50000, flags=64
            )

            # Verify enforce_post_only was called
            mock_enforce.assert_called_once_with(64)

            # Verify handler was called with enforced flags
            call_args = mock_handler.call_args
            event = call_args[0][0]
            data = call_args[0][1]
            self.assertEqual(event, "on")
            self.assertIn("flags", data)

    async def test_websocket_inputs_update_order(self):
        """
        Test WS inputs update_order always enforces POST_ONLY and includes flags.
        """
        from bfxapi.websocket._client.bfx_websocket_inputs import BfxWebSocketInputs

        mock_handler = AsyncMock()
        inputs = BfxWebSocketInputs(mock_handler)

        with patch(
            "bfxapi.websocket._client.bfx_websocket_inputs.enforce_post_only"
        ) as mock_enforce:
            mock_enforce.return_value = POST_ONLY

            # Test with flags
            await inputs.update_order(id=12345, amount=0.02, flags=0)
            mock_enforce.assert_called_once_with(0)

            # Verify flags are in payload
            call_args = mock_handler.call_args
            data = call_args[0][1]
            self.assertIn("flags", data)

            # Reset mocks
            mock_enforce.reset_mock()
            mock_handler.reset_mock()

            # Test without flags - still enforced and included
            await inputs.update_order(id=12345, amount=0.02)
            mock_enforce.assert_called_once_with(None)

            call_args = mock_handler.call_args
            data = call_args[0][1]
            self.assertIn("flags", data)

    async def test_websocket_inputs_submit_funding_offer(self):
        """Test WebSocket inputs submit_funding_offer does not send flags."""
        from bfxapi.websocket._client.bfx_websocket_inputs import BfxWebSocketInputs

        mock_handler = AsyncMock()
        inputs = BfxWebSocketInputs(mock_handler)

        with patch(
            "bfxapi.websocket._client.bfx_websocket_inputs.enforce_post_only"
        ) as mock_enforce:
            mock_enforce.return_value = POST_ONLY

            await inputs.submit_funding_offer(
                type="LIMIT", symbol="fUSD", amount=1000, rate=0.0001, period=2
            )

            # Verify enforce_post_only not called
            mock_enforce.assert_not_called()

            # Verify handler called without flags
            call_args = mock_handler.call_args
            event = call_args[0][0]
            data = call_args[0][1]
            self.assertEqual(event, "fon")
            self.assertNotIn("flags", data)

    @patch("bfxapi.websocket._client.bfx_websocket_client.enforce_post_only")
    async def test_websocket_client_handle_input_enforcement(self, mock_enforce):
        """Test WebSocket client enforces POST_ONLY for orders only."""
        from bfxapi.websocket._client.bfx_websocket_client import BfxWebSocketClient

        mock_enforce.return_value = POST_ONLY

        # Create client with mocked websocket
        client = BfxWebSocketClient.__new__(BfxWebSocketClient)
        client._websocket = MagicMock()
        client._websocket.send = AsyncMock()
        # Simulate authenticated state to pass decorator checks
        client._authentication = True

        # Make __handle_websocket_input accessible
        handle_input = client._BfxWebSocketClient__handle_websocket_input

        # Test new order
        await handle_input(
            "on",
            {
                "type": "LIMIT",
                "symbol": "tBTCUSD",
                "amount": 0.01,
                "price": 50000,
            },
        )
        mock_enforce.assert_called_with(None)

        # Test order update with flags
        mock_enforce.reset_mock()
        await handle_input("ou", {"id": 12345, "flags": 64})
        mock_enforce.assert_called_with(64)

        # Test funding offer - should not enforce or touch flags
        mock_enforce.reset_mock()
        await handle_input("fon", {"type": "LIMIT", "symbol": "fUSD", "amount": 1000})
        mock_enforce.assert_not_called()


class TestIntegrationScenarios(unittest.TestCase):
    """Test complex integration scenarios."""

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


if __name__ == "__main__":
    unittest.main()
