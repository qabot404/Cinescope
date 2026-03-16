from constants import MOVIES_ENDPOINT


def test_get_movies_public_returns_movies_list(api_requester):
    """Проверка получения списка фильмов"""
    response = api_requester.send_request(
        method="GET",
        endpoint=MOVIES_ENDPOINT,
        expected_status=200,
    )

    data = response.json()
    assert "movies" in data
    assert isinstance(data["movies"], list)


def test_get_movies_response_has_pagination_fields(api_requester):
    """Ответ содержит обязательные поля пагинации"""
    response = api_requester.send_request(
        method="GET",
        endpoint=MOVIES_ENDPOINT,
        expected_status=200,
    )

    data = response.json()
    assert "count" in data
    assert "page" in data
    assert "pageSize" in data
    assert "pageCount" in data


def test_get_movies_items_have_required_fields(api_requester):
    """Фильмы в списке содержат обязательные поля"""
    response = api_requester.send_request(
        method="GET",
        endpoint=MOVIES_ENDPOINT,
        expected_status=200,
    )

    movies = response.json()["movies"]
    if movies:
        movie = movies[0]
        assert "id" in movie
        assert "name" in movie
        assert "price" in movie
        assert "published" in movie


def test_get_movies_with_invalid_query_param_returns(api_requester):
    """Некорректный query-параметр приводит к ошибке валидации"""
    response = api_requester.send_request(
        method="GET",
        endpoint=f"{MOVIES_ENDPOINT}?page=invalid",
        expected_status=400,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"


def test_get_movies_wrong_endpoint_returns(api_requester):
    """Запрос к несуществующему endpoint возвращает 404"""
    response = api_requester.send_request(
        method="GET",
        endpoint="/movie",
        expected_status=404,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"
