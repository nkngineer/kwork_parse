import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from gigachat_api import get_categorized_description

"""
TODO:
3. отправка в тг бота
    - сделать тг бота с вебхуками, который при обновлении ленты биржи будет высылать новые заказы в тг
4. автообновление страницы + добавление новых заказов
5. сохранение истории(?)
"""


class Connection:
    def __init__(self, login: str, password: str, profile_path: str) -> None:
        """
        Инициализация:
        - Передача логина и пароля от kwork.ru, а также путь к конфигу с данными(чтобы не логиниться каждый раз)
        - Создание необходимых для работы переменных
        """
        self.login: str = login
        self.password: str = password
        self.profile_path: str = profile_path

        self.options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=self.options)
        self.selenium_set()

        self.page_len: int = 0
        self.get_page_len()

    def selenium_set(self):
        self.options.add_argument(f"--user-data-dir={self.profile_path}")
        self.options.add_argument("--profile-directory=Default")

    def auth(self):
        self.driver.get("https://kwork.ru/login")

        wait = WebDriverWait(self.driver, timeout=30)

        wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input[placeholder='Электронная почта или логин']")
            )
        ).send_keys(self.login)

        wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input[type='password'][placeholder='Пароль']")
            )
        ).send_keys(self.password)

        wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "button.auth-form__button.kw-button.kw-button--size-40.kw-button--green",
                )
            )
        ).click()

        print("Logged in")

    def get_page_len(self):
        """
        Страниц всегда на одну меньше
        (из-за того, что в парсинге учитывается стрелка переключения на следующую страницу)
        """
        self.driver.get("https://kwork.ru/projects")
        pages = self.driver.find_elements(By.CLASS_NAME, "pagination__item")
        print("page_count: ", len(pages))
        self.page_len = len(pages)

    def parse_marketplace(self):

        for page in range(1, self.page_len):
            url = f"https://kwork.ru/projects?a=1&page={page}"
            self.driver.get(url)
            cards = self.driver.find_elements(By.CLASS_NAME, "want-card")
            for card in cards:
                card_title = card.find_element(By.TAG_NAME, "h1")
                card_description = card.find_element(
                    By.CLASS_NAME, "wants-card__description-text"
                )
                more_button = card_description.find_element(
                    By.CLASS_NAME, "kw-link-dashed"
                )
                self.driver.execute_script("arguments[0].click();", more_button)

                ai_decription = get_categorized_description(card_description.text)

                card_cost = card.find_element(By.CLASS_NAME, "wants-card__right")

                time_left_element = card.find_element(
                    By.XPATH, ".//span[contains(text(), 'Осталось')]"
                )
                """
                Для отладки
                """
                print(card_title.text)
                print(card_description.text)
                print(card_cost.text)
                print(time_left_element.text)
                print("---")
                print(ai_decription)


def main():
    load_dotenv()
    c = Connection(
        os.getenv("KWORK_LOGIN"), os.getenv("KWORK_PASSWORD"), os.getenv("PROFILE_PATH")
    )
    c.parse_marketplace()


if __name__ == "__main__":
    main()
