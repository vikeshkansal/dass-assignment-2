# Part - 1 Report

## Part 1.2 

### Fixes

Iteration 1: Fixed import errors by adding a `__init__.py` to the `moneypoly` directory.
Iteration 2: added docstrings and removed unused import from `moneypoly/bank.py`.
Iteration 3: added module docstring and changed '==' based comparison to simply 'is' comparison in `moneypoly/board.py`.
Iteration 4: added module docstrings and reformatted long lines in `moneypoly/cards.py`.
Iteration 5: added module docstring in `moneypoly/config.py`.
Iteration 6: removed unused import of `BOARD_SIZE`, added module docstring, defined `double_streak` attribute in `__init__` for Dice class in `moneypoly/dice.py`.
Iteration 7: added module docstring, removed unused imports (`os`, `GO_TO_JAIL_POSITION`), fixed unnecessary `elif` after `break`, and added missing final newline in `moneypoly/game.py`.
Iteration 8: removed unnecessary parens after 'not' keyword, used normal print statement instead of f-string since no interpolated variables in `moneypoly/game.py`.
Iteration 9: added newline at last line, module docstring, removed unused `sys` import, removed unused variable `old_position` in `moneypoly/player.py`.
Iteration 10: added module docstring and class docstring for `PropertyGroup`, removed unnecessary `else` after `return` in `unmortgage` in `moneypoly/property.py`.
Iteration 11: added module docstring and changed bare `except` to `except ValueError` in `safe_int_input` in `moneypoly/ui.py`.
Iteration 12: changed the `is_eliminated` property to be a class attribute (used to be instance attribute) since it is an immutable data type in `moneypoly/player.py`.
Iteration 13: changed `turn_number`, `running`, `current_index`, `board` to be class attributes instead of instance attributes in the `Game` class since there's only ever 1 instance of `Game`, refactored `_apply_card` to fix the too-many-branches warning by using dispatch dictionary by defining helper functions in `moneypoly/game.py`.
Iteration 14: changed `is_mortgaged`, `houses` to be a class property from an instance property, changed `mortgage_value` to a property method in the `Property` class, also changed `group` to be read as a keyword argument that is to be passed whenever property is made in `moneypoly/property.py`. Changed `moneypoly/board.py` to accomodate this.
Iteration 15: added function and module docstrings to `main.py`.
