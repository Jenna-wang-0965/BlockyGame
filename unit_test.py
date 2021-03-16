from __future__ import annotations
from typing import *
import os
import pygame
import pytest

from block import Block
from blocky import _block_to_squares
from goal import BlobGoal, PerimeterGoal, _flatten, generate_goals
from player import _get_block, create_players, HumanPlayer, RandomPlayer, SmartPlayer
from renderer import Renderer
from settings import COLOUR_LIST

def set_children(block: Block, colours: List[Optional[Tuple[int, int, int]]]) \
        -> None:
    """Set the children at <level> for <block> using the given <colours>.

    Precondition:
        - len(colours) == 4
        - block.level + 1 <= block.max_depth
    """
    size = block._child_size()
    positions = block._children_positions()
    level = block.level + 1
    depth = block.max_depth

    block.children = []  # Potentially discard children
    for i in range(4):
        b = Block(positions[i], size, colours[i], level, depth)
        block.children.append(b)

# TODO: ~~~~~~   TASK 1   ~~~~~~     ~~~~~~   TASK 1   ~~~~~~     ~~~~~~   TASK 1   ~~~~~~
def test_rotate_1() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 3)
    # Level 1
    colours1 = [None, COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board, colours1)

    # Level 2
    colours2 = [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[0]]
    set_children(board.children[0], colours2)

    # Nothing at level 3

    # a copy of the board
    copy_board = board.create_copy()
    assert board.smash() is False
    assert board.children[0].smash() is False
    assert id(copy_board) != id(board)
    assert copy_board == board

    assert board.smashable() is False
    assert board.smash() is False
    assert board.children[0].smash() is False
    # swap vertically
    assert board.swap(1) is True
    assert board.children[0].colour == COLOUR_LIST[3]
    assert board.children[1].colour == COLOUR_LIST[1]
    assert board.children[2].colour == COLOUR_LIST[2]
    assert board.children[3].colour is None
    assert board.children[3].children[0].colour == COLOUR_LIST[1]
    assert board.children[3].children[2].colour == COLOUR_LIST[3]
    # swap vertically again
    assert board.swap(1) is True
    assert board.children[3].colour == COLOUR_LIST[3]
    assert board.children[2].colour == COLOUR_LIST[1]
    assert board.children[1].colour == COLOUR_LIST[2]
    assert board.children[0].colour is None
    assert board.children[0].children[0].colour == COLOUR_LIST[1]
    assert board.children[0].children[2].colour == COLOUR_LIST[3]
    assert board.children[1].swap(1) is False
    assert board.children[1].swap(2) is False
    assert copy_board == board
    assert id(copy_board) != id(board)
    # swap horizontally
    assert board.swap(0) is True
    assert board.children[2].colour == COLOUR_LIST[3]
    assert board.children[3].colour == COLOUR_LIST[1]
    assert board.children[0].colour == COLOUR_LIST[2]
    assert board.children[1].colour is None
    assert board.children[1].children[0].colour == COLOUR_LIST[1]
    assert board.children[1].children[2].colour == COLOUR_LIST[3]
    assert board.children[3].level - 1 == board.level
    assert board.children[1].max_depth == board.max_depth
    # swap horizontally again
    assert board.swap(0) is True
    assert copy_board == board
    assert id(copy_board) != id(board)
    assert board.children[0].swap(1) is True
    assert board.children[0].swap(1) is True
    assert board.children[0].swap(0) is True
    assert board.children[0].swap(0) is True

    # assert board.children[1].smash() is True

    assert board.children[1].combine() is False
    assert board.children[2].combine() is False
    assert board.children[0].combine() is False
    assert board.children[0].combine() is False
    assert board.children[3].combine() is False
    assert board.children[0].colour is None
    assert board.children[1].colour == COLOUR_LIST[2]
    #
    assert board.children[3].combine() is False
    assert board.children[3].combine() is False
    assert board.children[3].colour == COLOUR_LIST[3]

def test_smash_and_paint_2() -> None:
    board = Block((0, 0), 750, COLOUR_LIST[1], 0, 0)
    assert board.level == board.max_depth
    assert board.paint(COLOUR_LIST[1]) is False
    assert board.paint(COLOUR_LIST[2]) is True
    assert board.smash() is False
    assert board.combine() is False

def test_smash_3() -> None:
    board = Block((0, 0), 750, COLOUR_LIST[1], 0, 1)
    assert board.children == []
    assert board.smash() is True
    assert len(board.children) == 4
    assert board.children[3].level - 1 == board.level
    assert board.children[1].max_depth == board.max_depth
    assert board.children[0].smash() is False

def test_rotate_4() -> None:
    board = Block((0, 0), 750, COLOUR_LIST[1], 0, 1)
    assert board.rotate(1) is False
    assert board.rotate(3) is False

def test_rotate_5() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 1)
    # Level 1
    colours = [COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board, colours)
    copy_board = board.create_copy()

    # Rotate Clockwise
    assert board.rotate(1) is True
    assert board.children[0].colour == COLOUR_LIST[2]
    assert board.children[1].colour == COLOUR_LIST[0]
    assert board.children[2].colour == COLOUR_LIST[2]
    assert board.children[3].colour == COLOUR_LIST[3]
    assert board.children[1].level - 1 == board.level
    assert board.children[3].level - 1 == board.level
    assert board.paint(COLOUR_LIST[0]) is False
    assert board.children[0].paint(COLOUR_LIST[2]) is False
    assert board.children[0].paint(COLOUR_LIST[0]) is True
    assert board.children[0].paint(COLOUR_LIST[2]) is True

    # Rotate ColockWise
    assert board.rotate(1) is True
    assert board.children[1].colour == COLOUR_LIST[2]
    assert board.children[2].colour == COLOUR_LIST[3]
    assert board.children[3].colour == COLOUR_LIST[2]
    assert board.children[0].colour == COLOUR_LIST[0]
    assert board.children[1].level - 1 == board.level
    assert board.children[3].level - 1 == board.level
    assert board.children[1].max_depth == board.max_depth

    # Rotate Counter_clockwise
    assert board.rotate(3) is True
    assert board.children[0].colour == COLOUR_LIST[2]
    assert board.children[1].colour == COLOUR_LIST[0]
    assert board.children[2].colour == COLOUR_LIST[2]
    assert board.children[3].colour == COLOUR_LIST[3]
    assert board.children[1].level - 1 == board.level
    assert board.children[3].level - 1 == board.level

    # Rotate Counter-clockwise
    assert board.rotate(3) is True
    assert board == copy_board

