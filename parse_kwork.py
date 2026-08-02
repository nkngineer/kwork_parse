import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from mistral import get_categorized_description
from parse_json import decode_json_list

"""
TODO:
1. парсинг биржи
    - добавить фильтрацию (✅️, сделано через фильтры при логине. Был вариант вручную постоянно выбирать фильтры, но пусть пока будет в долгом ящике)
    - разделить название, цену, дату, подробное описание на разные части (✅️)
    - добавить парсинг всех страниц по фильтрам (✅️)
2. ИИ(mistral) обрабатывает описание и делает краткую сводку(что делать, какие инструменты и навыки требуются)
    - создать качественный промпт
    - подключить Mistral по API ✅️
    - протестировать промпт на Mistral ✅️
    - скормить карточки на каждой странице ИИ в формате json
        - сделать 2 варианта
            - парсинг и закидывание в mistral каждой карточки отдельно
            - парсинг и закидывание в mistral пачку карточек средней длины(допустим 5-6 карточек)
    - Структуризировать __init__
3. отправка в тг бота
    - сделать тг бота с вебхуками, который при обновлении ленты биржи будет высылать новые заказы в тг
4. автообновление страницы +добавление новых заказов
5. сохранение истории(?)
"""

"""
https://developers.sber.ru/docs/ru/gigachat/guides/selecting-a-model?lang=py
"""


class Connection:
    def __init__(self, login: str, password: str, profile_path: str):
        """
        Структуризировать __init__
        """
        self.login: str = login
        self.password: str = password
        options = webdriver.ChromeOptions()
        self.profile_path: str = profile_path
        options.add_argument(f"--user-data-dir={self.profile_path}")
        options.add_argument("--profile-directory=Default")
        self.driver = webdriver.Chrome(options=options)
        self.page_len: int = 0
        self.descriptions_list: list[str] = []
        self.descriptions_str: str = ""
        self.get_page_len()

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
        Либо оставить, но держать в голове, что страниц всегда на одну меньше
        Либо как-то проверять что содержит этот класс, цифру, или стрелку перемещения страниц
        """
        self.driver.get("https://kwork.ru/projects")
        pages = self.driver.find_elements(By.CLASS_NAME, "pagination__item")
        print("page_count: ", len(pages))
        self.page_len = len(pages)

    def parse_marketplace(self):
        for page in range(1, len(pages)):
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

                self.descriptions_list.append(card_description.text)

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

        self.format_for_json()
        cat_desc = get_categorized_description(self.descriptions_str)
        res = decode_json_list(cat_desc)
        print(res)

    def format_for_json(self):
        for card_id, description_card in enumerate(self.descriptions_list, start=1):
            self.descriptions_str += (
                f"Card_id : {card_id}\nCard_description : {description_card}\n"
            )

        print(self.descriptions_str)


def main():
    load_dotenv()
    c = Connection(
        os.getenv("KWORK_LOGIN"), os.getenv("KWORK_PASSWORD"), os.getenv("PROFILE_PATH")
    )
    c.parse_marketplace()


if __name__ == "__main__":
    main()
