import importlib.util
from pathlib import Path

MODULE = Path(__file__).parents[1] / "src" / "poker_study.py"
spec = importlib.util.spec_from_file_location("poker_study", MODULE)
poker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poker)


def test_royal_straight_flush():
    cards = ["Ah", "Kh", "Qh", "Jh", "Th", "2c", "3d"]
    assert poker.best_rank(cards)[0] == 8


def test_quads():
    cards = ["As", "Ah", "Ad", "Ac", "Kd", "2c", "3h"]
    assert poker.best_rank(cards)[0] == 7


def test_full_house():
    cards = ["As", "Ah", "Ad", "Kc", "Kd", "2c", "3h"]
    assert poker.best_rank(cards)[0] == 6


def test_wheel_straight():
    cards = ["As", "2h", "3d", "4c", "5d", "Kh", "Qs"]
    rank = poker.best_rank(cards)
    assert rank[0] == 4
    assert rank[1][0] == 5


def test_distribution_complete_board():
    hero = ["Ah", "Kh"]
    board = ["Qh", "Jh", "Th", "2c", "3d"]
    dist = poker.final_category_distribution(hero, board)
    assert dist[8] == 1.0
