def test_get_movies_public_returns_movies_list(api_manager):
    """Проверка получения списка фильмов"""
    response = api_manager.movies_api.get_movies()

    data = response.json()
    assert "movies" in data
    assert isinstance(data["movies"], list)


def test_get_movies_with_filters(api_manager):
    """Проверка, что API возвращает фильмы, соответствующие заданным фильтрам по цене и статусу публикации"""
    params = {
        "minPrice": 5,
        "maxPrice": 20,
        "published": True,
    }

    response = api_manager.movies_api.get_movies(params=params)

    data = response.json()
    movies = data["movies"]

    assert movies, "Список отфильтрованных фильмов пуст"

    for movie in movies:
        assert 5 <= movie["price"] <= 20
        assert movie["published"] is True


def test_get_movies_response_has_pagination_fields(api_manager):
    """Ответ содержит обязательные поля пагинации"""
    response = api_manager.movies_api.get_movies()

    data = response.json()
    assert "count" in data
    assert "page" in data
    assert "pageSize" in data
    assert "pageCount" in data


def test_get_movies_items_have_required_fields(api_manager):
    """Фильмы в списке содержат обязательные поля"""
    response = api_manager.movies_api.get_movies()

    movies = response.json()["movies"]
    if movies:
        movie = movies[0]
        assert "id" in movie
        assert "name" in movie
        assert "price" in movie
        assert "published" in movie


def test_get_movies_with_invalid_query_param_returns(api_manager):
    """Некорректный query-параметр приводит к ошибке валидации"""
    response = api_manager.movies_api.get_movies(
        params={"page": "invalid"},
        expected_status=400,
    )

    assert response.status_code == 400


def test_get_movies_wrong_endpoint_returns(api_requester):
    """Запрос к несуществующему endpoint возвращает 404"""
    response = api_requester.send_request(
        method="GET",
        endpoint="/movie",
        expected_status=404,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"
