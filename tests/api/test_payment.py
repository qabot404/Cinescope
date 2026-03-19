from constants import PAYMENT_BASE_URL
import requests
import pytest
from custom_requester.custom_requester import CustomRequester


def test_create_payment_success(payment_requester, payment_payload):
    """Успешное создание платежа с корректными данными"""
    response = payment_requester.send_request(
        method="POST",
        endpoint="/create",
        data=payment_payload,
        expected_status=201,
    )

    data = response.json()
    assert data.get("status") == "SUCCESS", "Некорректный статус платежа"


def test_create_payment_invalid_card(payment_requester, payment_payload_with_invalid_card_number):
    """Ошибка при неверном номере карты"""
    response = payment_requester.send_request(
        method="POST",
        endpoint="/create",
        data=payment_payload_with_invalid_card_number,
        expected_status=400,
    )

    data = response.json()
    assert data["error"]["status"] == "INVALID_CARD"


def test_create_payment_unauthorized(payment_payload):
    """Попытка создания платежа без авторизации"""
    unauthorized_requester = CustomRequester(requests.Session(), PAYMENT_BASE_URL)
    unauthorized_requester.send_request(
        method="POST",
        endpoint="/create",
        data=payment_payload,
        expected_status=401,
    )


def test_create_payment_non_existing_movie(payment_requester, card_data):
    """Попытка оплаты несуществующего фильма"""
    payload = {
        "movieId": 999999999,
        "amount": 1,
        "card": card_data,
    }

    payment_requester.send_request(
        method="POST",
        endpoint="/create",
        data=payload,
        expected_status=404,
    )


@pytest.mark.xfail(reason="Ожидается 500 Internal Server Error")
def test_create_payment_server_error(payment_requester, payment_payload):
    """Ошибка сервера"""
    payment_requester.send_request(
        method="POST",
        endpoint="/create",
        data=payment_payload,
        expected_status=500,
    )


def test_get_user_payments_success(payment_requester):
    """Успешное получение списка платежей текущего пользователя"""
    response = payment_requester.send_request(
        method="GET",
        endpoint="/user",
        expected_status=200,
    )

    data = response.json()
    assert isinstance(data, list)


def test_get_user_payments_without_auth():
    """Ошибка доступа без авторизации"""
    unauthorized_requester = CustomRequester(requests.Session(), PAYMENT_BASE_URL)
    unauthorized_requester.send_request(
        method="GET",
        endpoint="/user",
        expected_status=401,
    )


def test_get_user_payments_by_user_id_success(admin_payment_requester):
    """Успешное получение платежей пользователя"""
    response = admin_payment_requester.send_request(
        method="GET",
        endpoint="/user",
        expected_status=200,
    )

    payments = response.json()
    assert len(payments) > 0

    user_id = payments[0]["userId"]
    response_user = admin_payment_requester.send_request(
        method="GET",
        endpoint=f"/user/{user_id}",
        expected_status=200,
    )

    user_payments = response_user.json()
    assert isinstance(user_payments, list)


def test_get_user_payments_by_user_id_not_found(admin_payment_requester):
    """Ошибка при передаче некорректного userId"""
    invalid_user_id = "00000000-0000-0000-0000-000000000000"
    admin_payment_requester.send_request(
        method="GET",
        endpoint=f"/user/{invalid_user_id}",
        expected_status=404,
    )


def test_get_user_payments_by_user_id_without_auth(payment_requester):
    """Ошибка недостатка прав доступа"""
    user_id = "8cbabbe9-5fff-4dbe-a77e-104bf4e63dbe"
    payment_requester.send_request(
        method="GET",
        endpoint=f"/user/{user_id}",
        expected_status=403,
    )


def test_get_all_payments_success(admin_payment_requester):
    """Успешное получение списка платежей"""
    response = admin_payment_requester.send_request(
        method="GET",
        endpoint="/find-all",
        expected_status=200,
    )

    data = response.json()
    assert "payments" in data, "В ответе отсутствует список платежей"
    assert isinstance(data["payments"], list)


def test_get_all_payments_filter_by_status(admin_payment_requester):
    """Фильтрация платежей по статусу"""
    response = admin_payment_requester.send_request(
        method="GET",
        endpoint="/find-all?status=SUCCESS",
        expected_status=200,
    )

    data = response.json()
    for payment in data["payments"]:
        assert payment["status"] == "SUCCESS"


def test_get_all_payments_sort_by_created_at(admin_payment_requester):
    """Проверка сортировки по дате создания"""
    response = admin_payment_requester.send_request(
        method="GET",
        endpoint="/find-all?created=desc",
        expected_status=200,
    )

    payments = response.json()["payments"]
    if len(payments) > 1:
        assert payments[0]["createdAt"] >= payments[1]["createdAt"]


def test_get_all_payments_invalid_params(admin_payment_requester):
    """Ошибка с некорректными параметрами фильтрации"""
    admin_payment_requester.send_request(
        method="GET",
        endpoint="/find-all?page=-1",
        expected_status=400,
    )
