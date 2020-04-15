"This file realises all game logic"
from random import choice

import presenter.config as config

class ChoiceQuery:
    def __init__(self, choose_dict, numlist=True):
        self.dict = choose_dict
        self.numlist = numlist


class Side:
    def __init__(self, name: str):
        self.name = name
        self.reputation = 7
        self.requests = []

    def make_request(self, interface):
        "Chooose request, shows it and returns"
        request = choice(self.requests)
        interface.display(f'{self.name}:\n{request.text}')
        return request

    def change_reputation(self, number: int):
        "Change side reputation"
        self.reputation += number


class Game:
    def __init__(self, bd_path: str):
        self.turns = 1
        self.activity = 1000
        self.activity_fall = 75
        self.sides = {i: Side(j) for i, j in zip(config.SIDES, config.NAMES)}
        self.last_side = False

        requests_dict = config.csv_to_requests(bd_path)
        for side in config.SIDES:
            self.sides[side].requests = requests_dict[side]

    def set_output_interface(self, interface):
        "set output game interface"
        self.iface = interface

    def play(self):
        "coroutine that plays the game"
        while self.activity > 0:
            self.iface.display(self.status())
            yield from self.one_turn()
            if not self.check_satisfaction():
                break
        else:
            self.iface.display(f"Актив чата упал до нуля и он умир. Прожито ходов: {self.turns - 1}")

    def status(self) -> str:
        s = f"Ход: {self.turns}\n"
        s += f"Актив: {self.activity} сообщ./день\n\n"
        for side in self.sides:
            s += f"{self.sides[side].name}: {self.sides[side].reputation}\n"
        return s

    def one_turn(self):
        choice_dict = config.NAMES_TO_SIDES.copy()  # словарь сторон на выбор
        if self.last_side:  # если есть предыдущая выбранная сторона
            last_side_name = config.SIDES_TO_NAMES[self.last_side]
            del choice_dict[last_side_name]  # удаляем её

        side = yield ChoiceQuery(choice_dict)

        request = self.sides[side].make_request(self.iface)
        self.last_side = side

        approved = yield ChoiceQuery({'+': True, '-': False}, False)
        self.process_request(request, approved)
        self.activity -= self.activity_fall
        self.turns += 1

    def check_satisfaction(self) -> bool:
        additional_activity = 0
        for side in self.sides.values():
            reputation = side.reputation
            if reputation <= 0:  #  or reputation >= 15
                self.iface.display(
                    f'Так как фракция "{side.name}" полностью потеряла к вам уважение в чатике произошла революция и вас свергли. Прожито ходов: {self.turns - 1}'
                )
                return False
            if reputation >= 15:
                self.iface.display(
                    f'Так как фракция "{side.name}" приобрела слишком большое влияние в чатике произошла революция и вас свергли. Прожито ходов: {self.turns - 1}'
                )
                return False
            if reputation > 10:
                additional_activity += 10 * (reputation - 10)
        self.activity += additional_activity
        s = f"Изменения актива:\n-{self.activity_fall} падение каждый ход\n"
        if additional_activity:
            s += f"+{additional_activity} дополнительный актив от довольных фракций\n"
        self.iface.display(s)
        return True

    def process_request(self, request, approved: bool):
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
