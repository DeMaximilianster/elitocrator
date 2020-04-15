"This file realises console input/output with ConsoleGamerunner"

from presenter.logic import ChoiceQuery

class ConsoleOutput:
    @staticmethod
    def display(*args, sep=' ', end='\n'):
        "Output the information from the game"
        print(*args, sep=sep, end=end)


class ConsoleGamerunner:
    def __init__(self, game):
        self.game = game
        self.game.set_output_interface(ConsoleOutput())

    @staticmethod
    def make_choice(options: dict):
        "Realises choice interface"
        print('(', '/'.join(options.keys()), '): ', sep='', end='')
        answers = options
        while 1:
            inp = input()
            if inp in answers:
                return answers[inp]
            print('Некорректный ввод')

    @staticmethod
    def make_numbered_choice(options: dict):
        "Realises choice interface with numbered options"
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
        "Checks the type of query and asks the user"
        if isinstance(query, ChoiceQuery):
            if query.numlist:
                return self.make_numbered_choice(query.dict)
            else:
                return self.make_choice(query.dict)
        else:
            raise ValueError(f'Unknown Querry: {query}')

    def run_game(self):
        "Runs a game"
        player = self.game.play()
        query = next(player)
        answer = self.process_query(query)
        while 1:
            try:
                query = player.send(answer)
            except StopIteration:
                break
            answer = self.process_query(query)
