import pytest

from clients.api.api_manager import ApiManager
from conftest import test_user
from models.base_models import RegisterUserResponse


class TestAuthAPI:
    @pytest.mark.slow
    def test_register_user(self, api_manager: ApiManager, test_user):
        response = api_manager.auth_api.register_user(user_data=test_user)

        register_user_response = RegisterUserResponse(**response.json())

        assert register_user_response.email == test_user.email, "Email не совпадает"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        """Тест на регистрацию и авторизацию пользователя"""
        login_data = {
            "email": registered_user.email,
            "password": registered_user.password,
        }

        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        # Проверки
        assert "accessToken" in response_data, (
            "Токен доступа отсутствует в ответе"
        )
        assert response_data["user"]["email"] == registered_user.email, "Email не совпадает"

    def test_register_with_existing_email_returns_conflict(self, api_manager: ApiManager, test_user):
        """Попытка регистрации с существующим email"""

        payload = test_user

        api_manager.auth_api.register_user(payload)

        response = api_manager.auth_api.register_user(payload, expected_status=409)
        data = response.json()

        assert "message" in data, "Сообщения об ошибке отсутствует"

    def test_register_with_short_password(self, api_manager: ApiManager, test_user):
        """Попытка регистрации с паролем длиной менее 8 символов"""
        payload = test_user.model_copy()
        payload.password = "Short1"
        payload.passwordRepeat = "Short1"

        response = api_manager.auth_api.register_user(payload, expected_status=400)
        data = response.json()

        assert "message" in data, "Сообщение об ошибке отсутствуют"

    def test_login_with_invalid_credentials(self, api_manager: ApiManager, test_user):
        """Проверка ошибки авторизации при неверном логине или пароле"""
        payload = {
            "email": test_user.email,
            "password": "WrongPassword123",
        }

        response = api_manager.auth_api.login_user(payload, expected_status=401)
        data = response.json()
        assert "message" in data, "Сообщение об ошибке отсутствует"

    def test_create_user_success(
            self, api_manager: ApiManager, admin_session, test_user
    ):
        """Успешное создание пользователя администратором"""
        api_manager.user_api.session = admin_session

        payload = test_user.model_copy()
        payload.verified = True
        payload.banned = False

        response = api_manager.user_api.create_user(payload)
        data = response.json()

        assert response.status_code == 201, (
            "Ожидался статус 201 при создании пользователя"
        )
        assert data["email"] == payload.email
        assert data["fullName"] == payload.fullName
        assert data["verified"] is True
        assert data.get("banned", False) is False
        assert "id" in data
        assert "roles" in data

    def test_create_user_with_existing_email_returns_conflict(
            self, api_manager: ApiManager, admin_session, test_user
    ):
        """Попытка создания пользователя с существующим email"""
        api_manager.user_api.session = admin_session

        payload = test_user.model_copy()
        payload.verified = True
        payload.banned = False

        # Первая попытка
        first_response = api_manager.user_api.create_user(payload)
        assert first_response.status_code == 201, "Первая регистрация должна быть успешной"

        # Повторная попытка
        second_response = api_manager.user_api.create_user(
            payload, expected_status=409
        )
        data = second_response.json()
        assert "message" in data, "Ответ должен содержать сообщение об ошибке"

    def test_update_user_status(
            self, api_manager: ApiManager, admin_session, created_user_id
    ):
        """Успешное обновление статусов verified и banned пользователю"""
        api_manager.user_api.session = admin_session

        payload = {
            "verified": True,
            "banned": True,
            "roles": ["USER"],
        }

        response = api_manager.user_api.update_user(created_user_id, payload)
        data = response.json()

        assert response.status_code == 200, "Статусы пользователя не обновлены"
        assert data["verified"] is True
        assert data["banned"] is True

    def test_update_user_roles_success(
            self, api_manager: ApiManager, admin_session, created_user_id
    ):
        """Успешное изменение ролей пользователя"""
        api_manager.user_api.session = admin_session

        payload = {
            "verified": True,
            "banned": False,
            "roles": ["USER", "ADMIN"],
        }

        response = api_manager.user_api.update_user(created_user_id, payload)
        data = response.json()

        assert response.status_code == 200, "Роли пользователя не обновлены"
        assert "ADMIN" in data["roles"], "Роль ADMIN отсутствует"
        assert "USER" in data["roles"], "Роль USER отсутствует"

    def test_update_user_roles_invalid(
            self, api_manager: ApiManager, admin_session, created_user_id
    ):
        """Ошибка при передаче некорректных ролей"""
        api_manager.user_api.session = admin_session

        payload = {
            "verified": True,
            "banned": False,
            "roles": ["INVALID"],
        }

        response = api_manager.user_api.update_user(
            created_user_id, payload, expected_status=400
        )
        data = response.json()
        assert "message" in data, "Ответ должен содержать сообщение об ошибке"
