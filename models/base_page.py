from models.page_action import PageAction


class BasePage:
    def __init__(self, page):
        self.page = page
        self.action = PageAction(page)
        self.home_url = "https://dev-cinescope.coconutqa.ru/"

        # Общие локаторы для всех страниц на сайте
        self.home_button = "a[href='/' and text()='Cinescope']"
        self.all_movies_button = "a[href='/movies' and text()='Все фильмы']"

    def open_url(self, url: str):
        self.action.open_url(url)

    def go_to_home_page(self):
        self.action.click_element(self.home_button)
        self.action.wait_redirect_for_url(self.home_url)

    def go_to_all_movies(self):
        self.action.click_element(self.all_movies_button)
        self.action.wait_redirect_for_url(f"{self.home_url}movies")

    def make_screenshot_and_attach_to_allure(self):
        self.action.make_screenshot_and_attach_to_allure()
