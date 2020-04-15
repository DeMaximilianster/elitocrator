from collections import defaultdict
import csv

DATABASE_PATH = "./model/elitocrator_db.csv"

SIDES = ['com', 'adm', 'cod', 'con', 'mem', 'tim']
NAMES = ['Комитет', 'Админосостав', 'Кодеры', 'Контент-мейкеры', 'Участники', 'Тимка']

NAMES_TO_SIDES = dict(zip(NAMES, SIDES))  # + {'Контентмейкеры': 'con'}
SIDES_TO_NAMES = dict(zip(SIDES, NAMES))


class Request:
    def __init__(self, text: str, text_denied: str, text_approved: str, denied: dict, approved: dict):
        self.text = text
        self.text_denied = text_denied
        self.text_approved = text_approved
        self.denied = denied
        self.approved = approved


def sides_to_dict(l: list) -> dict:
    return {key: int(value) for key, value in zip(SIDES, l)}


def csv_to_requests(path: str) -> defaultdict:
    fdict = defaultdict(list)
    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for column in tuple(zip(*reader))[1:]:  # первый столбец заголовок
            side, text, text_denied, text_approved, _, *diff_list = column
            side_numb = len(SIDES)
            denied = sides_to_dict(diff_list[:side_numb])
            approved = sides_to_dict(diff_list[-side_numb:])

            request = Request(text, text_denied, text_approved, denied, approved)
            side_key = NAMES_TO_SIDES[side]
            fdict[side_key].append(request)
    return fdict
