import random
import uuid

import pytest
import requests
from sqlalchemy.orm import Session

from clients.api.api_manager import ApiManager
from constants import (
    API_BASE_URL,
    BASE_URL,
    HEADERS,
    LOGIN_ENDPOINT,
    PAYMENT_BASE_URL,
    REGISTER_ENDPOINT,
)
from custom_requester.custom_requester import CustomRequester
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper
from entities.user import User
from enums.roles import Roles
from models.base_models import TestUser

from resources.user_creds import SuperAdminCreds
from utils.data_generator import DataGenerator


@pytest.fixture
def test_user() -> TestUser:
    """Генерация случайного пользователя для тестов"""
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER.value]
    )


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


@pytest.fixture(scope="session")
def admin_api(api_manager):
    """Создание авторизованного ApiManager для администратора"""
    admin_credentials = ("api1@gmail.com", "asdqwe123Q")
    api_manager.auth_api.authenticate(admin_credentials)
    return api_manager


@pytest.fixture
def admin_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    admin_payload = creation_user_data.copy()
    admin_payload["email"] = f"{uuid.uuid4()}@gmail.com"  # ← ВАЖНО

    user = User(
        admin_payload["email"],
        admin_payload["password"],
        [Roles.ADMIN.value],
        new_session
    )

    super_admin.api.user_api.create_user(admin_payload)
    user.api.auth_api.authenticate(user.creds)

    return user


@pytest.fixture
def registered_user(api_manager, super_admin, test_user):
    """Фикстура для регистрации и получения данных зарегистрированного пользователя"""
    response = api_manager.auth_api.register_user(test_user)
    user_id = response.json()["id"]

    super_admin.api.user_api.update_user(user_id, {"verified": True})

    user_data = test_user.model_copy()
    user_data.id = user_id
    return user_data


@pytest.fixture(scope="function")
def creation_user_data(test_user):
    updated_data = test_user.__dict__.copy()

    updated_data["roles"] = [
        role.value if isinstance(role, Roles) else role
        for role in updated_data["roles"]
    ]

    updated_data.update({
        "verified": True,
        "banned": False
    })

    return updated_data


@pytest.fixture
def created_user(super_admin, creation_user_data):
    """Фикстура для создания пользователя через API с правами супер-администратора."""
    response = super_admin.api.user_api.create_user(creation_user_data)
    return TestUser(**response.json())


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    user_data = creation_user_data.copy()
    user_data["email"] = f"{uuid.uuid4()}@gmail.com"

    user = User(
        user_data['email'],
        user_data['password'],
        [Roles.ADMIN.value],
        new_session
    )

    super_admin.api.user_api.create_user(user_data)
    user.api.auth_api.authenticate(user.creds)
    return user


@pytest.fixture
def auth_session(test_user):
    """Создание авторизованной сессии для обычного пользователя"""
    register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"

    response = requests.post(
        register_url,
        json=test_user.model_dump(mode="json", exclude_none=True),
        headers=HEADERS
    )
    assert response.status_code == 201, "Ошибка регистрации пользователя"

    login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"
    login_data = {
        "email": test_user.email,
        "password": test_user.password,
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
def user_session():
    """Фикстура для создания сессию юзера"""
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture(scope="session")
def super_admin():
    session = requests.Session()
    api_manager = ApiManager(session)

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        api_manager)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin


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
def created_movie(admin_api):
    """Фикстура для создания тестового фильма с последующим удалением после выполнения теста"""
    created_movies = []

    def _create_movie(movie_data=None):
        data = movie_data or {
            "name": f"Test Movie {uuid.uuid4()}",
            "description": "Test Description",
            "price": 10,
            "location": "MSK",
            "published": True,
            "genreId": 1,
        }

        response = admin_api.movies_api.create_movie(data)
        movie_id = response.json()["id"]

        movie = {
            "id": movie_id,
            "data": data,
            "deleted": False,
        }
        created_movies.append(movie)

        return movie

    yield _create_movie

    for movie in created_movies:
        if not movie["deleted"]:
            admin_api.movies_api.delete_movie(
                movie["id"],
                expected_status=200,
            )


@pytest.fixture
def movie_for_delete(admin_api):
    """Создание тестового фильма для проверки удаления"""
    data = {
        "name": f"Test Movie {uuid.uuid4()}",
        "description": "Test Description",
        "price": 10,
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    response = admin_api.movies_api.create_movie(data)
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
def existing_movie_id(api_manager):
    """Возвращает id существующего опубликованного фильма"""
    response = api_manager.movies_api.get_movies(
        params={"published": True},
        expected_status=200,
    )

    data = response.json()
    movies = data.get("movies", [])

    if not movies:
        pytest.fail("Список опубликованных фильмов пуст")

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


@pytest.fixture(scope="module")
def db_session() -> Session:
    """Фикстура, которая создает и возвращает сессию для работы с базой данных
        После завершения теста сессия автоматически закрывается"""
    db_session = get_db_session()
    yield db_session
    db_session.close()


@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    """Фикстура для экземпляра хелпера"""
    db_helper = DBHelper(db_session)
    return db_helper


@pytest.fixture(scope="function")
def created_test_user(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user
    # Cleanup после теста
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)
