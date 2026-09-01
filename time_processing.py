import datetime
import re


def get_kwork_time_delta(date: str):
    days_match = re.search(r"(\d+)\s*д\.?", date)
    hours_match = re.search(r"(\d+)\s*ч\.?", date)
    minutes_match = re.search(r"(\d+)\s*мин\.?", date)

    days = int(days_match.group(1)) if days_match else 0
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0

    res = days * 24 * 60 + hours * 60 + minutes
    print(f"{res} minutes")
    delta = datetime.timedelta(minutes=res)
    return delta


def main():
    now = datetime.datetime.now()
    ex = "52 мин. 5 д. 15 ч."
    get_kwork_time_delta(ex)


if __name__ == "__main__":
    main()
