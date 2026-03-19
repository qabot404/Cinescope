def test_edit_movie_by_valid_id_returns(admin_user, existing_movie_id):
    """Редактирование фильма по валидному id"""
    payload = {"price": 600}

    response = admin_user.movies_api.update_movie(
        movie_id=existing_movie_id,
        data=payload,
        expected_status=200,
    )

    data = response.json()
    assert data["id"] == existing_movie_id
    assert data["price"] == payload["price"]


def test_edit_movie_by_non_existent_id_returns(admin_user):
    """Попытка редактирования фильма по несуществующему id"""
    non_existent = 99999
    payload = {"price": 900}

    response = admin_user.movies_api.update_movie(
        movie_id=non_existent,
        data=payload,
        expected_status=404,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"


def test_edit_movie_with_negative_id_returns(admin_user):
    """Попытка редактирования фильма с отрицательным id"""
    negative_id = -1
    payload = {"price": 1000}

    response = admin_user.movies_api.update_movie(
        movie_id=negative_id,
        data=payload,
        expected_status=404,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"
