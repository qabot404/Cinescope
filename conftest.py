import random
import uuid

import pytest
import requests

from clients.api.api_manager import ApiManager
from constants import (
    API_BASE_URL,
    BASE_URL,
    HEADERS,
    LOGIN_ENDPOINT,
    MOVIES_ENDPOINT,
    PAYMENT_BASE_URL,
    REGISTER_ENDPOINT,
)
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator


@pytest.fixture
def test_user():
    """Генерация случайного пользователя для тестов"""
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"],
    }


@pytest.fixture(scope="session")
def session():
    """Фикстура для создания HTTP-сессии"""
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    """Фикстура возвращает экземпляр ApiManager"""
    return ApiManager(session)


@pytest.fixture(scope="session")
def admin_session():
    """Создание авторизованной сессии администратора"""
    login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
    admin_credentials = {
        "email": "api1@gmail.com",
        "password": "asdqwe123Q",
    }

    response = requests.post(
        login_url,
        json=admin_credentials,
        headers=HEADERS,
    )
    assert response.status_code in (200, 201), "Ошибка авторизации администратора"

    token = response.json().get("accessToken")
    assert token is not None, "Токен доступа отсутствует в ответе"

    admin_http_session = requests.Session()
    admin_http_session.headers.update(HEADERS)
    admin_http_session.headers.update({"Authorization": f"Bearer {token}"})
    return admin_http_session


@pytest.fixture
def admin_user(api_manager):
    """Создание авторизованного ApiManager для администратора"""
    admin_credentials = ("api1@gmail.com", "asdqwe123Q")
    api_manager.auth_api.authenticate(admin_credentials)
    return api_manager


@pytest.fixture
def registered_user(api_manager, test_user):
    """Фикстура для регистрации и получения данных зарегистрированного пользователя"""
    response = api_manager.auth_api.register_user(test_user)
    response_data = response.json()

    user_data = test_user.copy()
    user_data["id"] = response_data["id"]
    return user_data


@pytest.fixture
def auth_session(test_user):
    """Создание авторизованной сессии для обычного пользователя"""
    register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"
    response = requests.post(register_url, json=test_user, headers=HEADERS)
    assert response.status_code == 201, "Ошибка регистрации пользователя"

    login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"],
    }
    response = requests.post(login_url, json=login_data, headers=HEADERS)
    assert response.status_code in (200, 201), "Ошибка авторизации"

    token = response.json().get("accessToken")
    assert token is not None, "Токен доступа отсутствует в ответе"

    user_http_session = requests.Session()
    user_http_session.headers.update(HEADERS)
    user_http_session.headers.update({"Authorization": f"Bearer {token}"})
    return user_http_session


@pytest.fixture
def api_requester(admin_session):
    """Фикстура для отправки запросов к API с авторизацией администратора"""
    return CustomRequester(admin_session, API_BASE_URL)


@pytest.fixture
def payment_requester(auth_session):
    """Фикстура для отправки запросов к API платежей"""
    return CustomRequester(auth_session, PAYMENT_BASE_URL)


@pytest.fixture
def admin_payment_requester(admin_session):
    """Фикстура для отправки запросов к API платежей от администратора"""
    return CustomRequester(admin_session, PAYMENT_BASE_URL)


@pytest.fixture
def created_movie(admin_user):
    """Фикстура для создания тестового фильма с последующим удалением после выполнения теста"""
    data = {
        "name": f"Test Movie {uuid.uuid4()}",
        "description": "Test Description",
        "price": 10,
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    response = admin_user.movies_api.create_movie(data)
    movie_id = response.json()["id"]

    yield movie_id

    admin_user.movies_api.delete_movie(
        movie_id,
        expected_status=200,
    )


@pytest.fixture
def movie_for_delete(admin_user):
    """Создание тестового фильма для проверки удаления"""
    data = {
        "name": f"Test Movie {uuid.uuid4()}",
        "description": "Test Description",
        "price": 10,
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    response = admin_user.movies_api.create_movie(data)
    return response.json()["id"]


@pytest.fixture
def created_user_id(admin_session):
    """Создание пользователя для тестов PATCH /user/{id}"""
    payload = {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": DataGenerator.generate_random_password(),
        "verified": True,
        "banned": False,
    }

    response = admin_session.post(f"{BASE_URL}/user", json=payload)
    assert response.status_code == 201, "Не удалось создать пользователя"
    return response.json()["id"]


@pytest.fixture
def card_data():
    """Валидные данные банковской карты для тестового API"""
    return {
        "cardNumber": "4242424242424242",
        "cardHolder": "John Doe",
        "expirationDate": "12/25",
        "securityCode": 123,
    }


@pytest.fixture
def existing_movie_id(auth_session):
    """Возвращает id существующего опубликованного фильма"""
    response = auth_session.get(
        f"{API_BASE_URL}{MOVIES_ENDPOINT}",
        params={"published": True},
    )
    assert response.status_code == 200, (
        f"Ошибка получения списка фильмов: {response.text}"
    )
    data = response.json()
    movies = data.get("movies", [])
    assert movies, "Список фильмов пуст"
    return movies[0]["id"]


@pytest.fixture
def payment_payload(card_data, existing_movie_id):
    """Корректный payload для создания платежа"""
    return {
        "movieId": existing_movie_id,
        "amount": random.randint(1, 5),
        "card": card_data,
    }


@pytest.fixture
def payment_payload_with_invalid_card_number(card_data, existing_movie_id):
    """Невалидные данные банковской карты"""
    card_data_invalid = card_data.copy()
    card_data_invalid["cardNumber"] = "0000000000000000"
    return {
        "movieId": existing_movie_id,
        "amount": 1,
        "card": card_data_invalid,
    }
