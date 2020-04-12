from random import choice
from collections import defaultdict
import csv

sides_list = ['com', 'adm', 'cod', 'con', 'mem', 'tim']
sides_dict = {
    'Комитет': 'com',
    'Админосостав': 'adm',
    'Кодеры': 'cod',
    'Контент-мейкеры': 'con',
    'Контентмейкеры': 'con',
    'Участники': 'mem',
    'Тимка': 'tim'
}


class Game:
    def __init__(self):
        self.turns = 1
        self.activity = 1000
        self.sides = {
            'com': Side('Комитет'),
            'adm': Side('Админосостав'),
            'cod': Side('Кодеры'),
            'con': Side('Контент-мейкеры'),
            'mem': Side('Участники'),
            'tim': Side('Тимка')
        }

        requests_dict = csv_to_requests('test.csv')
        for side in sides_list:
            self.sides[side].requests = requests_dict[side]

        for side in sides_list:
            for request in self.sides[side].requests:
                print(request.text)

    def play(self):
        while self.activity > 0:
            self.status()
            self.one_turn()
            if not self.check_satisfaction():
                print("В чатике произошла революция и вас свергли. Прожито ходов: {}".format(self.turns-1))
                break
        else:
            print("У вас закончились ЯМы и чатик умир. Прожито ходов: {}".format(self.turns-1))

    def status(self):
        print("Ход:", self.turns)
        print("Актив:", self.activity, 'сообщ./день', end='\n\n')
        for side in self.sides:
            print(self.sides[side].name + ': ' + str(self.sides[side].reputation))

    def one_turn(self):
        side = input()
        request = self.sides[side].make_request()
        answer = input()
        approved = True if answer == '+' else False
        request.reaction(approved)
        self.activity -= 75
        self.turns += 1

    def check_satisfaction(self):
        additional_activity = 0
        for side in self.sides:
            reputation = self.sides[side].reputation
            if reputation <= 0 or reputation >= 15:
                return False
            if reputation > 10:
                additional_activity += 10*(reputation-10)
        self.activity += additional_activity
        print("Изменения актива:\n\n-75 падение каждый ход")
        if additional_activity:
            print(f"+{additional_activity} дополнительный актив от довольных фракций")
        print()

        return True


class Side:
    def __init__(self, name):
        self.name = name
        self.reputation = 7
        self.requests = []

    def make_request(self):
        request = choice(self.requests)
        print(request.text)
        return request

    def change_reputation(self, number):
        self.reputation += number


class Request:
    def __init__(self, text: str, text_denied: str, text_approved: str, denied: dict, approved: dict):
        self.text = text
        self.text_denied = text_denied
        self.text_approved = text_approved
        self.denied = denied
        self.approved = approved

    def reaction(self, approved):
        if approved:
            print(self.text_approved, end='\n\n')
            sides_dictionary = self.approved
        else:
            print(self.text_denied, end='\n\n')
            sides_dictionary = self.denied
        print('Изменения репутации:', end='\n\n')
        for side in sides_dictionary:
            difference = str(sides_dictionary[side])
            if difference[0] != '-':
                difference = '+' + difference
            game.sides[side].change_reputation(sides_dictionary[side])
            print(game.sides[side].name + ': ' + difference)
        print()


def sides_to_dict(l):
    return {key: int(value) for key, value in zip(sides_list, l)}


def csv_to_requests(path):
    fdict = defaultdict(list)
    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for column in tuple(zip(*reader))[1:]:  # первый столбец заголовок
            side, text, text_denied, text_approved, _, *diff_list = column
            denied, approved = sides_to_dict(diff_list[:6]), sides_to_dict(diff_list[-6:])

            request = Request(text, text_denied, text_approved, denied, approved)
            side_key = sides_dict[side]
            fdict[side_key].append(request) 
    return fdict


game = Game()
game.play()
