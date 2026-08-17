import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ai.gigachat_processing import get_categorized_description


class Parser:
    def __init__(self, login: str, password: str, profile_path: str | None) -> None:
        """
        Initialization:
        This function initialize selenium webdriver and create required variables
        """
        self.login: str = login
        self.password: str = password
        self.profile_path: str | None = profile_path

        self.options = webdriver.ChromeOptions()

        self.selenium_set()
        self.driver = webdriver.Chrome(options=self.options)

        self.page_len : int = self.get_page_len()
        if self.page_len is None:
            raise RuntimeError("Failed to initialize parser: could not determine page count")

    def selenium_set(self):
        """
        This function set webdriver options
        """
        self.options.add_argument(f"--user-data-dir={self.profile_path}")
        self.options.add_argument("--profile-directory=Default")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--headless=new")


    def auth(self):
        """
        Authorization:
        This function automatically set user login and password on kwork.ru
        """
        try:
            self.driver.get("https://kwork.ru/login")
        except Exception as e:
            print("Cannot connect to https://kwork.ru/login")
            print(e)
            return

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
        try:
            self.driver.get("https://kwork.ru/projects")
        except Exception as e:
            print("Cannot connect to https://kwork.ru/projects")
            print(e)
            return

        try:
            pages = self.driver.find_elements(By.CLASS_NAME, "pagination__item")
            if pages:
                print("page_count: ", len(pages))
                return len(pages)
            else: raise ValueError("Page count is 0")
        except Exception as e:
            print("Cannot get page count")
            print(e)
            return

    def parse_marketplace(self):
        """
        Parse marketplace function:
        1. Parser finds cards with test tasks on the marketplace page and find Title, Description and Cost
        2. Description will process by AI(Mistral | Gigachat)
        3. AI return the analyzed description with required skills and other options, that wrote in prompt
        """
        for page in range(1, self.page_len):
            url = f"https://kwork.ru/projects?a=1&page={page}"

            try:
                self.driver.get(url)
            except Exception as e:
                print(f"Cannot connect to {url}")
                print(e)
                return
            try:
                cards = self.driver.find_elements(By.CLASS_NAME, "want-card")
            except Exception as e:
                print(f"Cannot get cards")
                print(e)
                return

            for card in cards:
                try:
                    card_title = card.find_element(By.TAG_NAME, "h1")
                    card_description = card.find_element(
                        By.CLASS_NAME, "wants-card__description-text"
                    )
                    more_button = card_description.find_element(
                        By.CLASS_NAME, "kw-link-dashed"
                    )
                    self.driver.execute_script("arguments[0].click();", more_button)

                    ai_description = get_categorized_description(card_description.text)

                    card_cost = card.find_element(By.CLASS_NAME, "wants-card__right")

                    time_left_element = card.find_element(
                        By.XPATH, ".//span[contains(text(), 'Осталось')]"
                    )

                    """
                    For debug
                    """
                    print(card_title.text)
                    print(card_description.text)
                    print(card_cost.text)
                    print(time_left_element.text)
                    print("---")
                    print(ai_description)

                except Exception as e:
                    print(f"Card skipped. Error: {e}")


def main():
    load_dotenv()
    # TODO: убрать обязательный os.getenv("PROFILE_PATH")
    c = Parser(
        os.getenv("KWORK_LOGIN"), os.getenv("KWORK_PASSWORD"), os.getenv("PROFILE_PATH")
    )
    c.parse_marketplace()


if __name__ == "__main__":
    main()
