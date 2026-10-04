from __future__ import annotations

import itertools
import random
import tkinter as tk
from collections import Counter
from tkinter import ttk, messagebox

RANKS = "23456789TJQKA"
SUITS = "cdhs"
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANKS)}
SUIT_SYMBOL = {"c": "♣", "d": "♦", "h": "♥", "s": "♠"}
CATEGORY_NAMES = {
    8: "Стрит-флеш", 7: "Каре", 6: "Фулл-хаус", 5: "Флеш", 4: "Стрит",
    3: "Тройка", 2: "Две пары", 1: "Пара", 0: "Старшая карта",
}


def full_deck() -> list[str]:
    return [r + s for r in RANKS for s in SUITS]


def card_label(card: str) -> str:
    if not card:
        return "—"
    return f"{card[0]}{SUIT_SYMBOL[card[1]]}"


def five_card_rank(cards) -> tuple[int, tuple[int, ...]]:
    if len(cards) != 5:
        raise ValueError("five_card_rank expects exactly 5 cards")
    values = sorted((RANK_VALUE[c[0]] for c in cards), reverse=True)
    counts = Counter(values)
    groups = sorted(((cnt, val) for val, cnt in counts.items()), reverse=True)
    flush = len({c[1] for c in cards}) == 1
    unique = sorted(set(values), reverse=True)
    if 14 in unique:
        unique.append(1)
    straight_high = None
    for i in range(len(unique) - 4):
        window = unique[i:i + 5]
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
    if trips and (len(trips) >= 2 or pairs):
        return 6, (trips[0], trips[1] if len(trips) >= 2 else pairs[0])
    if flush:
        return 5, tuple(values)
    if straight_high:
        return 4, (straight_high,)
    if trips:
        kickers = sorted((v for v in values if v != trips[0]), reverse=True)[:2]
        return 3, (trips[0], *kickers)
    if len(pairs) >= 2:
        top, second = pairs[:2]
        return 2, (top, second, max(v for v in values if v not in (top, second)))
    if len(pairs) == 1:
        pair = pairs[0]
        kickers = sorted((v for v in values if v != pair), reverse=True)[:3]
        return 1, (pair, *kickers)
    return 0, tuple(values)


def best_rank(cards: list[str]) -> tuple[int, tuple[int, ...]]:
    if len(cards) < 5:
        raise ValueError("At least five cards are required")
    return max(five_card_rank(combo) for combo in itertools.combinations(cards, 5))


def category_name(cards: list[str]) -> str:
    if len(cards) < 5:
        return "Недостаточно карт для комбинации"
    return CATEGORY_NAMES[best_rank(cards)[0]]


def final_category_distribution(hero: list[str], board: list[str], simulations: int = 25000) -> dict[int, float]:
    known = hero + board
    if len(hero) != 2:
        raise ValueError("Choose exactly two hole cards")
    if len(set(known)) != len(known):
        raise ValueError("Cards must be unique")
    missing = 5 - len(board)
    if not 0 <= missing <= 5:
        raise ValueError("Board must have between 0 and 5 cards")
    deck = [c for c in full_deck() if c not in known]
    counts = Counter()
    exact_count = 1
    for i in range(missing):
        exact_count = exact_count * (len(deck) - i) // (i + 1)
    if exact_count <= 50000:
        outcomes = itertools.combinations(deck, missing)
        total = exact_count
    else:
        total = simulations
        outcomes = (tuple(random.sample(deck, missing)) for _ in range(simulations))
    for extra in outcomes:
        counts[best_rank(hero + board + list(extra))[0]] += 1
    return {cat: counts[cat] / total for cat in range(9)}


class PokerStudyApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Poker Study — Hand Trainer")
        self.geometry("980x690")
        self.minsize(900, 620)
        self.configure(bg="#11151b")
        self._setup_style()
        self.slots = []
        self._build_ui()
        self.random_deal()

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
        style.configure("Panel.TLabel", background="#1a212b", foreground="#f4f7fb", font=("Segoe UI", 11))
        style.configure("Big.TLabel", background="#1a212b", foreground="#f4f7fb", font=("Segoe UI", 20, "bold"))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("TCombobox", font=("Segoe UI", 14))

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=24)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Poker Study", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Учебный тренажёр комбинаций и вероятностей. Без ставок и подсказок для игры на деньги.", style="Sub.TLabel").pack(anchor="w", pady=(2, 18))
        cards_panel = ttk.Frame(root, style="Panel.TFrame", padding=18)
        cards_panel.pack(fill="x")
        ttk.Label(cards_panel, text="Ваши карты", style="Panel.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(cards_panel, text="Борд", style="Panel.TLabel").grid(row=0, column=3, columnspan=5, sticky="w", padx=(28, 0))
        choices = [""] + full_deck()
        for i in range(7):
            var = tk.StringVar()
            box = ttk.Combobox(cards_panel, textvariable=var, values=choices, width=5, state="readonly")
            col = i if i < 2 else i + 1
            box.grid(row=1, column=col, padx=(0 if i != 2 else 28, 8), pady=(8, 0))
            self.slots.append((var, box))
        buttons = ttk.Frame(root)
        buttons.pack(fill="x", pady=14)
        ttk.Button(buttons, text="Случайная раздача", command=self.random_deal).pack(side="left")
        ttk.Button(buttons, text="Проанализировать", command=self.analyze).pack(side="left", padx=8)
        ttk.Button(buttons, text="Очистить", command=self.clear_cards).pack(side="left")
        summary = ttk.Frame(root, style="Panel.TFrame", padding=18)
        summary.pack(fill="x", pady=(0, 14))
        self.hand_label = ttk.Label(summary, text="—", style="Big.TLabel")
        self.hand_label.pack(anchor="w")
        self.detail_label = ttk.Label(summary, text="Выберите две карты и карты борда.", style="Panel.TLabel")
        self.detail_label.pack(anchor="w", pady=(6, 0))
        odds_panel = ttk.Frame(root, style="Panel.TFrame", padding=18)
        odds_panel.pack(fill="both", expand=True)
        ttk.Label(odds_panel, text="Вероятность итоговой комбинации к риверу", style="Panel.TLabel").pack(anchor="w")
        self.tree = ttk.Treeview(odds_panel, columns=("combo", "chance"), show="headings", height=9)
        self.tree.heading("combo", text="Комбинация")
        self.tree.heading("chance", text="Вероятность")
        self.tree.column("combo", width=280, anchor="w")
        self.tree.column("chance", width=160, anchor="e")
        self.tree.pack(fill="both", expand=True, pady=(10, 0))
        ttk.Label(root, text="Расчёт предназначен для обучения теории вероятностей и распознавания комбинаций.", style="Sub.TLabel").pack(anchor="w", pady=(12, 0))

    def current_cards(self):
        hero = [self.slots[i][0].get() for i in range(2)]
        board = [self.slots[i][0].get() for i in range(2, 7)]
        return [c for c in hero if c], [c for c in board if c]

    def random_deal(self) -> None:
        cards = random.sample(full_deck(), 7)
        for i, slot in enumerate(self.slots):
            slot[0].set(cards[i] if i < 5 else "")
        self.analyze()

    def clear_cards(self) -> None:
        for var, _ in self.slots:
            var.set("")
        self.hand_label.config(text="—")
        self.detail_label.config(text="Выберите две карты и карты борда.")
        for item in self.tree.get_children():
            self.tree.delete(item)

    def analyze(self) -> None:
        hero, board = self.current_cards()
        known = hero + board
        if len(hero) != 2:
            messagebox.showinfo("Poker Study", "Выберите ровно две карманные карты.")
            return
        if len(set(known)) != len(known):
            messagebox.showerror("Poker Study", "Одна и та же карта выбрана несколько раз.")
            return
        if len(board) < 3:
            self.hand_label.config(text="До флопа")
            self.detail_label.config(text="Вероятности рассчитываются симуляцией; добавьте флоп для точного перебора.")
        else:
            self.hand_label.config(text=category_name(known))
            self.detail_label.config(text=f"Карты: {' '.join(card_label(c) for c in hero)}   |   Борд: {' '.join(card_label(c) for c in board)}")
        try:
            distribution = final_category_distribution(hero, board)
        except ValueError as exc:
            messagebox.showerror("Poker Study", str(exc))
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for cat in range(8, -1, -1):
            chance = distribution.get(cat, 0.0)
            if chance > 0.00005:
                self.tree.insert("", "end", values=(CATEGORY_NAMES[cat], f"{chance * 100:.2f}%"))


def main() -> None:
    PokerStudyApp().mainloop()


if __name__ == "__main__":
    main()
