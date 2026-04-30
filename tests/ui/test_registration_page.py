from uuid import uuid4
from playwright.sync_api import Page, expect


def test_registration(page: Page):
    page.goto('https://dev-cinescope.coconutqa.ru/register')

    # Локаторы
    full_name = page.get_by_placeholder("Имя Фамилия Отчество")
    email = page.locator('[name="email"]')
    password = page.locator('[name="password"]')
    password_repeat = page.locator('[name="passwordRepeat"]')
    submit_button = page.locator('button[type="submit"]')

    user_email = f'{uuid4()}@mail.qa'

    full_name.fill("Жмышенко Валерий Альбертович")
    email.fill(user_email)
    password.fill("Qwerty1234")
    password_repeat.fill("Qwerty1234")

    submit_button.click()

    # Проверки
    expect(page).to_have_url("https://dev-cinescope.coconutqa.ru/login")
    expect(page.get_by_text("Подтвердите свою почту")).to_be_visible()
