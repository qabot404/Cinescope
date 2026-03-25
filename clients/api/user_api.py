from custom_requester.custom_requester import CustomRequester


class UserAPI(CustomRequester):
    """
    Класс для работы с API пользователей.
    """

    def __init__(self, session, base_url):
        super().__init__(session=session, base_url=base_url)

    def create_user(self, payload, expected_status=201):
        """
        Создание пользователя.

        :param payload: Данные пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint="/user",
            data=payload,
            expected_status=expected_status,
        )

    def update_user(self, user_id, payload, expected_status=200):
        """
        Обновление пользователя.

        :param user_id: ID пользователя.
        :param payload: Данные для обновления.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"/user/{user_id}",
            data=payload,
            expected_status=expected_status,
        )

    def get_user_info(self, user_id, expected_status=200):
        """
        Получение информации о пользователе.

        :param user_id: ID пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="GET",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status,
        )

    def delete_user(self, user_id, expected_status=204):
        """
        Удаление пользователя.

        :param user_id: ID пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status,
        )