def test_rotate_6() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 2)
    # Level 1
    colours = [COLOUR_LIST[3], None, COLOUR_LIST[0], None]
    set_children(board, colours)

    # Level 2
    colours1 = [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board.children[1], colours1)

    colours2 = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[2]]
    set_children(board.children[3], colours2)
    copy_board = board.create_copy()

    assert board.children[0].combine() is False
    assert board.children[2].combine() is False

    # Rotate clockwise
    assert board.rotate(1) is True
    assert board.children[0].colour is None
    assert board.children[1].colour == COLOUR_LIST[0]
    assert board.children[2].colour is None
    assert board.children[3].colour == COLOUR_LIST[3]
    assert board.children[1].level - 1 == board.level
    assert board.children[0].children[0].colour == COLOUR_LIST[2]
    assert board.children[0].children[1].colour == COLOUR_LIST[0]
    assert board.children[0].children[2].colour == COLOUR_LIST[2]
    assert board.children[0].children[3].colour == COLOUR_LIST[1]
    assert board.children[0].children[2].level - 2 == board.level
    assert board.children[0].children[0].rotate(1) is False
    assert board.paint(COLOUR_LIST[2]) is False
    assert board.children[3].paint(COLOUR_LIST[3]) is False
    assert board.children[3].paint(COLOUR_LIST[0]) is False
    assert board.children[0].children[3].paint(COLOUR_LIST[1]) is False
    assert board.children[0].children[0].paint(COLOUR_LIST[1]) is True
    assert board.children[0].children[0].paint(COLOUR_LIST[2]) is True

    assert board.children[2].children[0].colour == COLOUR_LIST[1]
    assert board.children[2].children[1].colour == COLOUR_LIST[3]
    assert board.children[2].children[2].colour == COLOUR_LIST[2]
    assert board.children[2].children[3].colour == COLOUR_LIST[0]
    assert board.children[2].children[2].level - 2 == board.level
    assert board.children[2].children[0].rotate(1) is False
    copy_copy_no1 = board.create_copy()

    # Rotate clockwise again
    assert board.rotate(1) is True
    assert board.children[3].colour is None
    assert board.children[0].colour == COLOUR_LIST[0]
    assert board.children[1].colour is None
    assert board.children[2].colour == COLOUR_LIST[3]
    assert board.children[3].children[3].colour == COLOUR_LIST[2]
    assert board.children[3].children[0].colour == COLOUR_LIST[0]
    assert board.children[3].children[1].colour == COLOUR_LIST[2]
    assert board.children[3].children[2].colour == COLOUR_LIST[1]
    assert board.children[3].children[2].level - 2 == board.level
    assert board.children[3].children[0].rotate(1) is False

    assert board.children[1].children[3].colour == COLOUR_LIST[1]
    assert board.children[1].children[0].colour == COLOUR_LIST[3]
    assert board.children[1].children[1].colour == COLOUR_LIST[2]
    assert board.children[1].children[2].colour == COLOUR_LIST[0]
    assert board.children[1].children[2].level - 2 == board.level
    assert board.children[1].children[0].rotate(1) is False

    # Rotate Counter-clockwise
    assert board.rotate(3) is True
    assert copy_copy_no1 == board

    # Rotate Counter-clockwise
    assert board.rotate(3) is True
    assert copy_board == board

    assert board.children[1].combine() is True
    assert board.children[1].combine() is False
    assert board.children[1].colour == COLOUR_LIST[2]

    assert board.children[3].combine() is False
    assert board.children[3].combine() is False
    assert board.children[0].colour == COLOUR_LIST[3]

def test_paint_7() -> None:
    board = Block((0, 0), 750, COLOUR_LIST[1], 0, 1)

    assert board.paint(COLOUR_LIST[2]) is False
    assert board.combine() is False

# TODO: ~~~~~~   TASK 2   ~~~~~~    ~~~~~~   TASK 2   ~~~~~~     ~~~~~~   TASK 2   ~~~~~~
def test_smash8() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 2)
    # Level 1
    colours = [COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[3]]
    set_children(board, colours)
    copy_board = board.create_copy()

    assert board.children[0].smash() is True
    assert board.children[0].smash() is False
    assert board.children[0].children[0].smash() is False
    assert board.children[3].position == (375, 375)
    assert board.children[2].position == (0, 375)
    assert board.children[0].children[0].position == (563, 0)
    assert board.children[0].children[1].position == (375, 0)
    assert board.children[0].children[2].position == (375, 188)
    assert board.children[0].children[3].position == (563, 188)

def test_smash_9() -> None:
    board = Block((0, 0), 750, COLOUR_LIST[1], 0, 0)
    assert board.smash() is False
    assert board.smash() is False

def test_smash_10() -> None:
    board = Block((0, 0), 750, COLOUR_LIST[1], 0, 1)
    assert board.smash() is True
    assert board.children[0].position == (375, 0)
    assert board.children[1].position == (0, 0)
    assert board.children[2].position == (0, 375)
    assert board.children[3].position == (375, 375)
    assert board.children[0].smash() is False
    assert board.children[2].smash() is False

def test_block_to_squares_11() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 2)
    # Level 1
    colours = [COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board, colours)

    block_squares = _block_to_squares(board)
    assert len(block_squares) == 4
    assert ((COLOUR_LIST[3]), (375, 0), 375) in block_squares
    assert ((COLOUR_LIST[2]), (0, 0), 375) in block_squares
    assert ((COLOUR_LIST[0]), (0, 375), 375) in block_squares
    assert ((COLOUR_LIST[2]), (375, 375), 375) in block_squares

def test_block_to_squares_12() -> None:
    # level 0
    board = Block((0, 0), 750, COLOUR_LIST[1], 0, 1)
    # Level 1

    block_squares = _block_to_squares(board)
    assert len(block_squares) == 1
    assert (COLOUR_LIST[1], (0, 0), 750) in block_squares

