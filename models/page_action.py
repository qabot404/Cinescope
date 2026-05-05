import allure
from playwright.sync_api import Page


class PageAction:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Переход на страницу: {url}")
    def open_url(self, url: str):
        self.page.goto(url)

    @allure.step("Ввод текста '{text}' в поле '{locator}'")
    def enter_text_to_element(self, locator: str, text: str):
        self.page.fill(locator, text)

    @allure.step("Клик по элементу '{locator}'")
    def click_element(self, locator: str):
        self.page.click(locator)

    @allure.step("Клик по элементу с ролью '{role}' и именем '{name}'")
    def click_by_role(self, role: str, name: str):
        self.page.get_by_role(role, name=name).click()

    @allure.step("Ожидание редиректа на {url}")
    def wait_redirect_for_url(self, url: str):
        self.page.wait_for_url(url)
        assert self.page.url == url, "Редирект не произошёл"

    @allure.step("Ожидание появления текста: '{text}'")
    def wait_text_visible(self, text: str):
        self.page.get_by_text(text).wait_for(state="visible")

    @allure.step("Проверка видимости текста: '{text}'")
    def is_text_visible(self, text: str) -> bool:
        return self.page.get_by_text(text).is_visible()

    @allure.step("Ожидание состояния элемента '{locator}' = {state}")
    def wait_for_element(self, locator: str, state: str = "visible"):
        self.page.locator(locator).wait_for(state=state)

    @allure.step("Скриншот страницы")
    def make_screenshot_and_attach_to_allure(self):
        screenshot = self.page.screenshot(full_page=True)
        allure.attach(
            screenshot,
            name="Screenshot",
            attachment_type=allure.attachment_type.PNG
        )

    @allure.step("Проверка всплывающего сообщения: '{text}'")
    def check_pop_up_element_with_text(self, text: str):
        locator = self.page.get_by_text(text)

        locator.wait_for(state="visible")
        assert locator.is_visible(), "Уведомление не появилось"

        locator.wait_for(state="hidden")
        assert not locator.is_visible(), "Уведомление не исчезло"
