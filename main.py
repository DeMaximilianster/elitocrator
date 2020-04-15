from presenter.logic import Game
from presenter.config import DATABASE_PATH
from view.console import ConsoleGamerunner

ConsoleGamerunner(Game(DATABASE_PATH)).run_game()
