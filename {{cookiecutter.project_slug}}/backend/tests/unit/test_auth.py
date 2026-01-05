"""
Unit tests for authentication with Clerk.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.security.clerk_auth import ClerkAuthProvider, ClerkUser
from app.config import Settings


class TestClerkAuth:
    """Test Clerk authentication."""

    @pytest.fixture
    def test_settings(self):
        """Test settings."""
        return Settings(
            clerk_secret_key="sk_test_test",
            clerk_publishable_key="pk_test_test"
        )

    @pytest.fixture
    def clerk_provider(self, test_settings):
        """Clerk auth provider."""
        return ClerkAuthProvider(test_settings)

    def test_clerk_user_creation(self):
        """Test ClerkUser creation."""
        user_data = {
            "sub": "user_123",
            "email": "test@example.com",
            "username": "testuser",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://example.com/pic.jpg",
            "public_metadata": {"role": "user"}
        }

        user = ClerkUser(user_data)

        assert user.id == "user_123"
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.full_name == "Test User"

    @pytest.mark.asyncio
    async def test_get_jwks(self, clerk_provider):
        """Test getting JWKS from Clerk."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {"keys": []}
            mock_response.raise_for_status = MagicMock()
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            jwks = await clerk_provider.get_jwks()

            assert "keys" in jwks
