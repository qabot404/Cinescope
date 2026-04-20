import pytest
import allure

from models.movie_models import MovieResponse


@allure.epic("Movies")
@allure.feature("PATCH /movies/{id}")
class TestUpdateMovie:

    @pytest.mark.smoke
    @allure.story("Редактирование фильма")
    @allure.title("Успешное обновление фильма")
    def test_edit_movie_by_valid_id_returns(self, admin_api, created_movie):
        """Редактирование фильма по валидному id"""
        with allure.step("Создание тестового фильма"):
            movie = created_movie()

        with allure.step("Подготовка данных для обновления"):
            payload = {"price": 600}

        with allure.step(f"Отправка PATCH запроса на обновление фильма {movie['id']}"):
            response = admin_api.movies_api.update_movie(
                movie_id=movie["id"],
                data=payload,
                expected_status=200,
            )
        with allure.step("Проверка ответа через Pydantic модель"):
            parsed = MovieResponse(**response.json())

            assert parsed.id == movie["id"]
            assert parsed.price == payload["price"]

    @pytest.mark.parametrize(
        "movie_id",
        [
            99999,
            -1
        ],
        ids=[
            "Ошибка при обновлении фильма с несуществующим id: 99999",
            "Ошибка при обновлении фильма с отрицательным id: -1"
        ]
    )
    @pytest.mark.regression
    @allure.story("Ошибки обновления фильма")
    @allure.title("Ошибка при обновлении фильма с невалидным id: {movie_id}")
    def test_edit_movie_with_invalid_id_returns(self, admin_api, movie_id):
        with allure.step(f"Подготовка данных для обновления фильма с id = {movie_id}"):
            payload = {"price": 900}

        with allure.step(f"Отправка PATCH запроса на обновление фильма {movie_id}"):
            response = admin_api.movies_api.update_movie(
                movie_id=movie_id,
                data=payload,
                expected_status=404,
            )

        with allure.step("Проверка сообщения об ошибке"):
            data = response.json()
            assert "message" in data, "В ответе отсутствует сообщение об ошибке"

    @pytest.mark.db
    @allure.story("Проверка обновления в БД")
    @allure.title("Проверка, что фильм реально обновился в БД")
    def test_edit_movie_with_db_validation(self, admin_api, created_movie, db_helper):
        """Обновление фильма по валидному id с проверкой в БД"""
        with allure.step("Создание тестового фильма"):
            movie = created_movie()
            movie_id = movie["id"]

        with allure.step("Подготовка данных для обновления"):
            payload = {"price": 777}

        with allure.step(f"Отправка PATCH запроса на обновление фильма {movie_id}"):
            admin_api.movies_api.update_movie(
                movie_id=movie_id,
                data=payload,
                expected_status=200,
            )

        with allure.step("Проверка обновления в базе данных"):
            movie_in_db = db_helper.get_movie_by_id(movie_id)

        with allure.step("Проверка, что цена в БД соответствует обновленной"):
            assert movie_in_db is not None, "Фильм не найден в БД"
            assert movie_in_db.price == payload["price"], "Цена в БД не обновилась"