def test_block_to_squares_13() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 3)
    # Level 1
    colours1 = [None, COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board, colours1)

    # Level 2
    colours2 = [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[0]]
    set_children(board.children[0], colours2)

    # level 3

    block_squares = _block_to_squares(board)
    assert len(block_squares) == 7
    assert (COLOUR_LIST[1], (563, 0), 188) in block_squares
    assert (COLOUR_LIST[1], (375, 0), 188) in block_squares
    assert (COLOUR_LIST[3], (375, 188), 188) in block_squares
    assert (COLOUR_LIST[0], (563, 188), 188) in block_squares

    assert (COLOUR_LIST[2], (0, 0), 375) in block_squares
    assert (COLOUR_LIST[1], (0, 375), 375) in block_squares
    assert (COLOUR_LIST[3], (375, 375), 375) in block_squares

def test_block_to_squares_14() -> None:
    # Level 0
    board = Block((0, 0), 1000, None, 0, 2)
    # Level 1
    colours = [COLOUR_LIST[3], None, COLOUR_LIST[0], None]
    set_children(board, colours)

    # Level 2
    colours1 = [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board.children[1], colours1)

    colours2 = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[2]]
    set_children(board.children[3], colours2)

    block_squares = _block_to_squares(board)
    assert len(block_squares) == 10
    assert (COLOUR_LIST[3], (500, 0), 500) in block_squares

    assert (COLOUR_LIST[1], (250, 0), 250) in block_squares
    assert (COLOUR_LIST[2], (0, 0), 250) in block_squares
    assert (COLOUR_LIST[0], (0, 250), 250) in block_squares
    assert (COLOUR_LIST[2], (250, 250), 250) in block_squares

    assert (COLOUR_LIST[0], (0, 500), 500) in block_squares

    assert (COLOUR_LIST[0], (750, 500), 250) in block_squares
    assert (COLOUR_LIST[1], (500, 500), 250) in block_squares
    assert (COLOUR_LIST[3], (500, 750), 250) in block_squares
    assert (COLOUR_LIST[2], (750, 750), 250) in block_squares


# TODO: ~~~~~~   TASK 3   ~~~~~~    ~~~~~~   TASK 3   ~~~~~~     ~~~~~~   TASK 3   ~~~~~~

def test_generate_goals_15() -> None:
    goal = generate_goals(2)
    colour = COLOUR_LIST.copy()
    assert len(goal) == 2
    if isinstance(goal[0], PerimeterGoal):
        for i in goal:
            assert isinstance(i, PerimeterGoal)
            assert i.colour in colour
            colour.remove(i.colour)

    if isinstance(goal[0], BlobGoal):
        for ii in goal:
            assert isinstance(ii, BlobGoal)
            assert ii.colour in colour
            colour.remove(ii.colour)

def test_generate_goals_16() -> None:
    goal = generate_goals(0)
    assert len(goal) == 0
    assert goal == []

def test_generate_goals_17() -> None:
    goal = generate_goals(4)
    colour = COLOUR_LIST.copy()
    assert len(goal) == 4
    if isinstance(goal[0], PerimeterGoal):
        for i in goal:
            assert isinstance(i, PerimeterGoal)
            assert i.colour in colour
            colour.remove(i.colour)
        assert len(colour) == 0

    if isinstance(goal[0], BlobGoal):
        for ii in goal:
            assert isinstance(ii, BlobGoal)
            assert ii.colour in colour
            colour.remove(ii.colour)
        assert len(colour) == 0

def test_generate_goals_18() -> None:
    goal = generate_goals(3)
    colour = COLOUR_LIST.copy()
    assert len(goal) == 3
    if isinstance(goal[0], PerimeterGoal):
        for i in goal:
            assert isinstance(i, PerimeterGoal)
            assert i.colour in colour
            colour.remove(i.colour)
        assert len(colour) == 1

    if isinstance(goal[0], BlobGoal):
        for ii in goal:
            assert isinstance(ii, BlobGoal)
            assert ii.colour in colour
            colour.remove(ii.colour)
        assert len(colour) == 1

def test_generate_goals_19() -> None:
    goal = generate_goals(1)
    colour = COLOUR_LIST.copy()
    assert len(goal) == 1
    if isinstance(goal[0], PerimeterGoal):
        for i in goal:
            assert isinstance(i, PerimeterGoal)
            assert i.colour in colour
            colour.remove(i.colour)
        assert len(colour) == 3

    if isinstance(goal[0], BlobGoal):
        for ii in goal:
            assert isinstance(ii, BlobGoal)
            assert ii.colour in colour
            colour.remove(ii.colour)
        assert len(colour) == 3

# TODO: ~~~~~~   TASK 4   ~~~~~~     ~~~~~~   TASK 4   ~~~~~~     ~~~~~~   TASK 4   ~~~~~~

