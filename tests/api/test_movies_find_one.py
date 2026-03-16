from constants import MOVIES_ENDPOINT


def test_get_movie_by_valid_id_returns(api_requester):
    """Получение фильма по валидному id"""
    # Получаем список фильмов, чтобы взять существующий id
    list_response = api_requester.send_request(
        method="GET",
        endpoint=MOVIES_ENDPOINT,
        expected_status=200,
    )

    movies = list_response.json()["movies"]
    assert len(movies) > 0, "Список фильмов пуст"

    movie_id = movies[0]["id"]

    # Получаем фильм по id
    response = api_requester.send_request(
        method="GET",
        endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
        expected_status=200,
    )

    data = response.json()
    assert data["id"] == movie_id
    assert "name" in data
    assert "price" in data
    assert "location" in data


def test_get_movie_by_non_existent_id_returns(api_requester):
    """Попытка получения фильма по несуществующему id"""
    non_existent_id = 99999

    response = api_requester.send_request(
        method="GET",
        endpoint=f"{MOVIES_ENDPOINT}/{non_existent_id}",
        expected_status=404,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"


def test_get_movie_with_negative_id_returns(api_requester):
    """Попытка получения фильма с отрицательным id"""
    negative_id = -1

    response = api_requester.send_request(
        method="GET",
        endpoint=f"{MOVIES_ENDPOINT}/{negative_id}",
        expected_status=404,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"
