from constants import MOVIES_ENDPOINT
import uuid


def test_create_movie_with_valid_data_returns(api_requester):
    """Создание фильма с валидными данными"""
    payload = {
        "name": f"Test Movie Test {uuid.uuid4()}",
        "imageUrl": "https://example.com/image.png",
        "price": 300,
        "description": "Test movie description",
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    response = api_requester.send_request(
        method="POST",
        endpoint=MOVIES_ENDPOINT,
        data=payload,
        expected_status=201,
    )

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["price"] == payload["price"]
    assert data["location"] == payload["location"]
    assert "id" in data


def test_create_movie_without_name_returns(api_requester):
    """Попытка создания фильма без поля name"""
    payload = {
        "imageUrl": "https://example.com/image.png",
        "price": 300,
        "description": "Test movie description",
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    response = api_requester.send_request(
        method="POST",
        endpoint=MOVIES_ENDPOINT,
        data=payload,
        expected_status=400,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"


def test_create_movie_with_invalid_price_type_returns(api_requester):
    """Проверка валидации типа поля price при создании фильма"""
    payload = {
        "name": "Negative Price Movie",
        "imageUrl": "https://example.com/image.png",
        "price": "free",
        "description": "Invalid price",
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    response = api_requester.send_request(
        method="POST",
        endpoint=MOVIES_ENDPOINT,
        data=payload,
        expected_status=400,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"


def test_create_movie_with_duplicate_name_returns(api_requester):
    """Попытка создания фильма с уже существующим названием"""
    payload = {
        "name": f"Duplicate Movie Name Test {uuid.uuid4()}",
        "imageUrl": "https://example.com/image.png",
        "price": 250,
        "description": "Duplicate name test",
        "location": "SPB",
        "published": True,
        "genreId": 1,
    }

    # Успешный запрос
    api_requester.send_request(
        method="POST",
        endpoint=MOVIES_ENDPOINT,
        data=payload,
        expected_status=201,
    )

    # Повторный запрос — дубликат
    response = api_requester.send_request(
        method="POST",
        endpoint=MOVIES_ENDPOINT,
        data=payload,
        expected_status=409,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"
