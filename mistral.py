import logging
import os

from dotenv import load_dotenv
from mistralai.client import Mistral

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("mistral.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

load_dotenv()
client = Mistral(os.getenv("MISTRAL_API_KEY"))

TOKEN_ESTIMATE_DIVISOR = 4
MAX_TOKENS = 32000


def estimate_tokens(text: str) -> int:
    return len(text) // TOKEN_ESTIMATE_DIVISOR


def get_categorized_description(joined_cards: str):

    prompt = f"""Ты — опытный менеджер проектов и эксперт по фриланс-биржам. Твоя задача — проанализировать сразу несколько сырых описаний заказов (карточек задач от клиентов), извлечь из них ключевые требования и полностью очистить от "воды" (эмоций заказчика, нерелевантной предыстории).

    Твои шаги для КАЖДОЙ карточки:
    1. Выдели необходимые навыки, которыми должен обладать фрилансер (skills).
    2. Определи инструменты, программы, сервисы, CMS, языки или платформы (tools).
    3. Составь краткую, четкую выжимку самой задачи: что дано, что конкретно нужно сделать и какой ожидается результат (summary). 

    ВАЖНОЕ ПРАВИЛО: Ответ должен быть СТРОГО в формате валидного JSON-массива. Не пиши никаких приветствий, вводных слов или разметки markdown (например, не пиши ```json в начале). Верни только чистый JSON.

    Ожидаемый формат структуры:
    [
    {{
        "id": "номер карточки",
        "skills": ["Навык 1", "Навык 2"],
        "tools": ["Инструмент 1", "Инструмент 2"],
        "summary": "Краткое описание задачи в 2-4 предложениях..."
    }}
    ]

    Тексты заказов для анализа:
    {joined_cards}
    """
    prompt_tokens = estimate_tokens(prompt)
    log.info(
        "Prompt: %d chars, ~%d tokens (limit: %d, usage: %.1f%%)",
        len(prompt),
        prompt_tokens,
        MAX_TOKENS,
        prompt_tokens / MAX_TOKENS * 100,
    )

    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "user",
                "content": f"{prompt}",
            }
        ],
    )

    content = response.choices[0].message.content
    response_tokens = estimate_tokens(content)
    log.info(
        "Response: %d chars, ~%d tokens",
        len(content),
        response_tokens,
    )
    log.info("Total ~%d tokens (prompt + response)", prompt_tokens + response_tokens)

    return content


def main():
    z = get_categorized_description(
        """Срочно нужно написать Cleo скрипты для Grand Theft Auto San-Andreas. Делаю свою сборку для данной игры и нужен специальный Сleo скрипт, который позволит добавить игровые модели для сюжетных персонажей. Например в любой миссии у каждого сюжетного персонажа (например: Свит, Сизар) всего одна сюжетная модель, в миссиях их костюмы никак не меняются и возможно изменить только 1 модель, во всех миссиях она будет одна. Что именно мне нужно? Например есть миссия Большие Ставки и я хочу чтоб Цезарь конкретно в этом задании мог использовать другую модель (не "cesar", а "cesar2") чтоб условно эта модель привязывалась к миссии и именно в этой миссии у него был другой вариант модели (сами модели у меня есть и не нужно их создавать с нуля только прописать их в коде cleo скрипта чтоб они заменяли основную). Данную миссию я использовал лишь для примера ибо такой скрипт должен распространяться на 10-12 заданий, далее тому кто откликнется и поможет я распишу точно какие миссии и какие модели нужно в них привязать
  """
    )
    print(z)


if __name__ == "__main__":
    main()
