import uuid


def test_create_movie_with_valid_data_returns(admin_user):
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

    response = admin_user.movies_api.create_movie(
        data=payload,
        expected_status=201,
    )

    movie = response.json()

    assert movie["name"] == payload["name"]
    assert movie["price"] == payload["price"]
    assert movie["location"] == payload["location"]
    assert movie["description"] == payload["description"]
    assert movie["genreId"] == payload["genreId"]
    assert movie["published"] == payload["published"]


def test_create_movie_without_name_returns(admin_user):
    """Попытка создания фильма без поля name"""
    payload = {
        "imageUrl": "https://example.com/image.png",
        "price": 300,
        "description": "Test movie description",
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    response = admin_user.movies_api.create_movie(
        data=payload,
        expected_status=400,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"


def test_create_movie_with_invalid_price_type_returns(admin_user):
    """Проверка валидации типа поля price при создании фильма"""
    payload = {
        "name": f"Negative Price Movie {uuid.uuid4()}",
        "imageUrl": "https://example.com/image.png",
        "price": "free",
        "description": "Invalid price",
        "location": "MSK",
        "published": True,
        "genreId": 1,
    }

    response = admin_user.movies_api.create_movie(
        data=payload,
        expected_status=400,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"


def test_create_movie_with_duplicate_name_returns(admin_user):
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

    admin_user.movies_api.create_movie(
        data=payload,
        expected_status=201,
    )

    response = admin_user.movies_api.create_movie(
        data=payload,
        expected_status=409,
    )

    data = response.json()
    assert "message" in data, "В ответе отсутствует сообщение об ошибке"
