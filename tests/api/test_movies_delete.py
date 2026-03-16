from constants import MOVIES_ENDPOINT


def test_delete_movie_by_valid_id_returns(api_requester):
    """Удаление фильма по валидному id"""
    # Получаем список фильмов
    list_response = api_requester.send_request(
        method="GET",
        endpoint=MOVIES_ENDPOINT,
        expected_status=200,
    )

    movies = list_response.json()["movies"]
    assert len(movies) > 0, "Список фильмов пуст"

    movie_id = movies[0]["id"]

    # Удаляем фильм
    response = api_requester.send_request(
        method="DELETE",
        endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
        expected_status=200,
    )

    data = response.json()
    assert "id" in data


def test_delete_movie_by_non_existent_id_returns(api_requester):
    """Попытка удаления фильма по несуществующему id"""
    non_existent_id = 99999

    response = api_requester.send_request(
        method="DELETE",
        endpoint=f"{MOVIES_ENDPOINT}/{non_existent_id}",
        expected_status=404,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"


def test_delete_movie_with_negative_id_returns(api_requester):
    """Попытка удаления фильма с отрицательным id"""
    negative_id = -1

    response = api_requester.send_request(
        method="DELETE",
        endpoint=f"{MOVIES_ENDPOINT}/{negative_id}",
        expected_status=404,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"
