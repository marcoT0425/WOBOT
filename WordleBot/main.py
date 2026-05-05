import sys
import os
import random
from functools import lru_cache

# --- PDF ENGINE IMPORTS ---
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors

    HAS_PDF = True
except ImportError:
    HAS_PDF = False

# --- 1. DATA LOADING ---
proper_word, word_list, full_dictionary = [], [], []


def load_data():
    global proper_word, word_list, full_dictionary
    try:
        with open("proper word.txt", "r", encoding="utf-8") as f:
            proper_word = [line.strip().lower() for line in f if len(line.strip()) == 5]
        with open("word list.txt", "r", encoding="utf-8") as f:
            word_list = [line.strip().lower() for line in f if len(line.strip()) == 5]
        full_dictionary = list(set(proper_word + word_list))
    except FileNotFoundError:
        sys.exit("CRITICAL ERROR: Dictionary files missing.")


# --- 2. CORE PATTERN ENGINE ---
@lru_cache(maxsize=None)
def get_feedback(secret, guess):
    if secret == guess: return "ggggg"
    res, s_list, g_list = ['_'] * 5, list(secret), list(guess)
    for i in range(5):
        if g_list[i] == s_list[i]:
            res[i] = 'g'
            s_list[i] = g_list[i] = None
    for i in range(5):
        if g_list[i] is not None:
            char = g_list[i]
            for j in range(5):
                if s_list[j] == char:
                    res[i] = 'y'
                    s_list[j] = None
                    break
    return "".join(res)


def get_color_terminal(word, pattern):
    bg_green = "\033[48;2;83;141;78m"
    bg_yellow = "\033[48;2;181;159;59m"
    bg_gray = "\033[48;2;58;58;60m"
    text_white = "\033[1;97m"
    reset = "\033[0m"
    colored_word = ""
    for char, p in zip(word.upper(), pattern):
        if p == 'g':
            colored_word += f"{bg_green}{text_white} {char} {reset}"
        elif p == 'y':
            colored_word += f"{bg_yellow}{text_white} {char} {reset}"
        else:
            colored_word += f"{bg_gray}{text_white} {char} {reset}"
    return colored_word


# --- 3. PDF TREE LOGIC ---
def generate_tree_pdf(start_word, results_dict):
    if not HAS_PDF: return
    p_map = {'_': 0, 'y': 1, 'g': 2}
    sorted_targets = sorted(results_dict.keys(),
                            key=lambda t: [[p_map.get(c) for c in step[1]] for step in results_dict[t]])
    c = canvas.Canvas(f"{start_word.upper()}_Answer_tree.pdf", pagesize=A4)
    w, h = A4
    y, box, margin = h - 80, 10, 1.5
    word_w, col_w = (box + margin) * 5, (box + margin) * 5 + 35
    colors_map = {'g': colors.HexColor("#538d4e"), 'y': colors.HexColor("#b59f3b"), '_': colors.HexColor("#3a3a3c")}
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, h - 40, f"WORDLE DECISION TREE: {start_word.upper()}")
    prev_h = None
    for target in sorted_targets:
        if y < 50:
            c.showPage()
            y = h - 60
            prev_h = None
        history, x = results_dict[target], 40
        for i, (word, pattern) in enumerate(history):
            is_rep = prev_h and i < len(prev_h) and prev_h[i] == (word, pattern)
            if is_rep:
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(x + word_w / 2, y + 2, "↓")
            else:
                for ci, pc in enumerate(pattern):
                    bx = x + (ci * (box + margin))
                    c.setFillColor(colors_map.get(pc, colors.gray))
                    c.rect(bx, y, box, box, stroke=0, fill=1)
                    c.setFillColor(colors.white)
                    c.setFont("Helvetica", 7)
                    c.drawCentredString(bx + box / 2, y + 2.5, word[ci].upper())
            if i < len(history) - 1:
                arrow = "↓" if prev_h and i + 1 < len(prev_h) and history[i] == prev_h[i] and history[i + 1] == prev_h[
                    i + 1] else "→"
                if is_rep and not (prev_h and i + 1 < len(prev_h) and prev_h[i + 1] == history[i + 1]): arrow = "→"
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(x + word_w + 15, y + 2, arrow)
            x += col_w
        prev_h, y = history, y - 18
    c.save()


# --- 4. CORE ANALYTICS ---
tree_memory = {}


def is_hard_mode_valid(guess, prev_guess, pattern):
    if not prev_guess or not pattern: return True
    for i, p in enumerate(pattern):
        if p == "g" and guess[i] != prev_guess[i]: return False
    required_counts = {}
    for i, p in enumerate(pattern):
        if p in ("g", "y"):
            char = prev_guess[i]
            required_counts[char] = required_counts.get(char, 0) + 1
    for char, count in required_counts.items():
        if guess.count(char) < count: return False
    return True


