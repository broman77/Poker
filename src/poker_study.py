from __future__ import annotations

import random
import tkinter as tk
from collections import Counter
from tkinter import ttk

RANKS = "23456789TJQKA"
SUITS = "cdhs"
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANKS)}
SUIT_SYMBOL = {"c": "♣", "d": "♦", "h": "♥", "s": "♠"}
CATEGORY_NAMES = {
    8: "Стрит-флеш",
    7: "Каре",
    6: "Фулл-хаус",
    5: "Флеш",
    4: "Стрит",
    3: "Тройка",
    2: "Две пары",
    1: "Пара",
    0: "Старшая карта",
}


def full_deck() -> list[str]:
    return [r + s for r in RANKS for s in SUITS]


def card_label(card: str) -> str:
    return f"{card[0]}{SUIT_SYMBOL[card[1]]}"


def five_card_rank(cards: list[str] | tuple[str, ...]) -> tuple[int, tuple[int, ...]]:
    if len(cards) != 5:
        raise ValueError("Нужно ровно 5 карт")
    if len(set(cards)) != 5:
        raise ValueError("Карты не должны повторяться")

    values = sorted((RANK_VALUE[c[0]] for c in cards), reverse=True)
    counts = Counter(values)
    groups = sorted(((cnt, val) for val, cnt in counts.items()), reverse=True)
    flush = len({c[1] for c in cards}) == 1

    unique = sorted(set(values), reverse=True)
    if 14 in unique:
        unique.append(1)
    straight_high = None
    for i in range(len(unique) - 4):
        window = unique[i : i + 5]
        if window[0] - window[4] == 4:
            straight_high = window[0]
            break

    if flush and straight_high:
        return 8, (straight_high,)
    fours = [val for cnt, val in groups if cnt == 4]
    if fours:
        four = fours[0]
        return 7, (four, max(v for v in values if v != four))
    trips = sorted((val for cnt, val in groups if cnt == 3), reverse=True)
    pairs = sorted((val for cnt, val in groups if cnt == 2), reverse=True)
    if trips and pairs:
        return 6, (trips[0], pairs[0])
    if flush:
        return 5, tuple(values)
    if straight_high:
        return 4, (straight_high,)
    if trips:
        kickers = sorted((v for v in values if v != trips[0]), reverse=True)[:2]
        return 3, (trips[0], *kickers)
    if len(pairs) >= 2:
        top, second = pairs[:2]
        kicker = max(v for v in values if v not in (top, second))
        return 2, (top, second, kicker)
    if len(pairs) == 1:
        pair = pairs[0]
        kickers = sorted((v for v in values if v != pair), reverse=True)[:3]
        return 1, (pair, *kickers)
    return 0, tuple(values)


def category_name(cards: list[str]) -> str:
    return CATEGORY_NAMES[five_card_rank(cards)[0]]


class PokerStudyApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Poker Study — Combination Quiz")
        self.geometry("900x560")
        self.minsize(820, 520)
        self.configure(bg="#11151b")
        self.current_hand: list[str] = []
        self._setup_style()
        self._build_ui()
        self.new_hand()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#11151b")
        style.configure("Panel.TFrame", background="#1a212b")
        style.configure("Title.TLabel", background="#11151b", foreground="#f4f7fb", font=("Segoe UI", 24, "bold"))
        style.configure("Sub.TLabel", background="#11151b", foreground="#9ba8b8", font=("Segoe UI", 10))
        style.configure("Card.TLabel", background="#1a212b", foreground="#f4f7fb", font=("Segoe UI Symbol", 30, "bold"), padding=14)
        style.configure("Answer.TLabel", background="#1a212b", foreground="#f4f7fb", font=("Segoe UI", 22, "bold"))
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=10)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=28)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="Poker Study", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Учебный тренажёр распознавания 5-карточных комбинаций.", style="Sub.TLabel").pack(anchor="w", pady=(2, 22))

        panel = ttk.Frame(root, style="Panel.TFrame", padding=24)
        panel.pack(fill="both", expand=True)
        ttk.Label(panel, text="Назови комбинацию:", style="Answer.TLabel").pack(anchor="center", pady=(0, 18))

        self.cards_row = ttk.Frame(panel, style="Panel.TFrame")
        self.cards_row.pack(pady=10)
        self.card_labels: list[ttk.Label] = []
        for _ in range(5):
            label = ttk.Label(self.cards_row, text="--", style="Card.TLabel")
            label.pack(side="left", padx=6)
            self.card_labels.append(label)

        self.answer = ttk.Label(panel, text="Ответ скрыт", style="Answer.TLabel")
        self.answer.pack(pady=(26, 14))

        buttons = ttk.Frame(panel, style="Panel.TFrame")
        buttons.pack()
        ttk.Button(buttons, text="Показать ответ", command=self.show_answer).pack(side="left", padx=6)
        ttk.Button(buttons, text="Новая рука", command=self.new_hand).pack(side="left", padx=6)

        ttk.Label(root, text="Только изучение комбинаций: без ставок, игровых советов, анализа соперников и расчёта шансов конкретной раздачи.", style="Sub.TLabel").pack(anchor="w", pady=(16, 0))

    def new_hand(self) -> None:
        self.current_hand = random.sample(full_deck(), 5)
        for label, card in zip(self.card_labels, self.current_hand):
            label.config(text=card_label(card))
        self.answer.config(text="Ответ скрыт")

    def show_answer(self) -> None:
        self.answer.config(text=category_name(self.current_hand))


def main() -> None:
    PokerStudyApp().mainloop()


if __name__ == "__main__":
    main()