def test_get_block_20() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 3)
    # Level 1
    colours1 = [None, COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board, colours1)

    # Level 2
    colours2 = [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[0]]
    set_children(board.children[0], colours2)

    # level 3

    # testings at level 0
    assert _get_block(board, (0, 0), 0) == board
    assert _get_block(board, (4, 94), 0) == board
    assert _get_block(board, (9343, 32), 0) is None
    assert _get_block(board, (750, 32), 0) is None
    assert _get_block(board, (750, 0), 0) is None
    assert _get_block(board, (750, 750), 0) is None
    assert _get_block(board, (0, 750), 0) is None

    # testings at level 1
    assert _get_block(board, (0, 0), 1) == board.children[1]
    assert _get_block(board, (4, 94), 1) == board.children[1]
    assert _get_block(board, (321, 94), 1) == board.children[1]
    assert _get_block(board, (375, 94), 1) == board.children[0]
    assert _get_block(board, (375, 375), 1) == board.children[3]
    assert _get_block(board, (750, 750), 1) is None
    assert _get_block(board, (400, 750), 1) is None
    assert _get_block(board, (400, 300), 1) == board.children[0]
    assert _get_block(board, (833, 0), 1) is None
    assert _get_block(board, (500, 400), 1) == board.children[3]

    # testings at level 2
    assert _get_block(board, (0, 0), 2) == board.children[1]
    assert _get_block(board, (4, 94), 2) == board.children[1]
    # assert _get_block(board, (375, 375), 2) == board.children[3] # TODO: THIS ASSERTION FAILED
    assert _get_block(board, (375, 25), 2) == board.children[0].children[1]
    assert _get_block(board, (375, 205), 2) == board.children[0].children[2]
    assert _get_block(board, (375, 83), 2) == board.children[0].children[1]
    assert _get_block(board, (375, 299), 2) == board.children[0].children[2]
    assert _get_block(board, (400, 299), 2) == board.children[0].children[2]
    assert _get_block(board, (600, 299), 2) == board.children[0].children[3]
    assert _get_block(board, (600, 30), 2) == board.children[0].children[0]
    assert _get_block(board, (600, 188), 2) == board.children[0].children[3]
    assert _get_block(board, (563, 188), 2) == board.children[0].children[3]
    assert _get_block(board, (563, 187), 2) == board.children[0].children[0]
    assert _get_block(board, (600, 0), 2) == board.children[0].children[0]
    assert _get_block(board, (943, 0), 2) is None

    # above level 2
    assert _get_block(board, (0, 0), 3) == board.children[1]
    assert _get_block(board, (0, 0), 4) == board.children[1]
    assert _get_block(board, (375, 25), 3) == board.children[0].children[1]
    assert _get_block(board, (375, 205), 4) == board.children[0].children[2]
    assert _get_block(board, (375, 83), 3) == board.children[0].children[1]
    assert _get_block(board, (375, 299), 4) == board.children[0].children[2]
    assert _get_block(board, (400, 299), 5) == board.children[0].children[2]
    assert _get_block(board, (600, 299), 3) == board.children[0].children[3]
    assert _get_block(board, (600, 30), 4) == board.children[0].children[0]
    assert _get_block(board, (600, 188), 3) == board.children[0].children[3]

def test_get_block_21() -> None:
    # level 0
    board = Block((0, 0), 750, COLOUR_LIST[1], 0, 1)
    # Level 1

    # testings at level 0
    assert _get_block(board, (0, 0), 0) == board
    assert _get_block(board, (321, 34), 0) == board
    assert _get_block(board, (84, 34), 0) == board
    assert _get_block(board, (184, 303), 0) == board
    assert _get_block(board, (4, 303), 0) == board
    assert _get_block(board, (43, 33), 0) == board
    assert _get_block(board, (9, 3421), 0) is None
    assert _get_block(board, (750, 0), 0) is None
    assert _get_block(board, (0, 750), 0) is None
    assert _get_block(board, (92, 750), 0) is None
    assert _get_block(board, (750, 750), 0) is None
    assert _get_block(board, (750, 93), 0) is None

    # above level 0
    assert _get_block(board, (0, 0), 1) == board
    assert _get_block(board, (321, 34), 2) == board
    assert _get_block(board, (84, 34), 1) == board
    assert _get_block(board, (184, 303), 2) == board
    assert _get_block(board, (4, 303), 1) == board
    assert _get_block(board, (43, 33), 3) == board
    assert _get_block(board, (9, 3421), 5) is None
    assert _get_block(board, (750, 0), 1) is None
    assert _get_block(board, (0, 750), 2) is None
    assert _get_block(board, (92, 750), 1) is None
    assert _get_block(board, (750, 750), 1) is None
    assert _get_block(board, (750, 93), 1) is None

def test_get_block_22() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 2)
    # Level 1
    colours = [COLOUR_LIST[3], None, COLOUR_LIST[0], None]
    set_children(board, colours)

    # Level 2
    colours1 = [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board.children[1], colours1)

    colours2 = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[2]]
    set_children(board.children[3], colours2)


    # testing at level 0
    assert _get_block(board, (1, 2), 0) == board
    assert _get_block(board, (10, 22), 0) == board
    assert _get_block(board, (10, 22), 0) == board
    assert _get_block(board, (150, 22), 0) == board
    assert _get_block(board, (250, 22), 0) == board
    assert _get_block(board, (250, 220), 0) == board
    assert _get_block(board, (163, 220), 0) == board
    assert _get_block(board, (278, 89), 0) == board
    assert _get_block(board, (500, 300), 0) == board
    assert _get_block(board, (600, 300), 0) == board
    assert _get_block(board, (520, 699), 0) == board
    assert _get_block(board, (600, 700), 0) == board
    assert _get_block(board, (500, 700), 0) == board
    assert _get_block(board, (278, 300), 0) == board

    # testing at level 1
    assert _get_block(board, (500, 30), 1) == board.children[0]
    assert _get_block(board, (10, 22), 1) == board.children[1]
    assert _get_block(board, (10, 22), 1) == board.children[1]
    assert _get_block(board, (150, 22), 1) == board.children[1]
    assert _get_block(board, (250, 22), 1) == board.children[1]
    assert _get_block(board, (500, 300), 1) == board.children[0]
    assert _get_block(board, (600, 375), 1) == board.children[3]
    assert _get_block(board, (520, 699), 1) == board.children[3]
    assert _get_block(board, (600, 700), 1) == board.children[3]
    assert _get_block(board, (500, 700), 1) == board.children[3]

    # testing at level 2
    assert _get_block(board, (1, 2), 2) == board.children[1].children[1]
    assert _get_block(board, (10, 22), 2) == board.children[1].children[1]
    assert _get_block(board, (10, 22), 2) == board.children[1].children[1]
    assert _get_block(board, (150, 22), 2) == board.children[1].children[1]
    assert _get_block(board, (250, 22), 2) == board.children[1].children[0]
    assert _get_block(board, (250, 220), 2) == board.children[1].children[3]
    assert _get_block(board, (163, 220), 2) == board.children[1].children[2]
    assert _get_block(board, (278, 89), 2) == board.children[1].children[0]
    assert _get_block(board, (278, 300), 2) == board.children[1].children[3]
    assert _get_block(board, (500, 300), 2) == board.children[0]
    assert _get_block(board, (600, 300), 2) == board.children[0]
    assert _get_block(board, (520, 699), 2) == board.children[3].children[2]
    assert _get_block(board, (499, 699), 2) == board.children[3].children[2]
    assert _get_block(board, (60, 700), 2) == board.children[2]
    assert _get_block(board, (600, 700), 2) == board.children[3].children[3]
    assert _get_block(board, (10, 700), 2) == board.children[2]
    assert _get_block(board, (500, 700), 2) == board.children[3].children[2]
    assert _get_block(board, (563, 7), 2) == board.children[0]


