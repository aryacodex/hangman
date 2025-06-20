import os
import sys
from collections import namedtuple
from dataclasses import dataclass, field
from random import randint
from time import sleep

PuzzleLetter = namedtuple('PuzzleLetter', ['character', 'guessed'])
"""Type definition for a namedtuple('character', 'guessed').
character: str
    One of the characters from the mystery word.
guessed: bool
    True if the letter has been guessed, else False.
"""

Puzzle = list[PuzzleLetter]
"""Type definition for a list of PuzzleLetter's."""


def images() -> tuple[str, ...]:
    """Return a tuple of hangman (ascii) drawings."""
    return (
        r"""
=====""",

        r"""
    +
    |
    |
    |
    |
    |
=====""",

        r"""
 +--+
    |
    |
    |
    |
    |
=====""",

        r"""
 +--+
 |  |
    |
    |
    |
    |
=====""",

        r"""
 +--+
 |  |
 O  |
    |
    |
    |
=====""",

        r"""
 +--+
 |  |
 O  |
 |  |
    |
    |
=====""",

        r"""
 +--+
 |  |
 O  |
/|  |
    |
    |
=====""",

        r"""
 +--+
 |  |
 O  |
/|\ |
    |
    |
=====""",

        r"""
 +--+
 |  |
 O  |
/|\ |
/   |
    |
=====""",

        r"""
 +--+
 |  |
 O  |
/|\ |
/ \ |
    |
====="""
    )


def get_word_list(category: str = 'animals') -> list[str]:
    """Return a list of quiz words.
    Define your list of words here.
    Words must be separated by white-space only.
    Each word list must have a unique name, and have an
    entry in the word_list_dict.
    Parameters
    ----------
    category: str
        Types of words, default: "animals"
    Returns
    -------
    list[str]
        List of words of selected category
    Raises
    ------
    ValueError
        If 'category' invalid.
    """

    category = category.lower()

    animal_words = """
    Dog Cat Elephant Lion Tiger Giraffe Zebra Bear Koala
    Panda Kangaroo Penguin Dolphin Eagle Owl Fox Wolf Cheetah
    Leopard Jaguar Horse Cow Pig Sheep Goat Chicken Duck Goose
    Swan Octopus Shark Whale Platypus Chimpanzee Gorilla Orangutan
    Baboon Raccoon Squirrel Bat Hedgehog Armadillo Sloth Porcupine
    Anteater Camel Dingo Kangaroo Rat Lemur Meerkat Ocelot Parrot
    Quokka Vulture Wombat Yak Iguana jaguar Kakapo Lemming
    Manatee Nutria Ostrich Pangolin Quail Rhinoceros Serval
    Wallaby Coypu Tapir Pheasant
    """

    word_list_dict = {'animals': animal_words}

    try:
        words: str = word_list_dict[category]
        return [word.upper() for word in words.split()]
    except KeyError as exc:
        raise ValueError("Invalid category.") from exc


def get_secret_word() -> str:
    """Return a random word from multiple options."""
    try:
        words: list[str] = get_word_list()
    except ValueError as exc:
        raise RuntimeError("Unable to retrieve word list.") from exc
    secret_word = words[randint(0, len(words) - 1)]
    if isinstance(secret_word, str) and len(secret_word) > 0:
        return secret_word
    raise RuntimeError("Unable to return secret word.")


@dataclass
class GameState:
    """Manage state for the game.
    Attributes
    ----------
    player_name : str
        The player's name.
    word : str
        The mystery word.
    current_guess : str
        The current guess.
    guesses : set
        The set of all guesses tried in this game.
    remaining_letters : set
        The set of letters still required.
    puzzle : list
        Puzzle list.
    image_idx : int
        Index of the image to display.
    """
    player_name: str = ''
    word: str = ''
    current_guess: str = ''
    guesses: set[str] = field(default_factory=set)
    remaining_letters: set[str] = field(default_factory=set)
    puzzle: Puzzle = field(default_factory=list)
    image_idx: int = 0

    def initialise_game_state(self, ) -> None:
        """Post-instantiation initialisation.
        Complete the initialisation of GameState after
        puzzle_word has been set.
        """
        self.remaining_letters = set(self.word)
        self.puzzle = [PuzzleLetter(char, False) for char in self.word]

    def update_state_on_guess(self) -> None:
        """Update the game state based on the current guess.
        Tries to remove the guessed letter from the remaining_letters set.
        If the letter is not in the word, increment the image index.
        """
        try:
            self.remaining_letters.remove(self.current_guess)
            self.update_puzzle()
        except KeyError:
            self.image_idx += 1  # Not in word

    def update_puzzle(self) -> None:
        """Return updated puzzle.
        Called by update_game_state to handle updating the puzzle data.
        Add 'True' to each matching tuple and return result.
        """
        self.puzzle = [
            PuzzleLetter(char, val or (char == self.current_guess))
            for char, val in self.puzzle]

    def reset_current_game(self) -> None:
        """Reset current game settings.
        Does not reset entire session as some game settings,
        such as _player_name, need to persist across multiple games.
        """
        self.word = ''
        self.current_guess = ''
        self.guesses = set()
        self.remaining_letters = set()
        self.puzzle = []
        self.image_idx = 0


