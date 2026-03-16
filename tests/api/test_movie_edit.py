from conftest import existing_movie_id
from constants import MOVIES_ENDPOINT


def test_edit_movie_by_valid_id_returns(api_requester, existing_movie_id):
    """Редактирование фильма по валидному id"""
    payload = {"price": 600}

    response = api_requester.send_request(
        method="PATCH",
        endpoint=f"{MOVIES_ENDPOINT}/{existing_movie_id}",
        data=payload,
        expected_status=200,
    )

    data = response.json()
    assert data["id"] == existing_movie_id
    assert data["price"] == payload["price"]


def test_edit_movie_by_existent_id_returns(api_requester):
    """Попытка редактирования фильма по несуществующему id"""
    non_existent = 99999
    payload = {"price": 900}

    response = api_requester.send_request(
        method="PATCH",
        endpoint=f"{MOVIES_ENDPOINT}/{non_existent}",
        data=payload,
        expected_status=404,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"


def test_edit_movie_with_negative_id_returns(api_requester):
    """Попытка редактирования фильма с отрицательным id"""
    negative_id = -1
    payload = {"price": 1000}

    response = api_requester.send_request(
        method="PATCH",
        endpoint=f"{MOVIES_ENDPOINT}/{negative_id}",
        data=payload,
        expected_status=404,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"
