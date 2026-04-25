import json
from unittest.mock import patch, MagicMock, AsyncMock


VALID_ORG_PAYLOAD = {
    "type": "organization.created",
    "data": {
        "id": "org_test123",
        "name": "Test Corp",
        "slug": "test-corp",
    }
}

VALID_USER_PAYLOAD = {
    "type": "user.created",
    "data": {
        "id": "user_test123",
        "email_addresses": [{"email_address": "user@testcorp.com"}],
        "organization_memberships": [
            {
                "organization": {
                    "id": "org_test123",
                    "slug": "test-corp"
                }
            }
        ]
    }
}


def make_headers():
    return {
        "svix-id": "msg_test123",
        "svix-timestamp": "1234567890",
        "svix-signature": "v1,test_signature",
    }


class TestClerkWebhook:

    def test_invalid_signature_returns_400(self, client):
        """Bad signature → 400, nothing written to DB."""
        test_client, _ = client

        with patch("app.api.v1.endpoints.webhooks.Webhook") as mock_wh:
            from svix.webhooks import WebhookVerificationError
            mock_wh.return_value.verify.side_effect = WebhookVerificationError()

            response = test_client.post(
                "/api/v1/webhooks/clerk",
                content=json.dumps(VALID_ORG_PAYLOAD),
                headers=make_headers(),
            )

        assert response.status_code == 400
        assert "signature" in response.json()["detail"].lower()

    def test_org_created_inserts_tenant(self, client):
        """organization.created → tenant inserted."""
        test_client, mock_session = client

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # no duplicate
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        with patch("app.api.v1.endpoints.webhooks.Webhook") as mock_wh:
            mock_wh.return_value.verify.return_value = VALID_ORG_PAYLOAD

            response = test_client.post(
                "/api/v1/webhooks/clerk",
                content=json.dumps(VALID_ORG_PAYLOAD),
                headers=make_headers(),
            )

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_org_created_duplicate_skips_silently(self, client):
        """organization.created duplicate → 200, no insert."""
        test_client, mock_session = client

        from common.models.tenant import Tenant
        existing_tenant = MagicMock(spec=Tenant)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_tenant
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        with patch("app.api.v1.endpoints.webhooks.Webhook") as mock_wh:
            mock_wh.return_value.verify.return_value = VALID_ORG_PAYLOAD

            response = test_client.post(
                "/api/v1/webhooks/clerk",
                content=json.dumps(VALID_ORG_PAYLOAD),
                headers=make_headers(),
            )

        assert response.status_code == 200
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()

    def test_user_created_no_org_skips_gracefully(self, client):
        """user.created with no org membership → 200, no insert."""
        test_client, mock_session = client

        payload = {
            "type": "user.created",
            "data": {
                "id": "user_test123",
                "email_addresses": [{"email_address": "user@test.com"}],
                "organization_memberships": []  # no org
            }
        }

        with patch("app.api.v1.endpoints.webhooks.Webhook") as mock_wh:
            mock_wh.return_value.verify.return_value = payload

            response = test_client.post(
                "/api/v1/webhooks/clerk",
                content=json.dumps(payload),
                headers=make_headers(),
            )

        assert response.status_code == 200
        mock_session.add.assert_not_called()

    def test_unknown_event_type_returns_200(self, client):
        """Unknown event type → 200, silently ignored."""
        test_client, _ = client

        payload = {"type": "user.deleted", "data": {}}

        with patch("app.api.v1.endpoints.webhooks.Webhook") as mock_wh:
            mock_wh.return_value.verify.return_value = payload

            response = test_client.post(
                "/api/v1/webhooks/clerk",
                content=json.dumps(payload),
                headers=make_headers(),
            )

        assert response.status_code == 200