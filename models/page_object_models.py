from playwright.sync_api import Page
from models.base_page import BasePage


class CinescopLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}login"

        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.login_button = "form button[type='submit']"

    def open(self):
        self.open_url(self.url)

    def login(self, email: str, password: str):
        self.action.enter_text_to_element(self.email_input, email)
        self.action.enter_text_to_element(self.password_input, password)
        self.action.click_element(self.login_button)

    def assert_was_redirect_to_home_page(self):
        self.action.wait_redirect_for_url(self.home_url)

    def assert_allert_was_pop_up(self):
        self.action.check_pop_up_element_with_text("Вы вошли в аккаунт")


class CinescopMoviePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        self.review_textarea = "textarea[name='text']"
        self.rating_combobox = "button[role='combobox']"
        self.submit_review_button = "button[type='submit']:has-text('Отправить')"

    def open(self, movie_id: int):
        self.open_url(f"{self.home_url}movies/{movie_id}")

    def enter_review_text(self, text: str):
        self.action.enter_text_to_element(self.review_textarea, text)

    def select_rating(self, rating: int):
        self.action.click_element(self.rating_combobox)
        self.action.click_by_role("option", str(rating))

    def submit_review(self):
        self.action.click_element(self.submit_review_button)

    def leave_review(self, text: str, rating: int):
        self.enter_review_text(text)
        self.select_rating(rating)
        self.submit_review()

    def assert_review_is_visible(self, text: str):
        self.action.wait_text_visible(text)
        assert self.action.is_text_visible(text), \
            f"Отзыв '{text}' не появился"


class CinescopRegisterPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.url = f"{self.home_url}register"

        self.full_name_input = "input[name='fullName']"
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.repeat_password_input = "input[name='passwordRepeat']"

        self.register_button = "form button[type='submit']"

    def open(self):
        self.open_url(self.url)

    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        self.action.enter_text_to_element(self.full_name_input, full_name)
        self.action.enter_text_to_element(self.email_input, email)
        self.action.enter_text_to_element(self.password_input, password)
        self.action.enter_text_to_element(self.repeat_password_input, confirm_password)

        self.action.click_element(self.register_button)

    def assert_was_redirect_to_login_page(self):
        self.action.wait_redirect_for_url(f"{self.home_url}login")

    def assert_allert_was_pop_up(self):
        self.action.check_pop_up_element_with_text("Подтвердите свою почту")
