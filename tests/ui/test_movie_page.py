import allure
import pytest
from playwright.sync_api import sync_playwright

from models.page_object_models import CinescopLoginPage, CinescopMoviePage

MOVIE_ID = 195737


@allure.epic("Тестирование UI")
@allure.feature("Тестирование страницы фильма")
@pytest.mark.ui
class TestMoviePage:

    @allure.title("Оставление отзыва под фильмом")
    def test_leave_review(self, registered_user):
        with sync_playwright() as plawright:
            browser = plawright.chromium.launch(headless=False)
            page = browser.new_page()

            # Логинимся
            login_page = CinescopLoginPage(page)
            login_page.open()
            login_page.login(registered_user.email, registered_user.password)
            login_page.assert_was_redirect_to_home_page()

            # Переход на страницу фильма
            movie_page = CinescopMoviePage(page)
            movie_page.open(MOVIE_ID)

            # Оставляем отзыв
            review_text = "Отличный фильм, очень понравился!"
            movie_page.leave_review(text=review_text, rating=5)

            # Проверка, что отзыв оставлен
            movie_page.assert_review_is_visible(review_text)

            # Скриншот в Allure
            movie_page.make_screenshot_and_attach_to_allure()

            browser.close()