class UI:
    """User interface class."""

    def __init__(self, game_state: GameState) -> None:
        """Initialise UI.
        Parameters
        ----------
        game_state: GameState
            Game state
        """
        self.game_state = game_state
        self._indent = ' ' * 4

    def indent_text(self, text: str):
        """Indent each printed line."""
        indented = '\n'.join(
            [self._indent + line for line in str(text).split('\n')])
        return indented

    def display_message(self, message: str, end: str = '\n') -> None:
        """Display arbitrary text message to player.
        In the CLI interface, text is indented for an improved
        aesthetic appearance.
        """
        message = self.indent_text(message)
        print(message, end=end)

    def do_welcome(self) -> str:
        """Welcome new player.
        Get player's name, print welcome message and return player's name.
        Returns
        -------
        str
            The player's name.
        """
        UI.clear_terminal()
        self.print_slowly("Hi there. What's your name?", end=' ')
        player_name = input().title()
        self.print_slowly(f"Hello {player_name}.", end='\n')
        self.print_slowly(
            "You can quit at any time by pressing 'Ctrl + C'.", 8)
        return player_name

    def print_intro(self) -> None:
        """Print introduction to game.
        """
        self.print_slowly(f"OK {self.game_state.player_name}, let's play.")
        self.print_slowly("I'll think of a word""", end='')
        self.print_slowly(' .' * randint(3, 8), speed=5, indent=False)
        UI.clear_terminal()

    def get_guess(self) -> str:
        """Return a new guess.
        Returns
        -------
        str
            The guess - a single character string.
        """
        while True:
            print("Guess a letter: ", end='')
            new_guess = input().strip().upper()

            if len(new_guess) != 1:
                print("Guesses must be one letter only.")
                continue
            if new_guess in self.game_state.guesses:
                print(f"You've already guessed '{new_guess}'")
                continue
            return new_guess

    def display_game_start_screen(self) -> None:
        """Inform user of word length."""
        self.print_slowly(
            "I've thought of a word.\n"
            f"The word has {len(self.game_state.word)} letters.")
        sleep(1)
        UI.clear_terminal()

    def display_game_result(self,
                            is_winner: bool,
                            correct_answer: str) -> None:
        """Congratulate or console player."""
        if is_winner:
            self.print_slowly(f"Well done {self.game_state.player_name}. "
                              f"YOU WIN!", 20)
        else:
            self.print_slowly(
                f"Too bad {self.game_state.player_name}, you loose. "
                f"The word was {correct_answer}.")
            self.print_slowly("Better luck next time.", 6)

    def get_image(self) -> str:
        """Return hangman ascii drawing."""
        return images()[self.game_state.image_idx]

    def prompt_confirm(self, prompt: str) -> bool:
        """Prompt for yes/no answer.
        Parameters
        ----------
        prompt: str
            The message prompt.
        Returns
        -------
        bool
            True if yes, else False.
        """
        yes = ('y', 'yes')
        no = ('n', 'no')
        while True:
            self.display_message(prompt, end='')
            val = input()
            if val in yes:
                return True
            if val in no:
                return False
            print("Enter 'Y' or 'N'.")

    def update_screen(self, clear: bool = True) -> None:
        """Refresh screen with current game state."""
        if clear:
            UI.clear_terminal()
        # Print hangman image.
        self.display_message(self.get_image())
        # Print underscores and guessed letters.
        output = [f'{char} ' if val else '_ ' for
                  char, val in self.game_state.puzzle]
        self.display_message(f'{"".join(output)}\n\n')

    @staticmethod
    def clear_terminal() -> None:
        """Clear the terminal."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_slowly(self,
                     message: str,
                     speed: float = 10.0,
                     end: str = '\n',
                     indent: bool = True) -> None:
        """Print message one character at a time.
        Pauses for 1/speed seconds between characters
        Parameters
        ----------
        message: str
            The message to print
        end: str
            Line termination
        speed: int
            How fast to print. Higher = faster
        indent: bool
            Whether to indent the line, default: True
        """
        try:
            delay = abs(1 / speed)
        except ZeroDivisionError:
            self.display_message("Invalid speed. Defaulting to speed = 4")
            delay = 0.25
        for line in message.split('\n'):
            if indent:
                print(self._indent, end='')
            for char in line:
                sleep(delay)
                print(char, flush=True, end='')
            print(end=end)

    def display_exit_dialog(self) -> None:
        """Dialog before quitting."""
        self.display_message(f"\nBye {self.game_state.player_name}.")


class Hangman:
    """Game logic class.
    Attributes
    ----------
    self.state: GameState
        Game state manager.
    self.ui: UI
        User interface.
    """
    def __init__(self) -> None:
        """Constructor of game logic class."""
        self.state = GameState()
        self.ui = UI(self.state)

    def initialise_game(self, puzzle_word: str) -> None:
        """Post-instantiation initialisation.
        Complete the initialisation from puzzle_word.
        """
        self.state.word = puzzle_word
        self.state.initialise_game_state()

    def update_game_state(self, new_guess: str) -> None:
        """Update game attributes according to current guess.
        If current_guess is in word, update game state.
        - update GameState::current_guess
        - update GameState::guesses
        Then tell GameState() instance to manage its own update,
        """
        self.state.current_guess = new_guess
        self.state.guesses.add(new_guess)
        self.state.update_state_on_guess()

    def is_good_guess(self) -> bool:
        """Return True if current guess in puzzle word."""
        return self.state.current_guess in self.state.word

    def player_loses(self) -> bool:
        """Return True if player has lost.
        Game is lost when final hangman image is displayed.
        """
        return self.state.image_idx == len(images()) - 1

    def do_quit(self) -> None:
        """Exit the program."""
        self.ui.display_exit_dialog()
        sys.exit()


def play_game(game: Hangman) -> bool:
    """Play game.
    Main game loop.
    Parameters
    ----------
    game: Hangman
        Instance of the game logic class.
    Returns
    -------
    bool:
        True if player wins, else False.
    """
    game.ui.update_screen(clear=False)

    while game.state.remaining_letters:
        # Update the game state from player guess.
        game.update_game_state(game.ui.get_guess())
        # Display the result.
        game.ui.update_screen()
        if game.is_good_guess():
            game.ui.display_message(f"{game.state.current_guess} is correct.")
        else:
            game.ui.display_message(f"{game.state.current_guess} is wrong.")

        # Return False if hangman complete.
        if game.player_loses():
            return False
    return True


def new_game(game: Hangman) -> None:
    """A single complete game.
    Displays a welcome message to the player, generates a secret word, and
    initiates a game. Prints a win or loose message when game completes.
    Parameters
    ----------
    game: Hangman
        Instance of the game logic class.
    """
    state = game.state
    ui = game.ui

    # player_name initialised only in first game.
    if state.player_name == '':
        state.player_name = ui.do_welcome()

    ui.print_intro()

    try:
        secret_word = get_secret_word()
    except RuntimeError as exc:
        print(f"Sorry, there has been an error: {exc}")
        sys.exit()
    # Now that we have player_name and secret_word
    # we can complete initialisation of GameState.
    game.initialise_game(secret_word)

    ui.display_game_start_screen()

    # Play game and get result
    player_wins = play_game(game)
    ui.display_game_result(player_wins, state.word)

    # Reset for next game.
    state.reset_current_game()


def main():
    """Main loop.
    Instantiate an instance of Hangman game, which will
    persist for the life of program.
    Play game repeatedly until player quits.
    """
    new_game_session = Hangman()
    while True:
        try:
            new_game(new_game_session)
        except KeyboardInterrupt:
            new_game_session.do_quit()
        if new_game_session.ui.prompt_confirm("Play again? [y/n] "):
            continue
        new_game_session.do_quit()


if __name__ == '__main__':
    # Check Python version
    if sys.version_info < (3, 9):
        print("Hangman requires Python 3.9 or later.")
        print("Please update your Python version.")
        sys.exit(1)
    main()