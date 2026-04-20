import pytest
import allure


@allure.epic("Movies")
@allure.feature("GET /movies")
class TestGetMovies:

    @pytest.mark.smoke
    @allure.story("Получение списка фильмов")
    @allure.title("Успешное получение списка фильмов")
    def test_get_movies_public_returns_movies_list(self, api_manager):
        """Проверка получения списка фильмов"""
        with allure.step("Отправка GET запроса на получение списка фильмов"):
            response = api_manager.movies_api.get_movies()

        with allure.step("Проверка, что ответ содержит список фильмов"):
            data = response.json()
            assert "movies" in data
            assert isinstance(data["movies"], list)

    @pytest.mark.regression
    @allure.story("Фильтрация фильмов")
    @allure.title("Проверка фильтрации фильмов по цене и статусу публикации")
    def test_get_movies_with_filters(self, api_manager):
        """Проверка, что API возвращает фильмы, соответствующие заданным фильтрам по цене и статусу публикации"""
        with allure.step("Подготовка параметров фильтрации"):
            params = {
                "minPrice": 5,
                "maxPrice": 20,
                "published": True,
            }

        with allure.step("Отправка GET запроса с фильтрами"):
            response = api_manager.movies_api.get_movies(params=params)

        with allure.step("Проверка, что список отфильтрованных фильмов не пуст"):
            data = response.json()
            movies = data["movies"]
            assert movies, "Список отфильтрованных фильмов пуст"

        with allure.step("Проверка, что все фильмы соответствуют фильтрам"):
            for movie in movies:
                assert 5 <= movie["price"] <= 20, f"Цена фильма {movie['price']} не в диапазоне 5-20"
                assert movie["published"] is True, f"Фильм {movie['name']} не опубликован"

    @pytest.mark.regression
    @allure.story("Пагинация")
    @allure.title("Проверка наличия полей пагинации в ответе")
    def test_get_movies_response_has_pagination_fields(self, api_manager):
        """Ответ содержит обязательные поля пагинации"""
        with allure.step("Отправка GET запроса на получение списка фильмов"):
            response = api_manager.movies_api.get_movies()
            data = response.json()

        with allure.step("Проверка наличия полей пагинации"):
            assert "count" in data, "Отсутствует поле count"
            assert "page" in data, "Отсутствует поле page"
            assert "pageSize" in data, "Отсутствует поле pageSize"
            assert "pageCount" in data, "Отсутствует поле pageCount"

    @pytest.mark.regression
    @allure.story("Валидация данных")
    @allure.title("Проверка, что фильмы в списке содержат обязательные поля")
    def test_get_movies_items_have_required_fields(self, api_manager):
        """Фильмы в списке содержат обязательные поля"""
        with allure.step("Отправка GET запроса на получение списка фильмов"):
            response = api_manager.movies_api.get_movies()
            data = response.json()
            movies = data.get("movies", [])

        with allure.step("Проверка, что список фильмов не пуст"):
            if not movies:
                pytest.skip("Список фильмов пуст, проверка обязательных полей пропущена")

        with allure.step("Проверка обязательных полей у первого фильма"):
            movie = movies[0]
            assert "id" in movie, "Отсутствует поле id"
            assert "name" in movie, "Отсутствует поле name"
            assert "price" in movie, "Отсутствует поле price"
            assert "published" in movie, "Отсутствует поле published"

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.story("Ошибки валидации")
    @allure.title("Ошибка при передаче некорректного query-параметра")
    def test_get_movies_with_invalid_query_param_returns(self, api_manager):
        """Некорректный query-параметр приводит к ошибке валидации"""
        with allure.step("Подготовка некорректного параметра"):
            params = {"page": "invalid"}

        with allure.step("Отправка GET запроса с некорректным параметром"):
            response = api_manager.movies_api.get_movies(
                params=params,
                expected_status=400,
            )

        with allure.step("Проверка статуса ответа"):
            assert response.status_code == 400, "Статус код не соответствует ожидаемому"

    @pytest.mark.regression
    @pytest.mark.negative
    @allure.story("Ошибки маршрутизации")
    @allure.title("Ошибка 404 при запросе к несуществующему endpoint")
    def test_get_movies_wrong_endpoint_returns(self, api_requester):
        """Запрос к несуществующему endpoint возвращает 404"""
        with allure.step("Отправка GET запроса к несуществующему endpoint"):
            response = api_requester.send_request(
                method="GET",
                endpoint="/movie",
                expected_status=404,
            )

        with allure.step("Проверка сообщения об ошибке"):
            data = response.json()
            assert "message" in data, "В ответе отсутствует сообщение об ошибке"

    @pytest.mark.parametrize(
        "params, check_type, expected",
        [
            ({"minPrice": 5, "maxPrice": 20, "published": True}, "price", (5, 20)),
            ({"locations": ["MSK"], "published": True}, "location", "MSK"),
            ({"genreId": 1, "published": True}, "genre", 1),
        ],
        ids=[
            "filter_by_price_range",
            "filter_by_location_msk",
            "filter_by_genre_id_1",
        ]
    )
    @pytest.mark.regression
    @allure.story("Фильтрация фильмов")
    @allure.title("Параметризованная проверка фильтрации фильмов: {check_type}")
    def test_get_movies_with_filters_parametrized(self, api_manager, params, check_type, expected):
        """Параметризованный тест фильтрации фильмов"""
        with allure.step("Отправка GET запроса с параметрами фильтрации"):
            response = api_manager.movies_api.get_movies(params=params)

        with allure.step("Проверка, что список отфильтрованных фильмов не пуст"):
            data = response.json()
            movies = data["movies"]
            assert movies, "Список отфильтрованных фильмов пуст"

        with allure.step(f"Проверка фильтрации по полю {check_type}"):
            for movie in movies:
                if check_type == "price":
                    min_price, max_price = expected
                    assert min_price <= movie["price"] <= max_price, \
                        f"Цена фильма {movie['price']} не в диапазоне {min_price}-{max_price}"

                elif check_type == "location":
                    assert movie["location"] == expected, \
                        f"Локация фильма {movie['location']} не соответствует ожидаемой {expected}"

                elif check_type == "genre":
                    assert movie["genreId"] == expected, \
                        f"Жанр фильма {movie['genreId']} не соответствует ожидаемому {expected}"
