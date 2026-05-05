import allure
import pytest

from models.page_object_models import CinescopLoginPage, CinescopMoviePage


@allure.epic("Тестирование UI")
@allure.feature("Тестирование страницы фильма")
@pytest.mark.ui
class TestMoviePage:

    @allure.title("Оставление отзыва под фильмом")
    def test_leave_review(self, page, registered_user, created_movie):
        movie = created_movie()

        login_page = CinescopLoginPage(page)
        movie_page = CinescopMoviePage(page)

        with allure.step("Логин пользователя"):
            login_page.open()
            login_page.login(
                registered_user.email,
                registered_user.password
            )
            login_page.assert_was_redirect_to_home_page()

        with allure.step("Переход на страницу фильма"):
            movie_page.open(movie["id"])

        review_text = "Отличный фильм, очень понравился!"

        with allure.step("Оставление отзыва"):
            movie_page.leave_review(
                text=review_text,
                rating=5
            )

        with allure.step("Проверка отображения отзыва"):
            movie_page.assert_review_is_visible(review_text)

        with allure.step("Скриншот"):
            movie_page.make_screenshot_and_attach_to_allure()