# TODO: ~~~~~~   TASK 5   ~~~~~~     ~~~~~~   TASK 5   ~~~~~~     ~~~~~~   TASK 5   ~~~~~~

def test_update_child_pos_23() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 2)
    # Level 1
    colours = [COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[3]]
    set_children(board, colours)

    board._update_children_positions((375, 375))
    assert board.position == (375, 375)
    assert board.children[0].position == (750, 375)
    assert board.children[1].position == (375, 375)
    assert board.children[2].position == (375, 750)
    assert board.children[3].position == (750, 750)

def test_update_child_pos_24() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 3)
    # Level 1
    colours1 = [None, COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board, colours1)

    # Level 2
    colours2 = [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[0]]
    set_children(board.children[0], colours2)

    # Nothing at level 3

    board._update_children_positions((1000, 1000))
    assert board.position == (1000, 1000)
    assert board.children[0].children[0].position == (1563, 1000)
    assert board.children[0].children[1].position == (1375, 1000)
    assert board.children[0].children[2].position == (1375, 1188)
    assert board.children[0].children[3].position == (1563, 1188)

    assert board.children[1].position == (1000, 1000)
    assert board.children[2].position == (1000, 1375)
    assert board.children[3].position == (1375, 1375)

def test_update_child_pos_25() -> None:
    # Level 0
    board = Block((0, 0), 750, COLOUR_LIST[0], 0, 1)

    board._update_children_positions((750, 750))
    assert board.position == (750, 750)
    assert board.children == []

def test_update_child_pos_26() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 2)
    # Level 1
    colours = [COLOUR_LIST[3], None, COLOUR_LIST[0], None]
    set_children(board, colours)

    # Level 2
    colours1 = [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board.children[1], colours1)

    colours2 = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[2]]
    set_children(board.children[3], colours2)

    board._update_children_positions((1000, 1000))
    assert board.position == (1000, 1000)
    assert board.children[0].position == (1375, 1000)

    assert board.children[2].position == (1000, 1375)

    assert board.children[1].children[0].position == (1188, 1000)
    assert board.children[1].children[1].position == (1000, 1000)
    assert board.children[1].children[2].position == (1000, 1188)
    assert board.children[1].children[3].position == (1188, 1188)

    assert board.children[3].children[0].position == (1563, 1375)
    assert board.children[3].children[1].position == (1375, 1375)
    assert board.children[3].children[2].position == (1375, 1563)
    assert board.children[3].children[3].position == (1563, 1563)

def test_update_child_pos_27() -> None:
    # Level 0
    board = Block((0, 0), 750, COLOUR_LIST[0], 0, 0)

    board._update_children_positions((750, 750))
    assert board.position == (750, 750)
    assert board.children == []

# TODO: ~~~~~~   TASK 6   ~~~~~~     ~~~~~~   TASK 6   ~~~~~~    ~~~~~~   TASK 6   ~~~~~~
def test_flatten_28() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 3)
    # Level 1
    colours1 = [None, COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board, colours1)

    # Level 2
    colours2 = [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[0]]
    set_children(board.children[0], colours2)

    # Nothing at level 3
    copy_board = board.create_copy()
    assert id(copy_board) != id(board)
    flatten_board = _flatten(board)
    assert _flatten(copy_board)  == [[COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1]],
                                     [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1]],
                                     [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1]],
                                     [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1]],
                                     [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3]],
                                     [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3]],
                                     [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3]],
                                     [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3]]]
    assert flatten_board == [[COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1]],
                                     [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1]],
                                     [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1]],
                                     [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1]],
                                     [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3]],
                                     [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3]],
                                     [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3]],
                                     [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3]]]

def test_flatten_29() -> None:
    board = Block((0, 0), 750, COLOUR_LIST[1], 0, 0)
    copy_board = board.create_copy()

    assert id(copy_board) != id(board)
    flatten_board = _flatten(board)
    assert flatten_board == [[COLOUR_LIST[1]]]
    assert _flatten(copy_board)  == [[COLOUR_LIST[1]]]

def test_flatten_30() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 2)
    # Level 1
    colours = [COLOUR_LIST[3], None, COLOUR_LIST[0], None]
    set_children(board, colours)

    # Level 2
    colours1 = [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board.children[1], colours1)

    colours2 = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[2]]
    set_children(board.children[3], colours2)

    copy_board = board.create_copy()
    assert id(copy_board) != id(board)
    flatten_board = _flatten(board)

    assert flatten_board == [[COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[0]],
                             [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[0]],
                             [COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[1], COLOUR_LIST[3]],
                             [COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[0], COLOUR_LIST[2]]]
    assert _flatten(copy_board)  == [[COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[0]],
                             [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[0]],
                             [COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[1], COLOUR_LIST[3]],
                             [COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[0], COLOUR_LIST[2]]]

def test_flatten_31() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 2)
    # Level 1
    colours = [COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board, colours)
    copy_board = board.create_copy()
    assert id(copy_board) != id(board)
    flatten_board = _flatten(board)
    assert flatten_board == [[COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[0]],
                             [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[0]],
                             [COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[2]],
                             [COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[2]]]
    assert _flatten(copy_board) == [[COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[0]],
                             [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[0]],
                             [COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[2]],
                             [COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[2]]]

def test_flatten_32() -> None:
    # Level 0
    board = Block((0, 0), 750, COLOUR_LIST[2], 0, 2)
    copy_board = board.create_copy()
    assert id(copy_board) != id(board)
    flatten_board = _flatten(board)
    assert flatten_board == [[COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2]],
                             [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2]],
                             [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2]],
                             [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2]]]
    assert _flatten(copy_board) == [[COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2]],
                             [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2]],
                             [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2]],
                             [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[2]]]

