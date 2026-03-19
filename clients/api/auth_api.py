from constants import LOGIN_ENDPOINT, REGISTER_ENDPOINT
from custom_requester.custom_requester import CustomRequester


class AuthAPI(CustomRequester):
    """
    Класс для работы с аутентификацией.
    """

    def __init__(self, session, base_url):
        super().__init__(session=session, base_url=base_url)

    def register_user(self, user_data, expected_status=201):
        """
        Регистрация нового пользователя.

        :param user_data: Данные пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=user_data,
            expected_status=expected_status,
        )

    def login_user(self, login_data, expected_status=200):
        """
        Авторизация пользователя.

        :param login_data: Данные для логина.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=expected_status,
        )

    def authenticate(self, user_creds):
        """
        Авторизация пользователя с обновлением заголовков сессии токеном доступа.

        :param user_creds: Кортеж с email и паролем пользователя.
        """
        login_data = {"email": user_creds[0], "password": user_creds[1]}

        response = self.login_user(login_data).json()
        if "accessToken" not in response:
            raise KeyError("Token is missing")

        token = response["accessToken"]
        self._update_session_headers(
            **{"authorization": f"Bearer {token}"}
        )

    def delete_user(self, user_id, expected_status=204):
        """Удаление пользователя."""
        return self.send_request(
            method="DELETE",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status,
        )
