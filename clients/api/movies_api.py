from custom_requester.custom_requester import CustomRequester


class MoviesApi(CustomRequester):
    MOVIES_ENDPOINT = "/movies"

    def get_movies(self, params=None, expected_status=200):
        """
        Получение списка фильмов с возможностью фильтрации.

        :param params: Query-параметры запроса.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="GET",
            endpoint=self.MOVIES_ENDPOINT,
            params=params,
            expected_status=expected_status,
        )

    def get_movie_by_id(self, movie_id, expected_status=200):
        """
        Получение фильма по идентификатору.

        :param movie_id: Идентификатор фильма.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="GET",
            endpoint=f"{self.MOVIES_ENDPOINT}/{movie_id}",
            expected_status=expected_status,
        )

    def create_movie(self, data, expected_status=201):
        """
        Создание нового фильма.

        :param data: Данные фильма.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=self.MOVIES_ENDPOINT,
            data=data,
            expected_status=expected_status,
        )

    def update_movie(self, movie_id, data, expected_status=200):
        """
        Обновление данных фильма.

        :param movie_id: Идентификатор фильма.
        :param data: Данные для обновления.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"{self.MOVIES_ENDPOINT}/{movie_id}",
            data=data,
            expected_status=expected_status,
        )

    def delete_movie(self, movie_id, expected_status=200):
        """
        Удаление фильма.

        :param movie_id: Идентификатор фильма.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"{self.MOVIES_ENDPOINT}/{movie_id}",
            expected_status=expected_status,
        )
