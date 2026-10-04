package com.broman77.pokerstudy;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

public final class PokerEngine {
    public static final String[] CATEGORY_NAMES = {
            "Старшая карта", "Пара", "Две пары", "Тройка", "Стрит",
            "Флеш", "Фулл-хаус", "Каре", "Стрит-флеш"
    };

    private PokerEngine() {}

    public static List<String> fullDeck() {
        String ranks = "23456789TJQKA";
        String suits = "SHDC";
        List<String> deck = new ArrayList<>(52);
        for (int r = 0; r < ranks.length(); r++) {
            for (int s = 0; s < suits.length(); s++) {
                deck.add("" + ranks.charAt(r) + suits.charAt(s));
            }
        }
        return deck;
    }

    public static int evaluateBest(List<String> cards) {
        if (cards.size() < 5) throw new IllegalArgumentException("Нужно минимум 5 карт");
        int best = -1;
        for (int a = 0; a < cards.size() - 4; a++) {
            for (int b = a + 1; b < cards.size() - 3; b++) {
                for (int c = b + 1; c < cards.size() - 2; c++) {
                    for (int d = c + 1; d < cards.size() - 1; d++) {
                        for (int e = d + 1; e < cards.size(); e++) {
                            List<String> five = new ArrayList<>(5);
                            five.add(cards.get(a)); five.add(cards.get(b)); five.add(cards.get(c));
                            five.add(cards.get(d)); five.add(cards.get(e));
                            best = Math.max(best, evaluateFive(five));
                        }
                    }
                }
            }
        }
        return best;
    }

    private static int evaluateFive(List<String> cards) {
        Map<Integer, Integer> counts = new HashMap<>();
        Set<Integer> unique = new HashSet<>();
        char suit0 = cards.get(0).charAt(1);
        boolean flush = true;

        for (String card : cards) {
            int rank = rankValue(card.charAt(0));
            counts.put(rank, counts.getOrDefault(rank, 0) + 1);
            unique.add(rank);
            if (card.charAt(1) != suit0) flush = false;
        }

        boolean straight = isStraight(unique);
        if (straight && flush) return 8;
        if (counts.containsValue(4)) return 7;
        if (counts.containsValue(3) && counts.containsValue(2)) return 6;
        if (flush) return 5;
        if (straight) return 4;
        if (counts.containsValue(3)) return 3;

        int pairs = 0;
        for (int n : counts.values()) if (n == 2) pairs++;
        if (pairs == 2) return 2;
        if (pairs == 1) return 1;
        return 0;
    }

    private static boolean isStraight(Set<Integer> unique) {
        if (unique.size() != 5) return false;
        List<Integer> values = new ArrayList<>(unique);
        Collections.sort(values);
        if (values.get(4) - values.get(0) == 4) return true;
        return values.equals(java.util.Arrays.asList(2, 3, 4, 5, 14));
    }

    private static int rankValue(char rank) {
        String ranks = "--23456789TJQKA";
        int idx = ranks.indexOf(rank);
        if (idx < 2) throw new IllegalArgumentException("Неизвестный ранг: " + rank);
        return idx;
    }

    public static long[] finalHandDistribution(List<String> hole, List<String> board, int monteCarloIterations) {
        if (hole.size() != 2) throw new IllegalArgumentException("Нужно выбрать две карманные карты");
        if (!(board.size() == 0 || board.size() == 3 || board.size() == 4 || board.size() == 5)) {
            throw new IllegalArgumentException("Борд должен содержать 0, 3, 4 или 5 карт");
        }

        Set<String> used = new HashSet<>();
        used.addAll(hole);
        used.addAll(board);
        if (used.size() != hole.size() + board.size()) {
            throw new IllegalArgumentException("Одна и та же карта выбрана дважды");
        }

        List<String> remaining = fullDeck();
        remaining.removeAll(used);
        int missing = 5 - board.size();
        long[] counts = new long[9];

        if (missing == 0) {
            List<String> all = new ArrayList<>(hole);
            all.addAll(board);
            counts[evaluateBest(all)] = 1;
            return counts;
        }

        if (missing == 1) {
            for (String x : remaining) {
                List<String> all = new ArrayList<>(hole);
                all.addAll(board);
                all.add(x);
                counts[evaluateBest(all)]++;
            }
            return counts;
        }

        if (missing == 2) {
            for (int i = 0; i < remaining.size() - 1; i++) {
                for (int j = i + 1; j < remaining.size(); j++) {
                    List<String> all = new ArrayList<>(hole);
                    all.addAll(board);
                    all.add(remaining.get(i));
                    all.add(remaining.get(j));
                    counts[evaluateBest(all)]++;
                }
            }
            return counts;
        }

        int iterations = Math.max(5000, monteCarloIterations);
        Random random = new Random();
        for (int n = 0; n < iterations; n++) {
            List<String> sample = new ArrayList<>(remaining);
            Collections.shuffle(sample, random);
            List<String> all = new ArrayList<>(hole);
            all.addAll(board);
            for (int k = 0; k < missing; k++) all.add(sample.get(k));
            counts[evaluateBest(all)]++;
        }
        return counts;
    }

    public static long sum(long[] values) {
        long s = 0;
        for (long v : values) s += v;
        return s;
    }
}