def test_flatten_33() -> None:
    # Level 0
    board = Block((0, 0), 750, COLOUR_LIST[0], 0, 1)
    copy_board = board.create_copy()
    assert id(copy_board) != id(board)
    flatten_board = _flatten(board)
    assert flatten_board == [[COLOUR_LIST[0], COLOUR_LIST[0]],
                             [COLOUR_LIST[0], COLOUR_LIST[0]]]

def test_parimete_goal_34() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 2)
    # Level 1
    colours = [COLOUR_LIST[3], None, COLOUR_LIST[0], None]
    set_children(board, colours)

    # Level 2
    colours1 = [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board.children[1], colours1)

    colours2 = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[2]]
    set_children(board.children[3], colours2)

    goal_1 = PerimeterGoal(COLOUR_LIST[3])
    assert goal_1.score(board) == 5
    goal_2 = PerimeterGoal(COLOUR_LIST[0])
    assert goal_2.score(board) == 6
    goal_3 = PerimeterGoal(COLOUR_LIST[1])
    assert goal_3.score(board) == 1
    goal_4 = PerimeterGoal(COLOUR_LIST[2])
    assert goal_4.score(board) == 4

def test_parimete_goal_35() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 4)
    # Level 1
    colours = [COLOUR_LIST[3], None, COLOUR_LIST[0], None]
    set_children(board, colours)

    # Level 2
    colours1 = [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board.children[1], colours1)

    colours2 = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[3], None]
    set_children(board.children[3], colours2)

    # Level 3
    colours3 = [COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[0]]
    set_children(board.children[3].children[3], colours3)

    goal_1 = PerimeterGoal(COLOUR_LIST[0])
    assert goal_1.score(board) == 28
    goal_2 = PerimeterGoal(COLOUR_LIST[1])
    assert goal_2.score(board) == 6
    goal_3 = PerimeterGoal(COLOUR_LIST[2])
    assert goal_3.score(board) == 10
    goal_4 = PerimeterGoal(COLOUR_LIST[3])
    assert goal_4.score(board) == 20

def test_parimeter_goal_36() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 2)
    # Level 1
    colours = [COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board, colours)

    goal_1 = PerimeterGoal(COLOUR_LIST[0])
    assert goal_1.score(board) == 4
    goal_2 = PerimeterGoal(COLOUR_LIST[1])
    assert goal_2.score(board) == 0
    goal_3 = PerimeterGoal(COLOUR_LIST[2])
    assert goal_3.score(board) == 8
    goal_4 = PerimeterGoal(COLOUR_LIST[3])
    assert goal_4.score(board) == 4

def test_parimeter_goal_37() -> None:
    # Level 0
    board = Block((0, 0), 750, COLOUR_LIST[2], 0, 2)

    goal_1 = PerimeterGoal(COLOUR_LIST[0])
    assert goal_1.score(board) == 0
    goal_2 = PerimeterGoal(COLOUR_LIST[1])
    assert goal_2.score(board) == 0
    goal_3 = PerimeterGoal(COLOUR_LIST[2])
    assert goal_3.score(board) == 16
    goal_4 = PerimeterGoal(COLOUR_LIST[3])
    assert goal_4.score(board) == 0

def test_parimeter_goal_38() -> None:
    # Level 0
    board = Block((0, 0), 750, COLOUR_LIST[0], 0, 1)

    goal_1 = PerimeterGoal(COLOUR_LIST[0])
    assert goal_1.score(board) == 8
    goal_2 = PerimeterGoal(COLOUR_LIST[1])
    assert goal_2.score(board) == 0
    goal_3 = PerimeterGoal(COLOUR_LIST[2])
    assert goal_3.score(board) == 0
    goal_4 = PerimeterGoal(COLOUR_LIST[3])
    assert goal_4.score(board) == 0

def test_parimeter_goal_39() -> None:
    # Level 0
    board = Block((0, 0), 750, COLOUR_LIST[2], 0, 0)

    goal_1 = PerimeterGoal(COLOUR_LIST[0])
    assert goal_1.score(board) == 0
    goal_2 = PerimeterGoal(COLOUR_LIST[1])
    assert goal_2.score(board) == 0
    goal_3 = PerimeterGoal(COLOUR_LIST[2])
    assert goal_3.score(board) == 4
    goal_4 = PerimeterGoal(COLOUR_LIST[3])
    assert goal_4.score(board) == 0

# TODO: ~~~~~~   TASK 7   ~~~~~~     ~~~~~~   TASK 7   ~~~~~~     ~~~~~~   TASK 7   ~~~~~~

