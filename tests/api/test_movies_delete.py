def test_delete_movie_by_valid_id_returns(admin_user, movie_for_delete):
    """Проверка успешного удаления фильма по валидному идентификатору"""
    response = admin_user.movies_api.delete_movie(movie_for_delete)

    assert response.status_code == 200, "Фильм не был успешно удалён"


def test_delete_movie_by_non_existent_id_returns(admin_user):
    """Попытка удаления фильма по несуществующему id"""
    non_existent_id = 99999

    response = admin_user.movies_api.delete_movie(
        non_existent_id,
        expected_status=404,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"


def test_delete_movie_with_negative_id_returns(admin_user):
    """Попытка удаления фильма с отрицательным id"""
    negative_id = -1

    response = admin_user.movies_api.delete_movie(
        negative_id,
        expected_status=404,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"
