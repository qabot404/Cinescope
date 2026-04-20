import uuid
import pytest
import allure

from db_models.movies import MovieDBModel


@allure.epic("Movies")
@allure.feature("DELETE /movies/{id}")
class TestDeleteMovie:

    @pytest.mark.smoke
    @allure.story("Удаление фильма")
    @allure.title("Успешное удаление фильма по валидному id")
    def test_delete_movie_by_valid_id_returns(self, admin_api, movie_for_delete):
        """Проверка успешного удаления фильма по валидному идентификатору"""
        with allure.step(f"Отправка DELETE запроса на удаление фильма {movie_for_delete}"):
            response = admin_api.movies_api.delete_movie(movie_for_delete)

        with allure.step("Проверка статуса ответа"):
            assert response.status_code == 200, "Фильм не был успешно удалён"

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.story("Ошибки удаления фильма")
    @allure.title("Ошибка при удалении фильма по несуществующему id")
    def test_delete_movie_by_non_existent_id_returns(self, admin_api):
        """Попытка удаления фильма по несуществующему id"""
        with allure.step("Подготовка несуществующего ID"):
            non_existent_id = 99999

        with allure.step(f"Отправка DELETE запроса на удаление фильма {non_existent_id}"):
            response = admin_api.movies_api.delete_movie(
                non_existent_id,
                expected_status=404,
            )

        with allure.step("Проверка сообщения об ошибке"):
            data = response.json()

            assert "message" in data, "В ответе отсутствует сообщение об ошибке"

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.story("Ошибки удаления фильма")
    @allure.title("Ошибка при удалении фильма с отрицательным id")
    def test_delete_movie_with_negative_id_returns(self, admin_api):
        """Попытка удаления фильма с отрицательным id"""
        with allure.step("Подготовка отрицательного ID"):
            negative_id = -1

        with allure.step(f"Отправка DELETE запроса на удаление фильма {negative_id}"):
            response = admin_api.movies_api.delete_movie(
                negative_id,
                expected_status=404,
            )

        with allure.step("Проверка сообщения об ошибке"):
            data = response.json()

            assert "message" in data, "В ответе отсутствует сообщение об ошибке"

    @pytest.mark.slow
    @pytest.mark.parametrize(
        "user,expected_status",
        [
            ("super_admin", 200),
            ("admin_user", 403),
            ("common_user", 403)
        ],
        ids=[
            "super_admin_can_delete",
            "admin_cannot_delete",
            "user_cannot_delete"
        ]
    )
    @allure.story("Проверка ролей")
    @allure.title("Проверка удаления фильма в зависимости от роли пользователя: {user}")
    def test_delete_movie_with_roles(self, user, expected_status, movie_for_delete, super_admin, admin_user,
                                     common_user):
        """Проверка удаления фильма в зависимости от роли пользователя"""
        with allure.step(f"Подготовка пользователя с ролью {user}"):
            user_map = {
                "super_admin": super_admin,
                "admin_user": admin_user,
                "common_user": common_user
            }
            current_user = user_map[user]

        with allure.step(f"Отправка DELETE запроса от пользователя {user}"):
            response = current_user.api.movies_api.delete_movie(
                movie_for_delete,
                expected_status=expected_status
            )

        if expected_status != 200:
            with allure.step("Проверка сообщения об ошибке"):
                data = response.json()

                assert "message" in data
        else:
            with allure.step("Проверка успешного удаления"):

                assert response.status_code == 200

    @pytest.mark.db
    @allure.story("Проверка БД")
    @allure.title("Проверка данных в БД до создания, после создания и после удаления фильма")
    def test_create_and_delete_movie_with_database_validation(self, admin_api, db_session, created_movie):
        """Проверка данных в БД до создания фильма, после создания и после удаления"""
        with allure.step("Подготовка данных для создания фильма"):
            movie_data = {
                "name": f"Test Movie {uuid.uuid4()}",
                "description": "Test Description",
                "price": 10,
                "location": "MSK",
                "published": True,
                "genreId": 1,
            }

        with allure.step("Проверка, что фильма нет в БД до создания"):
            movie_before_create = db_session.query(MovieDBModel).filter(
                MovieDBModel.name == movie_data["name"]
            ).first()
            assert movie_before_create is None, "Фильм уже существует в БД до начала теста"

        with allure.step("Создание фильма через API"):
            created_movie_response = created_movie(movie_data)
            movie_id = created_movie_response["id"]

        with allure.step("Проверка, что фильм появился в БД после создания"):
            movie_after_create = db_session.query(MovieDBModel).filter(
                MovieDBModel.id == str(movie_id)
            ).first()
            assert movie_after_create is not None, "Фильм не появился в БД после создания"

        with allure.step(f"Отправка DELETE запроса на удаление фильма {movie_id}"):
            response = admin_api.movies_api.delete_movie(
                movie_id,
                expected_status=200,
            )
            created_movie_response["deleted"] = True

        with allure.step("Проверка, что фильм удален через API"):
            assert response.status_code == 200, "Фильм не был удален через API"

        with allure.step("Проверка, что фильм удален из БД"):
            movie_after_delete = db_session.query(MovieDBModel).filter(
                MovieDBModel.id == str(movie_id)
            ).first()
            assert movie_after_delete is None, "Фильм не был удален из БД"

    @pytest.mark.db
    @allure.story("Проверка БД")
    @allure.title("Проверка удаления фильма с валидацией через БД")
    def test_delete_movie_with_db_validation(self, super_admin, db_helper):
        """Проверка удаления фильма с валидацией через БД"""
        with allure.step("Создание фильма через БД хелпер"):
            movie = db_helper.create_movie()

        with allure.step("Проверка, что фильм существует в БД"):
            assert db_helper.get_movie_by_id(movie.id) is not None

        with allure.step(f"Отправка DELETE запроса на удаление фильма {movie.id}"):
            super_admin.api.movies_api.delete_movie(movie.id)

        with allure.step("Проверка, что фильм не доступен через API"):
            super_admin.api.movies_api.get_movie_by_id(
                movie.id,
                expected_status=404
            )

        with allure.step("Проверка, что фильм удален из БД"):
            assert db_helper.get_movie_by_id(movie.id) is None
