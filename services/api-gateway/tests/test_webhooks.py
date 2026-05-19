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

VALID_MEMBERSHIP_PAYLOAD = {
    "type": "organizationMembership.created",
    "data": {
        "role": "org:admin",
        "organization": {"id": "org_test123", "name": "Test Corp"},
        "public_user_data": {"user_id": "user_test456", "identifier": "user@testcorp.com"},
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

    def test_user_created_empty_email_addresses_returns_200(self, client):
        """user.created with empty email_addresses [] → 200, no crash (bug fix)."""
        test_client, mock_session = client
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        payload = {
            "type": "user.created",
            "data": {
                "id": "user_test123",
                "email_addresses": [],
                "organization_memberships": [],
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

class TestMembershipCreatedWebhook:

    def _setup_session(self, mock_session, tenant_found=True, user_exists=False):
        from common.models.tenant import Tenant
        from common.models.user import User

        tenant_result = MagicMock()
        if tenant_found:
            mock_tenant = MagicMock(spec=Tenant)
            mock_tenant.tenant_id = "org_test123"
            tenant_result.scalar_one_or_none.return_value = mock_tenant
        else:
            tenant_result.scalar_one_or_none.return_value = None

        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = (
            MagicMock(spec=User) if user_exists else None
        )

        call_count = 0

        async def side_effect(stmt):
            nonlocal call_count
            call_count += 1
            return tenant_result if call_count == 1 else user_result

        mock_session.execute = side_effect
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

    def test_membership_created_inserts_user(self, client):
        """organizationMembership.created happy path → user inserted."""
        test_client, mock_session = client
        self._setup_session(mock_session, tenant_found=True, user_exists=False)

        with patch("app.api.v1.endpoints.webhooks.Webhook") as mock_wh:
            mock_wh.return_value.verify.return_value = VALID_MEMBERSHIP_PAYLOAD
            response = test_client.post(
                "/api/v1/webhooks/clerk",
                content=json.dumps(VALID_MEMBERSHIP_PAYLOAD),
                headers=make_headers(),
            )

        assert response.status_code == 200
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_membership_created_tenant_not_found_skips(self, client):
        """organizationMembership.created, tenant missing → 200, no insert."""
        test_client, mock_session = client
        self._setup_session(mock_session, tenant_found=False)

        with patch("app.api.v1.endpoints.webhooks.Webhook") as mock_wh:
            mock_wh.return_value.verify.return_value = VALID_MEMBERSHIP_PAYLOAD
            response = test_client.post(
                "/api/v1/webhooks/clerk",
                content=json.dumps(VALID_MEMBERSHIP_PAYLOAD),
                headers=make_headers(),
            )

        assert response.status_code == 200
        mock_session.add.assert_not_called()

    def test_membership_created_duplicate_user_skips(self, client):
        """organizationMembership.created, user already exists → 200, no insert."""
        test_client, mock_session = client
        self._setup_session(mock_session, tenant_found=True, user_exists=True)

        with patch("app.api.v1.endpoints.webhooks.Webhook") as mock_wh:
            mock_wh.return_value.verify.return_value = VALID_MEMBERSHIP_PAYLOAD
            response = test_client.post(
                "/api/v1/webhooks/clerk",
                content=json.dumps(VALID_MEMBERSHIP_PAYLOAD),
                headers=make_headers(),
            )

        assert response.status_code == 200
        mock_session.add.assert_not_called()

    def test_membership_created_admin_role_stored(self, client):
        """org:admin → UserRole.ADMIN stored on user."""
        from common.models.user import UserRole
        test_client, mock_session = client
        self._setup_session(mock_session)

        added_user = None
        def capture(obj):
            nonlocal added_user
            added_user = obj
        mock_session.add = capture

        with patch("app.api.v1.endpoints.webhooks.Webhook") as mock_wh:
            mock_wh.return_value.verify.return_value = VALID_MEMBERSHIP_PAYLOAD
            test_client.post(
                "/api/v1/webhooks/clerk",
                content=json.dumps(VALID_MEMBERSHIP_PAYLOAD),
                headers=make_headers(),
            )

        assert added_user is not None
        assert added_user.role == UserRole.ADMIN

    def test_membership_created_member_role_stored(self, client):
        """org:member → UserRole.MEMBER stored on user."""
        from common.models.user import UserRole
        test_client, mock_session = client
        self._setup_session(mock_session)

        added_user = None
        def capture(obj):
            nonlocal added_user
            added_user = obj
        mock_session.add = capture

        payload = {
            "type": "organizationMembership.created",
            "data": {
                "role": "org:member",
                "organization": {"id": "org_test123", "name": "Test Corp"},
                "public_user_data": {"user_id": "user_test456", "identifier": "user@testcorp.com"},
            }
        }

        with patch("app.api.v1.endpoints.webhooks.Webhook") as mock_wh:
            mock_wh.return_value.verify.return_value = payload
            test_client.post(
                "/api/v1/webhooks/clerk",
                content=json.dumps(payload),
                headers=make_headers(),
            )

        assert added_user is not None
        assert added_user.role == UserRole.MEMBER

    def test_membership_created_missing_organization_key_skips(self, client):
        """No 'organization' key in payload → 200, no crash."""
        test_client, mock_session = client
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        payload = {
            "type": "organizationMembership.created",
            "data": {
                "role": "org:admin",
                "public_user_data": {"user_id": "user_test456", "identifier": "user@test.com"},
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

    def test_membership_created_missing_user_data_key_skips(self, client):
        """No 'public_user_data' key in payload → 200, no crash."""
        test_client, mock_session = client
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        payload = {
            "type": "organizationMembership.created",
            "data": {
                "role": "org:admin",
                "organization": {"id": "org_test123", "name": "Test Corp"},
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

    def test_membership_created_empty_org_id_skips(self, client):
        """Empty org_id in payload → 200, no insert."""
        test_client, mock_session = client
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        payload = {
            "type": "organizationMembership.created",
            "data": {
                "role": "org:admin",
                "organization": {"id": "", "name": "Test Corp"},
                "public_user_data": {"user_id": "user_test456", "identifier": "user@test.com"},
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

    def test_membership_created_empty_user_id_skips(self, client):
        """Empty user_id in payload → 200, no insert."""
        test_client, mock_session = client
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        payload = {
            "type": "organizationMembership.created",
            "data": {
                "role": "org:admin",
                "organization": {"id": "org_test123", "name": "Test Corp"},
                "public_user_data": {"user_id": "", "identifier": "user@test.com"},
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