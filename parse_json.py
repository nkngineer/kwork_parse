import json


def decode_json_list(json_list: str) -> list[dict]:
    response_cards = json.loads(json_list)
    for card in response_cards:
        print(f"Заказ №{card['id']}")
        print(f"Навыки: {card['skills']}")
        print(f"Инструменты: {card['tools']}")
        print(f"Что нужно делать: {card['summary']}")
        print("-" * 20)

    return response_cards


def main():
    pass


if __name__ == "__main__":
    main()
