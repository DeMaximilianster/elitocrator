from random import choice
from collections import defaultdict
import csv

sides_list = ['com', 'adm', 'cod', 'con', 'mem', 'tim']
names_list = ['Комитет', 'Админосостав', 'Кодеры', 'Контент-мейкеры', 'Участники', 'Тимка']

names_to_sides_dict = {i: j for i, j in zip(names_list, sides_list)}  # + {'Контентмейкеры': 'con'}
sides_to_names_dict = {i: j for i, j in zip(sides_list, names_list)}


class ChoiceQuery:
    def __init__(self, choose_dict, numlist=True):
        self.dict = choose_dict
        self.numlist = numlist


class ConsoleInterface:
    def __init__(self, game):
        self.game = game
        self.game.set_interface(self)

    def display(self, text):
        print(text)

    def make_choice(self, options):
        print('(', '/'.join(options.keys()), '): ', sep='', end='')
        answers = options
        while 1:
            inp = input()
            if inp in answers:
                return answers[inp]
            print('Некорректный ввод')

    def make_numbered_choice(self, options):
        for i, j in enumerate(options.keys()):
            print(f'{i + 1} - {j}')
        answers = {str(i + 1): j for i, j in enumerate(options.values())}
        while 1:
            inp = input()
            if inp in answers:
                print()
                return answers[inp]
            print('Некорректный ввод')

    def process_query(self, query):
        if isinstance(query, ChoiceQuery):
            if query.numlist:
                return self.make_numbered_choice(query.dict)
            else:
                return self.make_choice(query.dict)
        else:
            raise ValueError(f'Unknown Querry: {query}')

    def run_game(self):
        player = self.game.play()
        query = next(player)
        answer = self.process_query(query)
        while 1:
            try:
                query = player.send(answer)
            except StopIteration:
                break
            answer = self.process_query(query)


class Game:
    def __init__(self, bd_path):
        self.turns = 1
        self.activity = 1000
        self.activity_fall = 75
        self.sides = {
            'com': Side('Комитет'),
            'adm': Side('Админосостав'),
            'cod': Side('Кодеры'),
            'con': Side('Контент-мейкеры'),
            'mem': Side('Участники'),
            'tim': Side('Тимка')
        }
        self.last_side = False

        requests_dict = csv_to_requests(bd_path)
        for side in sides_list:
            self.sides[side].requests = requests_dict[side]

    def set_interface(self, interface):
        self.iface = interface

    def play(self):
        while self.activity > 0:
            self.iface.display(self.status())
            yield from self.one_turn()
            if not self.check_satisfaction():
                break
        else:
            self.iface.display(f"У вас закончились ЯМы и чатик умир. Прожито ходов: {self.turns - 1}")

    def status(self):
        s = f"Ход: {self.turns}\n"
        s += f"Актив: {self.activity} сообщ./день\n\n"
        for side in self.sides:
            s += f"{self.sides[side].name}: {self.sides[side].reputation}\n"
        return s

    def one_turn(self):
        choice_dict = names_to_sides_dict.copy()  # словарь сторон на выбор
        if self.last_side:  # если есть предыдущая выбранная сторона
            last_side_name = sides_to_names_dict[self.last_side]
            del choice_dict[last_side_name]  # удаляем её

        side = yield ChoiceQuery(choice_dict)

        request = self.sides[side].make_request(self.iface)
        approved = yield ChoiceQuery({'+': True, '-': False}, False)
        self.process_request(request, approved)
        self.activity -= self.activity_fall
        self.turns += 1

    def check_satisfaction(self):
        additional_activity = 0
        for side in self.sides:
            reputation = self.sides[side].reputation
            if reputation <= 0 or reputation >= 15:
                self.iface.display(f"В чатике произошла революция и вас свергли. Прожито ходов: {self.turns - 1}")
                return False
            if reputation > 10:
                additional_activity += 10 * (reputation - 10)
        self.activity += additional_activity
        s = f"Изменения актива:\n-{self.activity_fall} падение каждый ход\n"
        if additional_activity:
            s += f"+{additional_activity} дополнительный актив от довольных фракций"
        self.iface.display(s)
        return True

    def process_request(self, request, approved):
        s = ''
        if approved:
            s += request.text_approved + '\n\n'
            sides_dictionary = request.approved
        else:
            s += request.text_denied + '\n\n'
            sides_dictionary = request.denied
        s += 'Изменения репутации:\n\n'
        for side in sides_dictionary:
            difference = str(sides_dictionary[side])
            if difference[0] != '-':
                difference = '+' + difference
            self.sides[side].change_reputation(sides_dictionary[side])
            s += f'{self.sides[side].name}: {difference}\n'
        self.iface.display(s + '\n')


class Side:
    def __init__(self, name):
        self.name = name
        self.reputation = 7
        self.requests = []

    def make_request(self, interface):
        request = choice(self.requests)
        interface.display(f'{self.name}:\n{request.text}')
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
            side_key = names_to_sides_dict[side]
            fdict[side_key].append(request)
    return fdict


iface = ConsoleInterface(Game('test.csv'))
iface.run_game()