def test_blob_40() -> None:
    # Level 0
    board = Block((0, 0), 750, COLOUR_LIST[0], 0, 1)

    flatten_board_1 = _flatten(board)
    visited_1 = [[-1, -1], [-1, -1]]
    goal_1 = BlobGoal(COLOUR_LIST[0])
    assert goal_1._undiscovered_blob_size((3, 4), flatten_board_1, visited_1) == 0
    assert goal_1._undiscovered_blob_size((3, 2), flatten_board_1, visited_1) == 0
    assert goal_1._undiscovered_blob_size((0, 0), flatten_board_1, visited_1) == 4
    assert goal_1._undiscovered_blob_size((0, 1), flatten_board_1, visited_1) == 0
    assert goal_1._undiscovered_blob_size((1, 1), flatten_board_1, visited_1) == 0
    assert goal_1.score(board) == 4
    assert visited_1[0][0] == 1
    assert visited_1[0][1] == 1
    assert visited_1[1][0] == 1
    assert visited_1[1][1] == 1

    flatten_board_2 = _flatten(board)
    visited_2 = [[-1, -1], [-1, -1]]
    goal_2 = BlobGoal(COLOUR_LIST[1])
    assert goal_2._undiscovered_blob_size((3, 4), flatten_board_2, visited_2) == 0
    assert goal_2._undiscovered_blob_size((0, 0), flatten_board_2, visited_2) == 0
    assert goal_2._undiscovered_blob_size((9, 0), flatten_board_2, visited_2) == 0
    assert goal_2._undiscovered_blob_size((0, 1), flatten_board_1, visited_2) == 0
    assert goal_2._undiscovered_blob_size((1, 0), flatten_board_1, visited_2) == 0
    assert goal_2._undiscovered_blob_size((1, 1), flatten_board_1, visited_2) == 0
    assert goal_2._undiscovered_blob_size((0, 0), flatten_board_1, visited_2) == 0
    assert goal_2.score(board) == 0
    assert visited_2[0][0] == 0
    assert visited_2[1][0] == 0
    assert visited_2[0][1] == 0
    assert visited_2[1][1] == 0

    flatten_board_3 = _flatten(board)
    visited_3 = [[-1, -1], [-1, -1]]
    goal_3 = BlobGoal(COLOUR_LIST[2])
    assert goal_3._undiscovered_blob_size((3, 4), flatten_board_3, visited_3) == 0
    assert goal_3._undiscovered_blob_size((0, 0), flatten_board_3, visited_3) == 0
    assert goal_3._undiscovered_blob_size((2, -1), flatten_board_3, visited_3) == 0
    assert goal_3._undiscovered_blob_size((0, 0), flatten_board_1, visited_3) == 0
    assert goal_3._undiscovered_blob_size((0, 1), flatten_board_1, visited_3) == 0
    assert goal_3._undiscovered_blob_size((1, 0), flatten_board_1, visited_3) == 0
    assert goal_3._undiscovered_blob_size((1, 1), flatten_board_1, visited_3) == 0
    assert goal_3.score(board) == 0
    assert visited_3[0][0] == 0
    assert visited_3[0][1] == 0
    assert visited_3[1][1] == 0
    assert visited_3[1][0] == 0

    flatten_board_4 = _flatten(board)
    visited_4 = [[-1, -1], [-1, -1]]
    goal_4 = BlobGoal(COLOUR_LIST[3])
    assert goal_4._undiscovered_blob_size((3, 4), flatten_board_4, visited_4) == 0
    assert goal_4._undiscovered_blob_size((-2, 0), flatten_board_4, visited_4) == 0
    assert goal_4._undiscovered_blob_size((1, 0), flatten_board_4, visited_4) == 0
    assert goal_4._undiscovered_blob_size((0, 0), flatten_board_1, visited_4) == 0
    assert goal_4._undiscovered_blob_size((0, 1), flatten_board_1, visited_4) == 0
    assert goal_4._undiscovered_blob_size((1, 0), flatten_board_1, visited_4) == 0
    assert goal_4._undiscovered_blob_size((1, 1), flatten_board_1, visited_4) == 0
    assert goal_4.score(board) == 0
    assert visited_4[0][0] == 0
    assert visited_4[0][1] == 0
    assert visited_4[1][1] == 0
    assert visited_4[1][0] == 0

def test_blob_41() -> None:
    # Level 0
    board = Block((0, 0), 750, COLOUR_LIST[2], 0, 0)

    flatten_board_1 = _flatten(board)
    visited_1 = [[-1]]
    goal_1 = BlobGoal(COLOUR_LIST[0])
    assert goal_1._undiscovered_blob_size((3, 4), flatten_board_1, visited_1) == 0
    assert goal_1._undiscovered_blob_size((3, 2), flatten_board_1, visited_1) == 0
    assert goal_1._undiscovered_blob_size((0, 0), flatten_board_1, visited_1) == 0
    assert goal_1._undiscovered_blob_size((0, 1), flatten_board_1, visited_1) == 0
    assert goal_1._undiscovered_blob_size((1, 0), flatten_board_1, visited_1) == 0
    assert goal_1._undiscovered_blob_size((1, 1), flatten_board_1, visited_1) == 0
    assert goal_1.score(board) == 0
    assert visited_1[0][0] == 0

    flatten_board_2 = _flatten(board)
    visited_2 = [[-1]]
    goal_2 = BlobGoal(COLOUR_LIST[1])
    assert goal_2._undiscovered_blob_size((3, 4), flatten_board_2, visited_2) == 0
    assert goal_2._undiscovered_blob_size((-1, 2), flatten_board_2, visited_2) == 0
    assert goal_2._undiscovered_blob_size((0, 0), flatten_board_2, visited_2) == 0
    assert goal_2._undiscovered_blob_size((0, 1), flatten_board_2, visited_2) == 0
    assert goal_2._undiscovered_blob_size((1, 0), flatten_board_2, visited_2) == 0
    assert goal_2._undiscovered_blob_size((1, 1), flatten_board_2, visited_2) == 0
    assert goal_2.score(board) == 0
    assert visited_2[0][0] == 0

    flatten_board_3 = _flatten(board)
    visited_3 = [[-1]]
    goal_3 = BlobGoal(COLOUR_LIST[2])
    assert goal_3._undiscovered_blob_size((3, 4), flatten_board_3, visited_3) == 0
    assert goal_3._undiscovered_blob_size((-1, 2), flatten_board_3, visited_3) == 0
    assert goal_3._undiscovered_blob_size((0, 0), flatten_board_3, visited_3) == 1
    assert goal_3._undiscovered_blob_size((0, 1), flatten_board_3, visited_3) == 0
    assert goal_3._undiscovered_blob_size((1, 0), flatten_board_3, visited_3) == 0
    assert goal_3._undiscovered_blob_size((1, 1), flatten_board_3, visited_3) == 0
    assert goal_3.score(board) == 1
    assert visited_3[0][0] == 1

    flatten_board_3 = _flatten(board)
    visited_3 = [[-1]]
    goal_3 = BlobGoal(COLOUR_LIST[3])
    assert goal_3._undiscovered_blob_size((3, 4), flatten_board_3, visited_3) == 0
    assert goal_3._undiscovered_blob_size((-1, 2), flatten_board_3, visited_3) == 0
    assert goal_3._undiscovered_blob_size((0, 0), flatten_board_3, visited_3) == 0
    assert goal_3._undiscovered_blob_size((0, 1), flatten_board_3, visited_3) == 0
    assert goal_3._undiscovered_blob_size((1, 0), flatten_board_3, visited_3) == 0
    assert goal_3._undiscovered_blob_size((1, 1), flatten_board_3, visited_3) == 0
    assert goal_3.score(board) == 0
    assert visited_3[0][0] == 0

