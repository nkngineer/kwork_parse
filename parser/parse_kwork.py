import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ai.gigachat_processing import get_categorized_description
from database import Database

db = Database()


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

        self.page_len: int = self.get_page_len()
        if not self.page_len:
            raise RuntimeError(
                "Failed to initialize parser: could not determine page count"
            )

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
        Returns len of all pages at the market.
        There is always one more page(taken into account).
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
            else:
                raise ValueError("Page count is 0")
        except Exception as e:
            print("Cannot get page count")
            print(e)
            return

    def _card_project_url(self, card) -> str | None:
        """
        Returns the link to the project inside the card.
        Used as the card's stable primary key.
        (persists across page reloads)
        """
        try:
            link = card.find_element(By.CSS_SELECTOR, 'a[href*="/projects/"]')
            return link.get_attribute("href")
        except NoSuchElementException:
            return None

    def get_offer_url(self, card) -> tuple[str, str]:
        """
        Returns the (url, text) for the service offer on the card.

        On Kwork, the "Offer a service" button does not have a dedicated URL: it
        triggers a JS modal window that neither changes the page address nor opens
        a new tab (the button itself has no href attribute). Therefore, clicking it
        is not an option — it leads nowhere and may block the driver.
        Instead, the returned URL is the direct link to the project from the card,
        which is exactly where the freelancer submits their service offer.
        """
        offer_text = ""
        try:
            offer_link = card.find_element(
                By.XPATH,
                ".//*[contains(@class, 'projects-offer-btn')"
                " and contains(normalize-space(string(.)), 'Предложить услугу')]",
            )
            offer_text = offer_link.text.strip()
        except NoSuchElementException:
            pass

        return self._card_project_url(card) or "", offer_text

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

            processed: set[str] = set()

            while True:
                cards = self.driver.find_elements(By.CLASS_NAME, "want-card")
                card = None
                for candidate in cards:
                    try:
                        candidate.find_element(By.TAG_NAME, "h1")
                    except NoSuchElementException:
                        continue
                    candidate_key = self._card_project_url(candidate)
                    if candidate_key and candidate_key in processed:
                        continue
                    card = candidate
                    break
                if card is None:
                    break

                card_key = self._card_project_url(card)
                try:
                    card_description = card.find_element(
                        By.CLASS_NAME, "wants-card__description-text"
                    )
                    more_button = card_description.find_element(
                        By.CLASS_NAME, "kw-link-dashed"
                    )
                    self.driver.execute_script("arguments[0].click();", more_button)
                    actions = ActionChains(self.driver)
                    actions.move_to_element(card).perform()
                    self.driver.execute_script(
                        "document.querySelector('.cookies-agreement')?.remove();"
                    )

                    card_title = card.find_element(By.TAG_NAME, "h1")
                    title = card_title.text
                    description = card_description.text
                    card_cost = card.find_element(By.CLASS_NAME, "wants-card__right")
                    cost = card_cost.text
                    time_left_element = card.find_element(
                        By.XPATH, ".//span[contains(text(), 'Осталось')]"
                    )
                    time_left = time_left_element.text
                    ai_description = get_categorized_description(description)

                    offer_url, offer_text = self.get_offer_url(card)

                    db.insert(
                        title, description, offer_url, cost, time_left, ai_description
                    )
                    db.commit()
                    # print("URL service offer:", offer_url)
                    # print(title)
                    # print(description)
                    # print(cost)
                    # print(offer_text)
                    # print(time_left)
                    # print("---")
                    # print(ai_description)

                except Exception as e:
                    print(f"Card skipped. Error: {e}")
                finally:
                    if card_key:
                        processed.add(card_key)
                    try:
                        self.driver.execute_script("arguments[0].remove()", card)
                    except Exception:
                        pass


def main():
    load_dotenv()
    c = Parser(
        os.getenv("KWORK_LOGIN"), os.getenv("KWORK_PASSWORD"), os.getenv("PROFILE_PATH")
    )
    c.parse_marketplace()


if __name__ == "__main__":
    main()