def get_entropy_score(word, pool, hard_flag):
    groups = {}
    for secret in pool:
        p = get_feedback(secret, word)
        groups[p] = groups.get(p, 0) + 1
    score = len(groups) - (sum(v * v for v in groups.values()) / 100000)
    if word in pool: score += 0.000001 if hard_flag else 0.4
    return score


def get_best_move(pool, is_hard, prev_guess, last_p, history_tuple):
    cache_key = (history_tuple, is_hard)
    if cache_key in tree_memory: return tree_memory[cache_key]
    if len(pool) <= 2: return pool[0]
    candidates = full_dictionary
    if is_hard: candidates = [c for c in full_dictionary if is_hard_mode_valid(c, prev_guess, last_p)]

    best_word, best_score = None, -1
    for cand in candidates:
        score = get_entropy_score(cand, pool, is_hard)
        if score > best_score: best_score, best_word = score, cand
    tree_memory[cache_key] = best_word
    return best_word


def calculate_analytics(candidate, is_hard, pool, turn, history):
    total_turns, missed, stats = 0, [], [0] * 7
    max_turn_achieved = 0

    for secret in pool:
        s_p, s_g, s_t, s_hist = list(pool), candidate, turn, list(history)
        while s_t <= 6:
            p = get_feedback(secret, s_g)
            s_hist.append((s_g, p))
            if p == "ggggg":
                total_turns += s_t
                stats[s_t - 1] += 1
                if s_t > max_turn_achieved: max_turn_achieved = s_t
                break

            s_p = [w for w in s_p if get_feedback(w, s_g) == p]
            if not s_p: break
            if len(s_p) == 1:
                res_t = s_t + 1
                if res_t > 6:
                    missed.append(secret);
                    total_turns += 7;
                    stats[6] += 1
                    max_turn_achieved = 7
                else:
                    total_turns += res_t;
                    stats[res_t - 1] += 1
                    if res_t > max_turn_achieved: max_turn_achieved = res_t
                break

            s_t += 1
            if s_t > 6:
                missed.append(secret);
                total_turns += 7;
                stats[6] += 1
                max_turn_achieved = 7
                break
            s_g = get_best_move(tuple(s_p), is_hard, s_g, p, tuple(s_hist))

    win_p = (len(pool) - len(missed)) / len(pool) * 100 if pool else 0
    avg_exp = total_turns / len(pool) if pool else 0
    entropy = get_entropy_score(candidate, pool, is_hard)
    return win_p, avg_exp, max_turn_achieved, missed, stats, (candidate in pool), entropy


def get_share_stats(turns, history):
    emoji_map = {'g': '🟩', 'y': '🟨', '_': '⬛'}
    grid = ""
    for _, p in history:
        grid += "".join(emoji_map[c] for c in p) + "\n"
    score = "X" if turns > 6 else turns
    return f"WOBOT {score}/6\n\n{grid}"


