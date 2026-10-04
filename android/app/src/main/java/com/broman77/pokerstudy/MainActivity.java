package com.broman77.pokerstudy;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

public class MainActivity extends Activity {
    private final List<Spinner> slots = new ArrayList<>();
    private final List<String> cardCodes = new ArrayList<>();
    private final List<String> cardLabels = new ArrayList<>();
    private TextView resultView;
    private Button analyzeButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildCardLists();
        setContentView(buildUi());
        randomExample();
    }

    private View buildUi() {
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(Color.rgb(244, 246, 248));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(18), dp(22), dp(18), dp(28));
        scroll.addView(root);

        TextView title = text("Poker Study", 30, Color.rgb(22, 35, 47));
        title.setGravity(Gravity.CENTER_HORIZONTAL);
        root.addView(title, matchWrap());

        TextView subtitle = text("Android · тренажёр учебных и завершённых раздач", 15, Color.DKGRAY);
        subtitle.setGravity(Gravity.CENTER_HORIZONTAL);
        subtitle.setPadding(0, dp(4), 0, dp(18));
        root.addView(subtitle, matchWrap());

        TextView notice = text("Работает офлайн. Не подключается к покер-румам и не даёт рекомендаций по ставкам.", 14, Color.rgb(45, 71, 86));
        notice.setBackgroundColor(Color.rgb(226, 237, 243));
        notice.setPadding(dp(14), dp(12), dp(14), dp(12));
        root.addView(notice, matchWrap());

        TextView holeHeader = section("Карманные карты");
        root.addView(holeHeader, matchWrap());
        root.addView(spinnerRow("Карта 1", 0), matchWrap());
        root.addView(spinnerRow("Карта 2", 1), matchWrap());

        TextView boardHeader = section("Борд");
        root.addView(boardHeader, matchWrap());
        root.addView(spinnerRow("Флоп 1", 2), matchWrap());
        root.addView(spinnerRow("Флоп 2", 3), matchWrap());
        root.addView(spinnerRow("Флоп 3", 4), matchWrap());
        root.addView(spinnerRow("Тёрн", 5), matchWrap());
        root.addView(spinnerRow("Ривер", 6), matchWrap());

        analyzeButton = button("Рассчитать комбинации");
        analyzeButton.setOnClickListener(v -> analyze());
        root.addView(analyzeButton, buttonParams());

        Button random = button("Случайный учебный флоп");
        random.setOnClickListener(v -> randomExample());
        root.addView(random, buttonParams());

        Button reset = button("Очистить");
        reset.setOnClickListener(v -> resetCards());
        root.addView(reset, buttonParams());

        resultView = text("Выбери карты и нажми «Рассчитать комбинации».", 16, Color.rgb(27, 42, 53));
        resultView.setPadding(dp(14), dp(16), dp(14), dp(16));
        resultView.setBackgroundColor(Color.WHITE);
        root.addView(resultView, matchWrap());

        TextView footer = text("Вероятности показывают, какая твоя итоговая комбинация получится к риверу. На флопе и тёрне используется точный перебор; до флопа — Monte Carlo.", 13, Color.GRAY);
        footer.setPadding(0, dp(14), 0, 0);
        root.addView(footer, matchWrap());
        return scroll;
    }

    private LinearLayout spinnerRow(String name, int index) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setPadding(0, dp(3), 0, dp(3));

        TextView label = text(name, 15, Color.rgb(32, 46, 58));
        row.addView(label, new LinearLayout.LayoutParams(0, dp(50), 1f));

        Spinner spinner = new Spinner(this);
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, cardLabels);
        spinner.setAdapter(adapter);
        slots.add(spinner);
        row.addView(spinner, new LinearLayout.LayoutParams(0, dp(50), 1.25f));
        return row;
    }

    private void buildCardLists() {
        cardCodes.add("");
        cardLabels.add("—");
        String ranks = "23456789TJQKA";
        String suits = "SHDC";
        for (int r = ranks.length() - 1; r >= 0; r--) {
            for (int s = 0; s < suits.length(); s++) {
                String code = "" + ranks.charAt(r) + suits.charAt(s);
                cardCodes.add(code);
                cardLabels.add(prettyCard(code));
            }
        }
    }

    private String prettyCard(String code) {
        String rank = code.substring(0, 1).replace("T", "10");
        char suit = code.charAt(1);
        String symbol = suit == 'S' ? "♠" : suit == 'H' ? "♥" : suit == 'D' ? "♦" : "♣";
        return rank + symbol;
    }

    private void analyze() {
        final List<String> hole;
        final List<String> board;
        try {
            hole = readHole();
            board = readBoard();
            validateUnique(hole, board);
        } catch (IllegalArgumentException ex) {
            Toast.makeText(this, ex.getMessage(), Toast.LENGTH_LONG).show();
            return;
        }

        analyzeButton.setEnabled(false);
        resultView.setText("Считаю вероятности…");
        new Thread(() -> {
            try {
                long[] dist = PokerEngine.finalHandDistribution(hole, board, 30000);
                String report = buildReport(hole, board, dist);
                runOnUiThread(() -> {
                    resultView.setText(report);
                    analyzeButton.setEnabled(true);
                });
            } catch (Exception ex) {
                runOnUiThread(() -> {
                    resultView.setText("Ошибка: " + ex.getMessage());
                    analyzeButton.setEnabled(true);
                });
            }
        }).start();
    }

    private String buildReport(List<String> hole, List<String> board, long[] dist) {
        StringBuilder sb = new StringBuilder();
        List<String> known = new ArrayList<>(hole);
        known.addAll(board);

        sb.append("Карманные: ").append(prettyCard(hole.get(0))).append("  ").append(prettyCard(hole.get(1))).append("\n");
        if (!board.isEmpty()) {
            sb.append("Борд: ");
            for (String c : board) sb.append(prettyCard(c)).append("  ");
            sb.append("\n");
        }

        if (known.size() >= 5) {
            int current = PokerEngine.evaluateBest(known);
            sb.append("\nТекущая комбинация: ").append(PokerEngine.CATEGORY_NAMES[current]).append("\n");
        } else {
            sb.append("\nТекущая комбинация определяется после появления флопа.\n");
        }

        long total = PokerEngine.sum(dist);
        sb.append("\nИтог к риверу:\n");
        for (int i = PokerEngine.CATEGORY_NAMES.length - 1; i >= 0; i--) {
            if (dist[i] == 0) continue;
            double pct = dist[i] * 100.0 / total;
            sb.append(String.format(Locale.US, "%-16s %6.2f%%\n", PokerEngine.CATEGORY_NAMES[i], pct));
        }
        sb.append("\nМетод: ").append(board.size() >= 3 ? "точный перебор" : "Monte Carlo (30 000 симуляций)");
        return sb.toString();
    }

    private List<String> readHole() {
        List<String> hole = new ArrayList<>();
        String a = selected(slots.get(0));
        String b = selected(slots.get(1));
        if (a == null || b == null) throw new IllegalArgumentException("Выбери обе карманные карты");
        hole.add(a); hole.add(b);
        return hole;
    }

    private List<String> readBoard() {
        String f1 = selected(slots.get(2));
        String f2 = selected(slots.get(3));
        String f3 = selected(slots.get(4));
        String turn = selected(slots.get(5));
        String river = selected(slots.get(6));

        boolean anyFlop = f1 != null || f2 != null || f3 != null;
        boolean fullFlop = f1 != null && f2 != null && f3 != null;
        if (anyFlop && !fullFlop) throw new IllegalArgumentException("Для флопа выбери все три карты");
        if (turn != null && !fullFlop) throw new IllegalArgumentException("Тёрн можно добавить только после полного флопа");
        if (river != null && turn == null) throw new IllegalArgumentException("Ривер можно добавить только после тёрна");

        List<String> board = new ArrayList<>();
        if (fullFlop) { board.add(f1); board.add(f2); board.add(f3); }
        if (turn != null) board.add(turn);
        if (river != null) board.add(river);
        return board;
    }

    private void validateUnique(List<String> hole, List<String> board) {
        List<String> all = new ArrayList<>(hole);
        all.addAll(board);
        if (new java.util.HashSet<>(all).size() != all.size()) {
            throw new IllegalArgumentException("Одна и та же карта выбрана несколько раз");
        }
    }

    private String selected(Spinner spinner) {
        int p = spinner.getSelectedItemPosition();
        return p <= 0 ? null : cardCodes.get(p);
    }

    private void randomExample() {
        List<String> deck = PokerEngine.fullDeck();
        Collections.shuffle(deck);
        resetCards();
        for (int i = 0; i < 5; i++) selectCode(slots.get(i), deck.get(i));
        resultView.setText("Случайный учебный флоп готов. Нажми «Рассчитать комбинации».");
    }

    private void resetCards() {
        for (Spinner spinner : slots) spinner.setSelection(0);
        if (resultView != null) resultView.setText("Выбери карты и нажми «Рассчитать комбинации».");
    }

    private void selectCode(Spinner spinner, String code) {
        int idx = cardCodes.indexOf(code);
        if (idx >= 0) spinner.setSelection(idx);
    }

    private TextView section(String value) {
        TextView t = text(value, 19, Color.rgb(20, 83, 104));
        t.setPadding(0, dp(20), 0, dp(6));
        return t;
    }

    private TextView text(String value, int sp, int color) {
        TextView t = new TextView(this);
        t.setText(value);
        t.setTextSize(sp);
        t.setTextColor(color);
        return t;
    }

    private Button button(String value) {
        Button b = new Button(this);
        b.setText(value);
        b.setAllCaps(false);
        return b;
    }

    private LinearLayout.LayoutParams matchWrap() {
        return new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
    }

    private LinearLayout.LayoutParams buttonParams() {
        LinearLayout.LayoutParams p = matchWrap();
        p.setMargins(0, dp(8), 0, 0);
        return p;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
