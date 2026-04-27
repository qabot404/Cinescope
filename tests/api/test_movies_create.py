import uuid
import pytest
import allure

from models.movie_models import MovieResponse


@allure.epic("Movies")
@allure.feature("POST /movies")
class TestCreateMovie:

    @pytest.mark.smoke
    @allure.story("Создание фильма")
    @allure.title("Успешное создание фильма с валидными данными")
    def test_create_movie_with_valid_data_returns(self, admin_api, db_helper):
        """Создание фильма с валидными данными"""
        with allure.step("Подготовка данных для создания фильма"):
            payload = {
                "name": f"Test Movie Test {uuid.uuid4()}",
                "imageUrl": "https://example.com/image.png",
                "price": 300,
                "description": "Test movie description",
                "location": "MSK",
                "published": True,
                "genreId": 1,
            }

        with allure.step("Отправка POST запроса на создание фильма"):
            response = admin_api.movies_api.create_movie(
                data=payload,
                expected_status=201,
            )

        with allure.step("Проверка ответа через Pydantic модель"):
            parsed = MovieResponse(**response.json())

        with allure.step("Проверка всех полей фильма"):
            assert parsed.name == payload["name"]
            assert parsed.price == payload["price"]
            assert parsed.location == payload["location"]
            assert parsed.description == payload["description"]
            assert parsed.genreId == payload["genreId"]
            assert parsed.published == payload["published"]
            assert parsed.imageUrl == payload["imageUrl"]

        with allure.step("Проверка создания фильма в базе данных"):
            movie_in_db = db_helper.get_movie_by_id(parsed.id)

            assert movie_in_db is not None, "Фильм не найден в БД"
            assert movie_in_db.name == payload["name"]
            assert movie_in_db.price == payload["price"]
            assert movie_in_db.genre_id == payload["genreId"]

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.story("Ошибки создания фильма")
    @allure.title("Ошибка при создании фильма без поля name")
    def test_create_movie_without_name_returns(self, admin_api):
        """Попытка создания фильма без поля name"""
        with allure.step("Подготовка данных без поля name"):
            payload = {
                "imageUrl": "https://example.com/image.png",
                "price": 300,
                "description": "Test movie description",
                "location": "MSK",
                "published": True,
                "genreId": 1,
            }

        with allure.step("Отправка POST запроса на создание фильма"):
            response = admin_api.movies_api.create_movie(
                data=payload,
                expected_status=400,
            )

        with allure.step("Проверка сообщения об ошибке"):
            data = response.json()

            assert "message" in data, "В ответе отсутствует сообщение об ошибке"

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.story("Ошибки создания фильма")
    @allure.title("Ошибка при создании фильма с некорректным типом price")
    def test_create_movie_with_invalid_price_type_returns(self, admin_api):
        """Проверка валидации типа поля price при создании фильма"""
        with allure.step("Подготовка данных с некорректным типом price"):
            payload = {
                "name": f"Negative Price Movie {uuid.uuid4()}",
                "imageUrl": "https://example.com/image.png",
                "price": "free",
                "description": "Invalid price",
                "location": "MSK",
                "published": True,
                "genreId": 1,
            }

        with allure.step("Отправка POST запроса на создание фильма"):
            response = admin_api.movies_api.create_movie(
                data=payload,
                expected_status=400,
            )

        with allure.step("Проверка сообщения об ошибке"):
            data = response.json()

            assert "message" in data, "В ответе отсутствует сообщение об ошибке"

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.story("Ошибки создания фильма")
    @allure.title("Ошибка при создании фильма с дублирующимся названием")
    def test_create_movie_with_duplicate_name_returns(self, admin_api):
        """Попытка создания фильма с уже существующим названием"""
        with allure.step("Подготовка данных для создания фильма"):
            payload = {
                "name": f"Duplicate Movie Name Test {uuid.uuid4()}",
                "imageUrl": "https://example.com/image.png",
                "price": 250,
                "description": "Duplicate name test",
                "location": "SPB",
                "published": True,
                "genreId": 1,
            }

        with allure.step("Создание первого фильма"):
            admin_api.movies_api.create_movie(
                data=payload,
                expected_status=201,
            )

        with allure.step("Попытка создания фильма с тем же названием"):
            response = admin_api.movies_api.create_movie(
                data=payload,
                expected_status=409,
            )

        with allure.step("Проверка сообщения об ошибке"):
            data = response.json()

            assert "message" in data, "В ответе отсутствует сообщение об ошибке"

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.story("Авторизация и доступ")
    @allure.title("Пользователь с ролью USER не может создать фильм")
    def test_create_movie_forbidden_for_common_user(self, common_user):
        """Пользователь с ролью USER не может создать фильм"""
        with allure.step("Подготовка данных для создания фильма"):
            payload = {
                "name": "Forbidden Movie",
                "imageUrl": "https://example.com/image.png",
                "price": 100,
                "description": "Should not be created",
                "location": "MSK",
                "published": True,
                "genreId": 1,
            }

        with allure.step("Отправка POST запроса от обычного пользователя"):
            response = common_user.api.movies_api.create_movie(
                data=payload,
                expected_status=403
            )

        with allure.step("Проверка сообщения об ошибке"):
            data = response.json()

            assert isinstance(data, dict), "Ответ должен быть словарем"
            assert "message" in data, "В ответе отсутствует сообщение об ошибке"


# Параметризованный тест для создания фильмов с разными жанрами
@allure.epic("Movies")
@allure.feature("POST /movies")
class TestCreateMovieParameterized:

    @pytest.mark.parametrize("genre_id, genre_name", [
        (1, "Action"),
        (2, "Comedy"),
        (3, "Drama"),
        (4, "Horror"),
    ])
    @pytest.mark.regression
    @allure.story("Создание фильма с разными жанрами")
    @allure.title("Создание фильма с жанром {genre_name} (id={genre_id})")
    def test_create_movie_with_different_genres(self, admin_api, db_helper, genre_id, genre_name):
        """Параметризованный тест создания фильмов с разными жанрами"""
        with allure.step(f"Подготовка данных для создания фильма с жанром {genre_name}"):
            payload = {
                "name": f"Genre Test Movie {genre_name} {uuid.uuid4()}",
                "imageUrl": "https://example.com/image.png",
                "price": 500,
                "description": f"Movie with {genre_name} genre",
                "location": "MSK",
                "published": True,
                "genreId": genre_id,
            }

        with allure.step("Отправка POST запроса на создание фильма"):
            response = admin_api.movies_api.create_movie(
                data=payload,
                expected_status=201,
            )

        with allure.step("Проверка ответа через Pydantic модель"):
            parsed = MovieResponse(**response.json())

        with allure.step("Проверка жанра фильма"):
            assert parsed.genreId == genre_id
            assert parsed.name == payload["name"]

        with allure.step("Проверка в базе данных"):
            movie_in_db = db_helper.get_movie_by_id(parsed.id)

            assert movie_in_db is not None
            assert movie_in_db.genre_id == genre_id