def test_blob_42() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 4)
    # Level 1
    colours = [COLOUR_LIST[3], None, COLOUR_LIST[0], None]
    set_children(board, colours)

    # Level 2
    colours1 = [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board.children[1], colours1)

    colours2 = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[3], None]
    set_children(board.children[3], colours2)

    # Level 3
    colours3 = [COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[0]]
    set_children(board.children[3].children[3], colours3)

    goal_0 = BlobGoal(COLOUR_LIST[0])
    assert goal_0.score(board) == 80

    goal_1 = BlobGoal(COLOUR_LIST[1])
    assert goal_1.score(board) == 16

    goal_2 = BlobGoal(COLOUR_LIST[2])
    assert goal_2.score(board) == 16

    goal_3 = BlobGoal(COLOUR_LIST[3])
    assert goal_3.score(board) == 64

def test_blob_43() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 2)
    # Level 1
    colours = [COLOUR_LIST[3], None, COLOUR_LIST[0], None]
    set_children(board, colours)

    # Level 2
    colours1 = [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board.children[1], colours1)

    colours2 = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[2]]
    set_children(board.children[3], colours2)


    goal_0 = BlobGoal(COLOUR_LIST[0])
    assert goal_0.score(board) == 5

    goal_1 = BlobGoal(COLOUR_LIST[1])
    assert goal_1.score(board) == 1

    goal_2 = BlobGoal(COLOUR_LIST[2])
    assert goal_2.score(board) == 1

    goal_3 = BlobGoal(COLOUR_LIST[3])
    assert goal_3.score(board) == 4

def test_blob_44() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 2)
    # Level 1
    colours = [COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[2]]
    set_children(board, colours)


    goal_0 = BlobGoal(COLOUR_LIST[0])
    assert goal_0.score(board) == 4

    goal_1 = BlobGoal(COLOUR_LIST[1])
    assert goal_1.score(board) == 0

    goal_2 = BlobGoal(COLOUR_LIST[2])
    assert goal_2.score(board) == 4

    goal_3 = BlobGoal(COLOUR_LIST[3])
    assert goal_3.score(board) == 4

def test_blob_45() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 3)
    # Level 1
    colours = [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[3]]
    set_children(board, colours)


    goal_0 = BlobGoal(COLOUR_LIST[0])
    assert goal_0.score(board) == 16

    goal_1 = BlobGoal(COLOUR_LIST[1])
    assert goal_1.score(board) == 0

    goal_2 = BlobGoal(COLOUR_LIST[2])
    assert goal_2.score(board) == 32

    goal_3 = BlobGoal(COLOUR_LIST[3])
    assert goal_3.score(board) == 16

def test_blob_46() -> None:
    # Level 0
    board = Block((0, 0), 750, None, 0, 4)
    # Level 1
    colours = [None, None, None, None]
    set_children(board, colours)

    # Level 2
    colours1 = [COLOUR_LIST[0], COLOUR_LIST[0], None, COLOUR_LIST[3]]
    set_children(board.children[0], colours1)
    colours_5 = [None, COLOUR_LIST[2], COLOUR_LIST[2], None]
    set_children(board.children[1], colours_5)
    colours_6 = [None, None, COLOUR_LIST[1], None]
    set_children(board.children[2], colours_6)
    colours_7 = [None, None, COLOUR_LIST[1], None]
    set_children(board.children[3], colours_7)

    # Level 3
    colours3 = [COLOUR_LIST[2], COLOUR_LIST[0], None, COLOUR_LIST[3]]
    set_children(board.children[0].children[2], colours3)
    colours_8 = [COLOUR_LIST[0], COLOUR_LIST[2], COLOUR_LIST[3], COLOUR_LIST[1]]
    set_children(board.children[1].children[0], colours_8)
    colours_9 = [None, COLOUR_LIST[2], COLOUR_LIST[3], COLOUR_LIST[1]]
    set_children(board.children[1].children[3], colours_9)
    colours_10 = [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board.children[2].children[0], colours_10)
    colours_11 = [COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[0]]
    set_children(board.children[2].children[1], colours_11)
    colours_12 = [COLOUR_LIST[2], COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[0]]
    set_children(board.children[2].children[3], colours_12)
    colours_13 = [COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[3]]
    set_children(board.children[3].children[0], colours_13)
    colours_14 = [COLOUR_LIST[3], None, COLOUR_LIST[1], COLOUR_LIST[0]]
    set_children(board.children[3].children[1], colours_14)
    colours_15 = [COLOUR_LIST[3], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board.children[3].children[3], colours_15)

    #level 4
    colours4 = [COLOUR_LIST[3], COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[0]]
    set_children(board.children[0].children[2].children[2], colours4)
    colours_16 = [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1]]
    set_children(board.children[1].children[3].children[0], colours_16)
    colours_17 = [COLOUR_LIST[0], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board.children[3].children[1].children[1], colours_17)

    goal_0 = BlobGoal(COLOUR_LIST[0])
    assert goal_0.score(board) == 44

    goal_1 = BlobGoal(COLOUR_LIST[1])
    assert goal_1.score(board) == 40

    goal_2 = BlobGoal(COLOUR_LIST[2])
    assert goal_2.score(board) == 49

    goal_3 = BlobGoal(COLOUR_LIST[3])
    assert goal_3.score(board) == 42

# TODO: ~~~~~~   TASK 8   ~~~~~~     ~~~~~~   TASK 8   ~~~~~~     ~~~~~~   TASK 8   ~~~~~~

def test_create_player_47() -> None:
    a = create_players(3, 2, [1, 3, 2])
    assert len(a) == 8
    assert a[0].id == 0
    assert a[4].id == 4
    assert a[7].id == 7
    assert isinstance(a[1], HumanPlayer)
    assert isinstance(a[2], HumanPlayer)
    assert isinstance(a[3], RandomPlayer)
    assert isinstance(a[5], SmartPlayer)
    assert isinstance(a[7], SmartPlayer)

def test_create_player_48() -> None:
    a = create_players(0, 0, [])
    assert len(a) == 0

def test_create_player_49() -> None:
    a = create_players(9, 10, [])
    assert len(a) == 19
    assert a[4].id == 4
    assert isinstance(a[4], HumanPlayer)
    assert isinstance(a[8], HumanPlayer)
    assert isinstance(a[9], RandomPlayer)

if __name__ == '__main__':
    pytest.main(['unit_test.py'])