# --- 5. EXECUTION ---
def run_game(mode, hard, limit, start_word, target=None):
    pool, turn, history = proper_word.copy(), 0, []
    solve_path_plain, solve_path_colored, full_history = [], [], []
    current_guess = start_word
    user_manual_guess = None

    while turn < 6:
        turn += 1
        if mode in [2, 3, 4]:
            p = get_feedback(target, current_guess)
        else:
            while True:
                user_input = input(f"\nPattern for '{current_guess.upper()}': ").lower().strip()
                raw = user_input.split()
                if not raw: continue
                if len(raw) > 1:
                    user_manual_guess = raw[0].lower()
                    p = raw[1]
                else:
                    user_manual_guess = None
                    p = raw[0]
                if len(p) == 5 and all(c in 'gy_' for c in p): break

        final_word_used = user_manual_guess if user_manual_guess else current_guess
        solve_path_plain.append(final_word_used)
        solve_path_colored.append(get_color_terminal(final_word_used, p))
        full_history.append((final_word_used, p))
        if p == "ggggg": break

        pool = [w for w in pool if get_feedback(w, final_word_used) == p]
        history.append((final_word_used, p))

        if turn < 6:
            active_pool = full_dictionary if not hard else [c for c in full_dictionary if
                                                            is_hard_mode_valid(c, final_word_used, p)]

            if mode == 1:
                print(f"\nCandidates left: {len(pool)}")
                print(f"Theoretical Analysis of Top {limit}...")

            entropy_list = [(w, get_entropy_score(w, pool, hard)) for w in active_pool]
            entropy_list.sort(key=lambda x: x[1], reverse=True)

            enriched = []
            for i, (w, ent) in enumerate(entropy_list[:limit], 1):
                res = calculate_analytics(w, hard, pool, turn + 1, history)
                enriched.append({
                    'word': w, 'win_p': res[0], 'exp': res[1], 'worst': res[2],
                    'missed': res[3], 'stats': res[4], 'isa': res[5], 'entropy': res[6]
                })
                if mode == 1:
                    sys.stdout.write(f"\rProgress: {int((i / limit) * 100)}% ");
                    sys.stdout.flush()

            enriched.sort(key=lambda x: (-x['win_p'], x['exp'], x['worst'], x['isa'], -x['entropy'], x['word']))

            if mode == 1:
                print("\n\nWORD          | WIN %   | EXP (DIFF)         | WORST | ANS?   | STATS")
                print("-" * 75)
                baseline_exp = enriched[0]['exp']
                for item in enriched[:15]:
                    diff = item['exp'] - baseline_exp
                    diff_str = f"(+{diff:.3f})" if diff > 0 else f"({diff:.3f})"
                    ans_str = "True" if item['isa'] else "False"
                    # Corrected monospace padding for table alignment
                    print(
                        f"{item['word'].upper():13} | {item['win_p']:7.1f} | {item['exp']:6.3f} {diff_str:10} | {item['worst']:5} | {ans_str:6} | {item['stats']}")

                if user_manual_guess:
                    u_data = next((x for x in enriched if x['word'] == user_manual_guess), None)
                    if not u_data:
                        u_res = calculate_analytics(user_manual_guess, hard, pool, turn + 1, history)
                        u_data = {'word': user_manual_guess, 'win_p': u_res[0], 'exp': u_res[1], 'worst': u_res[2],
                                  'missed': u_res[3]}

                    def fmt_avg(exp_total, current_t):
                        val = exp_total - current_t
                        return f"≤{val:.3f}" if val > 2 else f"{val:.3f}"

                    print(f"\nYour guess: {u_data['word'].upper()}. Win chance: {u_data['win_p']:.1f}%", end="")
                    if u_data['missed']: print(f". Danger word: {u_data['missed'][0].upper()}", end="")
                    print(f"\nRemaining guesses needed (avg): {fmt_avg(u_data['exp'], turn)}")
                    print(f"Bot suggestion: {enriched[0]['word'].upper()} (Avg: {fmt_avg(enriched[0]['exp'], turn)})")

            current_guess = enriched[0]['word']

    res_turns = turn if (full_history and full_history[-1][1] == "ggggg") else 7
    if mode in [1, 3]: print("\n" + get_share_stats(res_turns, full_history))
    return res_turns, solve_path_colored, solve_path_plain, full_history


def main():
    load_data()
    print("WOBOT SYSTEM\n1: Analysis\n2: 500 Random Tests\n3: Bot Playthrough\n4: Cumulative (All Words)")
    try:
        mode = int(input("Select Mode: "))
        hard = input("Hard Mode? (Y/N): ").lower() == 'y'
        limit = int(input("LIMIT (Depth): "))
        start_w = input("Starting Word: ").lower().strip()
    except ValueError:
        sys.exit("Invalid Input.")

    targets = []
    if mode == 2:
        targets = random.sample(proper_word, 500)
    elif mode == 3:
        targets = [input("Target word: ").lower().strip()]
    elif mode == 4:
        targets = proper_word

    if mode == 1:
        run_game(1, hard, limit, start_w)
    else:
        total_turns, txt_out, pdf_data, dist = 0, [], {}, [0] * 7
        for i, t in enumerate(targets):
            turns, path_col, path_plain, hist = run_game(mode, hard, limit, start_w, target=t)
            total_turns += turns
            dist[min(turns - 1, 6)] += 1
            txt_out.append(",".join(path_plain))
            pdf_data[t] = hist
            print(f"\n{t.upper()} ({i + 1}/{len(targets)})")
            for row in path_col: print(row)
            if mode != 3: print(f"Current Avg: {total_turns / (i + 1):.4f}")

        if mode in [2, 4]:
            print("\n" + "=" * 30 + "\nFINAL STATISTICS")
            print(f"Solve Rate: {(sum(dist[:6]) / len(targets)) * 100:.2f}% ({sum(dist[:6])}/{len(targets)})")
            print(f"Average Score: {total_turns / len(targets):.4f}")
            print("\nDISTRIBUTION")
            colors_hex = ["\033[38;2;114;176;234m", "\033[38;2;123;223;242m", "\033[38;2;121;237;133m",
                          "\033[38;2;172;237;121m", "\033[38;2;242;226;123m", "\033[38;2;239;153;119m"]
            reset = "\033[0m"
            max_val = max(dist) if max(dist) > 0 else 1
            for i in range(6):
                bar = "█" * int((dist[i] / max_val) * 20)
                print(f"{i + 1} {colors_hex[i]}{bar} {dist[i]}{reset}")
            print(f"X {' ' * 20} {dist[6]}\n" + "=" * 30)
            with open(f"{start_w.upper()}.txt", "w") as f:
                f.write("\n".join(txt_out))
            generate_tree_pdf(start_w, pdf_data)


if __name__ == "__main__":
    main()
