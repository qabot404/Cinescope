from models.base_models import TestUser


class TestUserAPI:

    def test_create_user(self, created_user, creation_user_data):
        user = created_user

        assert user.id is not None and user.id != ""
        assert user.email == creation_user_data["email"]
        assert user.fullName == creation_user_data["fullName"]
        assert [role.value for role in user.roles] == creation_user_data["roles"]
        assert user.verified is True

    def test_get_user_by_locator(self, super_admin, created_user, creation_user_data):
        response_by_id = TestUser(
            **super_admin.api.user_api.get_user(created_user.id).json()
        )
        response_by_email = TestUser(
            **super_admin.api.user_api.get_user(created_user.email).json()
        )

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"
        assert response_by_id.id is not None and response_by_id.id != "", "ID должен быть не пустым"
        assert response_by_id.email == creation_user_data["email"]
        assert response_by_id.fullName == creation_user_data["fullName"]
        assert [role.value for role in response_by_id.roles] == creation_user_data["roles"]
        assert response_by_id.verified is True

    def test_get_user_by_id_common_user(self, common_user):
        common_user.api.user_api.get_user(common_user.email, expected_status=403)
