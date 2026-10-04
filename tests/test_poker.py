import importlib.util
from pathlib import Path

MODULE = Path(__file__).parents[1] / "src" / "poker_study.py"
spec = importlib.util.spec_from_file_location("poker_study", MODULE)
poker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poker)


def test_straight_flush():
    assert poker.five_card_rank(["Ah", "Kh", "Qh", "Jh", "Th"])[0] == 8


def test_quads():
    assert poker.five_card_rank(["As", "Ah", "Ad", "Ac", "Kd"])[0] == 7


def test_full_house():
    assert poker.five_card_rank(["As", "Ah", "Ad", "Kc", "Kd"])[0] == 6


def test_flush():
    assert poker.five_card_rank(["Ah", "Jh", "8h", "4h", "2h"])[0] == 5


def test_wheel_straight():
    rank = poker.five_card_rank(["As", "2h", "3d", "4c", "5d"])
    assert rank[0] == 4
    assert rank[1][0] == 5
