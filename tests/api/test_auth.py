from clients.api.api_manager import ApiManager
from utils.data_generator import DataGenerator


class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, test_user):
        """Тест на регистрацию пользователя"""
        response = api_manager.auth_api.register_user(test_user)
        data = response.json()

        # Проверки
        assert data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in data, "ID пользователя отсутствует в ответе"
        assert "roles" in data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in data["roles"], "Роль 'USER' должна быть у пользователя"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        """Тест на регистрацию и авторизацию пользователя"""
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"],
        }

        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        # Проверки
        assert "accessToken" in response_data, (
            "Токен доступа отсутствует в ответе"
        )
        assert response_data["user"]["email"] == registered_user["email"], (
            "Email не совпадает"
        )

    def test_register_with_existing_email_returns_conflict(self, api_manager: ApiManager):
        """Попытка регистрации с существующим email"""
        password = DataGenerator.generate_random_password()
        payload = {
            "email": DataGenerator.generate_random_email(),
            "fullName": DataGenerator.generate_random_name(),
            "password": password,
            "passwordRepeat": password,
        }

        # Первая регистрация
        api_manager.auth_api.register_user(payload)

        # Повторная регистрация
        response = api_manager.auth_api.register_user(payload, expected_status=409)
        data = response.json()
        assert "message" in data, "Сообщение об ошибке отсутствует"

    def test_register_with_short_password(self, api_manager: ApiManager):
        """Попытка регистрации с паролем длиной менее 8 символов"""
        payload = {
            "email": DataGenerator.generate_random_email(),
            "fullName": DataGenerator.generate_random_name(),
            "password": "Short1",
            "passwordRepeat": "Short1",
        }

        response = api_manager.auth_api.register_user(payload, expected_status=400)
        data = response.json()
        assert "message" in data, "Сообщение об ошибке отсутствует"

    def test_login_with_invalid_credentials(self, api_manager: ApiManager):
        """Проверка ошибки авторизации при неверном логине или пароле"""
        payload = {
            "email": DataGenerator.generate_random_email(),
            "password": "WrongPassword123",
        }

        response = api_manager.auth_api.login_user(payload, expected_status=401)
        data = response.json()
        assert "message" in data, "Сообщение об ошибке отсутствует"

    def test_create_user_success(
            self, api_manager: ApiManager, admin_session
    ):
        """Успешное создание пользователя администратором"""
        api_manager.user_api.session = admin_session

        payload = {
            "email": DataGenerator.generate_random_email(),
            "fullName": DataGenerator.generate_random_name(),
            "password": DataGenerator.generate_random_password(),
            "verified": True,
            "banned": False,
        }

        response = api_manager.user_api.create_user(payload)
        data = response.json()

        assert response.status_code == 201, (
            "Ожидался статус 201 при создании пользователя"
        )
        assert data["email"] == payload["email"]
        assert data["fullName"] == payload["fullName"]
        assert data["verified"] is True
        assert data.get("banned", False) is False
        assert "id" in data
        assert "roles" in data

    def test_create_user_with_existing_email_returns_conflict(
            self, api_manager: ApiManager, admin_session
    ):
        """Попытка создания пользователя с существующим email"""
        api_manager.user_api.session = admin_session
        email = DataGenerator.generate_random_email()

        payload = {
            "email": email,
            "fullName": DataGenerator.generate_random_name(),
            "password": DataGenerator.generate_random_password(),
            "verified": True,
            "banned": False,
        }

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
