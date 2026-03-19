def test_get_movie_by_valid_id_returns(api_manager, existing_movie_id):
    """Получение фильма по валидному id"""
    response = api_manager.movies_api.get_movie_by_id(existing_movie_id)

    data = response.json()
    assert data["id"] == existing_movie_id
    assert "name" in data
    assert "price" in data
    assert "location" in data


def test_get_movie_by_non_existent_id_returns(api_manager):
    """Попытка получения фильма по несуществующему id"""
    non_existent_id = 99999

    response = api_manager.movies_api.get_movie_by_id(
        non_existent_id,
        expected_status=404
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"


def test_get_movie_with_negative_id_returns(api_manager):
    """Попытка получения фильма с отрицательным id"""
    negative_id = -1

    response = api_manager.movies_api.get_movie_by_id(
        negative_id,
        expected_status=404
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"
