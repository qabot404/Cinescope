import pytest
import allure


@allure.epic("Movies")
@allure.feature("GET /movies/{id}")
class TestGetMovieById:

    @pytest.mark.smoke
    @allure.story("Получение фильма по ID")
    @allure.title("Успешное получение фильма по валидному ID")
    def test_get_movie_by_valid_id_returns(self, api_manager, existing_movie_id):
        """Получение фильма по валидному id"""
        with allure.step(f"Подготовка ID фильма: {existing_movie_id}"):
            pass

        with allure.step(f"Отправка GET запроса на получение фильма {existing_movie_id}"):
            response = api_manager.movies_api.get_movie_by_id(existing_movie_id)

        with allure.step("Проверка ответа"):
            data = response.json()

        with allure.step("Проверка, что ID фильма соответствует запрошенному"):
            assert data["id"] == existing_movie_id

        with allure.step("Проверка наличия обязательных полей"):
            assert "name" in data, "Отсутствует поле name"
            assert "price" in data, "Отсутствует поле price"
            assert "location" in data, "Отсутствует поле location"

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.story("Ошибки получения фильма")
    @allure.title("Ошибка при получении фильма по несуществующему ID")
    def test_get_movie_by_non_existent_id_returns(self, api_manager):
        """Попытка получения фильма по несуществующему id"""
        with allure.step("Подготовка несуществующего ID"):
            non_existent_id = 99999

        with allure.step(f"Отправка GET запроса на получение фильма {non_existent_id}"):
            response = api_manager.movies_api.get_movie_by_id(
                non_existent_id,
                expected_status=404
            )

        with allure.step("Проверка сообщения об ошибке"):
            data = response.json()
            assert "message" in data, "В ответе отсутствует сообщение об ошибке"

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.story("Ошибки получения фильма")
    @allure.title("Ошибка при получении фильма с отрицательным ID")
    def test_get_movie_with_negative_id_returns(self, api_manager):
        """Попытка получения фильма с отрицательным id"""
        with allure.step("Подготовка отрицательного ID"):
            negative_id = -1

        with allure.step(f"Отправка GET запроса на получение фильма {negative_id}"):
            response = api_manager.movies_api.get_movie_by_id(
                negative_id,
                expected_status=404
            )

        with allure.step("Проверка сообщения об ошибке"):
            data = response.json()
            assert "message" in data, "В ответе отсутствует сообщение об ошибке"
