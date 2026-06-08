import sys
import os
import random
import math
import time
from functools import lru_cache

# --- CONFIGURATION ENGINE ---
MAX_TURNS = 6  # Dynamic Max Turn setting (Default: 6)

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


def load_data(choice):
    global proper_word, word_list, full_dictionary
    try:
        if choice == 1:
            with open("proper word.txt", "r", encoding="utf-8") as f:
                proper_word = [line.strip().lower() for line in f if len(line.strip()) == 5]
            with open("word list.txt", "r", encoding="utf-8") as f:
                word_list = [line.strip().lower() for line in f if len(line.strip()) == 5]
        elif choice == 2:
            with open("NYT WordleBot Answers (1).txt", "r", encoding="utf-8") as f:
                proper_word = [line.strip().lower() for line in f if len(line.strip()) == 5]
            with open("wordlist_nyt20220830_all (1).txt", "r", encoding="utf-8") as f:
                word_list = [line.strip().lower() for line in f if len(line.strip()) == 5]
        elif choice == 3:
            with open("wordlist_nyt20230701_hidden (2).txt", "r", encoding="utf-8") as f:
                proper_word = [line.strip().lower() for line in f if len(line.strip()) == 5]
            with open("wordlist_nyt20220830_all (1).txt", "r", encoding="utf-8") as f:
                word_list = [line.strip().lower() for line in f if len(line.strip()) == 5]
        elif choice == 4:
            with open("proper word.txt", "r", encoding="utf-8") as f:
                proper_word = [line.strip().lower() for line in f if len(line.strip()) == 5]
            with open("proper word.txt", "r", encoding="utf-8") as f:
                word_list = [line.strip().lower() for line in f if len(line.strip()) == 5]
        elif choice == 5:
            with open("NYT WordleBot Answers (1).txt", "r", encoding="utf-8") as f:
                proper_word = [line.strip().lower() for line in f if len(line.strip()) == 5]
            with open("NYT WordleBot Answers (2).txt", "r", encoding="utf-8") as f:
                word_list = [line.strip().lower() for line in f if len(line.strip()) == 5]
        elif choice == 6:
            with open("wordlist_nyt20220830_hidden.txt", "r", encoding="utf-8") as f:
                proper_word = [line.strip().lower() for line in f if len(line.strip()) == 5]
            with open("wordlist_nyt20220830_all (1).txt", "r", encoding="utf-8") as f:
                word_list = [line.strip().lower() for line in f if len(line.strip()) == 5]
        full_dictionary = list(set(proper_word + word_list))
    except FileNotFoundError:
        sys.exit("CRITICAL ERROR: Dictionary files missing.")


# Global Feedback Matrix Lookup for ultra-high speed tree iterations
GLOBAL_FEEDBACK_CACHE = {}
# Unified Memorization Matrix to track coexistence paths across all permutations
UNIFIED_COEXISTENCE_CACHE = {}


# --- 2. CORE PATTERN ENGINE ---
@lru_cache(maxsize=445)
def get_feedback(secret, guess):
    pair = (secret, guess)
    if pair in GLOBAL_FEEDBACK_CACHE:
        return GLOBAL_FEEDBACK_CACHE[pair]

    if secret == guess:
        GLOBAL_FEEDBACK_CACHE[pair] = "ggggg"
        return "ggggg"

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
    out = "".join(res)
    GLOBAL_FEEDBACK_CACHE[pair] = out
    return out


def get_color_terminal(word, pattern):
    bg_green, bg_yellow, bg_gray = "\033[48;2;83;141;78m", "\033[48;2;181;159;59m", "\033[48;2;58;58;60m"
    text_white, reset = "\033[1;97m", "\033[0m"
    colored_word = ""
    for char, p in zip(word.upper(), pattern):
        if p == 'g':
            colored_word += f"{bg_green}{text_white} {char} {reset}"
        elif p == 'y':
            colored_word += f"{bg_yellow}{text_white} {char} {reset}"
        else:
            colored_word += f"{bg_gray}{text_white} {char} {reset}"
    return colored_word


def get_emoji_pattern(pattern):
    emoji_map = {'g': '▓', 'y': '▒', '_': '░'}
    return "".join(emoji_map[c] for c in pattern)


# --- 3. PDF & TEXT TREE LOGIC ---
def print_distribution(dist):
    print("\nDISTRIBUTION")
    # Exact Hex mappings derived from screenshot colors
    hex_colors = [
        "74;162;230",  # 1: Soft Blue
        "139;211;235",  # 2: Sky Blue
        "134;227;139",  # 3: Mint Green
        "182;240;130",  # 4: Chartreuse
        "240;229;140",  # 5: Straw Yellow
        "230;145;120",  # 6: Muted Terracotta Coral
        "242;162;177"  # X: Rose Pink
    ]
    reset = "\033[0m"
    max_count = max(dist) if max(dist) > 0 else 1
    max_bar_width = 30

    for i in range(7):
        label = str(i + 1) if i < 6 else "X"
        count = dist[i]

        # Sub-character block interpolation configuration to display tiny counts cleanly
        raw_width = (count / max_count) * max_bar_width
        whole_blocks = int(raw_width)
        remainder = raw_width - whole_blocks

        fractional_char = ""
        if count > 0 and whole_blocks == 0:
            fractional_char = "▏"
        elif remainder > 0:
            fractions = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉"]
            frac_idx = int(remainder * 8)
            fractional_char = fractions[frac_idx]

        bar_str = "█" * whole_blocks + fractional_char
        rgb = hex_colors[i]
        color_ansi = f"\033[38;2;{rgb}m"

        print(f"{label} {color_ansi}{bar_str:<31}{reset}{count}")


def export_tree_txt(start_word, results_dict):
    p_map = {'_': 0, 'y': 1, 'g': 2}
    sorted_targets = sorted(results_dict.keys(), key=lambda t: [[p_map.get(c) for c in s[1]] for s in results_dict[t]])

    filename = f"{start_word.upper()}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for target in sorted_targets:
            history = results_dict[target]
            words_path = [step[0] for step in history]
            f.write(",".join(words_path) + "\n")


def generate_tree_pdf(start_word, results_dict):
    if not HAS_PDF: return
    p_map = {'_': 0, 'y': 1, 'g': 2}
    sorted_targets = sorted(results_dict.keys(), key=lambda t: [[p_map.get(c) for c in s[1]] for s in results_dict[t]])
    c = canvas.Canvas(f"{start_word.upper()}_Answer_tree.pdf", pagesize=A4)
    w, h = A4
    y, box, margin = h - 80, 10, 1.5
    word_w, col_w = (box + margin) * 5, (box + margin) * 5 + 35
    colors_map = {'g': colors.HexColor("#538d4e"), 'y': colors.HexColor("#b59f3b"), '_': colors.HexColor("#3a3a3c")}
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, h - 40, f"WORDLE DECISION TREE: {start_word.upper()}")
    prev_h = None
    for target in sorted_targets:
        if y < 50: c.showPage(); y, prev_h = h - 60, None
        history, x = results_dict[target], 40
        for i, (word, pattern) in enumerate(history):
            is_rep = prev_h and i < len(prev_h) and prev_h[i] == (word, pattern)
            if is_rep:
                c.setFillColor(colors.black);
                c.setFont("Helvetica-Bold", 10);
                c.drawCentredString(x + word_w / 2, y + 2, "↓")
            else:
                for ci, pc in enumerate(pattern):
                    bx = x + (ci * (box + margin))
                    c.setFillColor(colors_map.get(pc, colors.gray));
                    c.rect(bx, y, box, box, stroke=0, fill=1)
                    c.setFillColor(colors.white);
                    c.setFont("Helvetica", 7);
                    c.drawCentredString(bx + box / 2, y + 2.5, word[ci].upper())
            if i < len(history) - 1:
                arrow = "↓" if prev_h and i + 1 < len(prev_h) and history[i] == prev_h[i] and history[i + 1] == prev_h[
                    i + 1] else "→"
                if is_rep and not (prev_h and i + 1 < len(prev_h) and prev_h[i + 1] == history[i + 1]): arrow = "→"
                c.setFillColor(colors.black);
                c.setFont("Helvetica-Bold", 10);
                c.drawCentredString(x + word_w + 15, y + 2, arrow)
            x += col_w
        prev_h, y = history, y - 18
    c.save()


# --- 4. CORE ANALYTICS ---
tree_memory = {}
SUBPOOL_SOLVER_CACHE = {}  # Fast execution sub-pool lookahead storage
BRANCH_PREDICTION_MATRIX = {}  # Multi-tier matrix mapping across common parent buckets


def is_hard_mode_valid(guess, prev_guess, pattern):
    if not prev_guess or not pattern: return True
    for i, p in enumerate(pattern):
        if p == "g" and guess[i] != prev_guess[i]: return False
    req_counts = {}
    for i, p in enumerate(pattern):
        if p in ("g", "y"):
            c = prev_guess[i];
            req_counts[c] = req_counts.get(c, 0) + 1
    for char, count in req_counts.items():
        if guess.count(char) < count: return False
    return True


@lru_cache(maxsize=445)
def get_entropy_score(word, pool_tuple, hard_flag):
    groups = {}
    for secret in pool_tuple:
        p = get_feedback(secret, word);
        groups[p] = groups.get(p, 0) + 1
    score = len(groups) - (sum(v * v for v in groups.values()) / 100000)
    if word in pool_tuple: score += 0.000001 if hard_flag else 0.4
    return score


def calculate_analytics(candidate, is_hard, pool, turn, history, limit_depth=5):
    total_turns, missed, stats, max_turn_achieved = 0, [], [0] * (MAX_TURNS + 1), 0
    pool_list = list(pool)

    # Nudge the evaluated current turn index to track depths accurately
    eval_turn = turn + 1

    if limit_depth >= 50:
        adjusted_depth = 15 if is_hard else 10
    else:
        adjusted_depth = limit_depth

    # Group targets into feedback pattern buckets and find largest bucket size
    buckets = {}
    largest_group = 0
    for secret in pool_list:
        p = get_feedback(secret, candidate)
        if p not in buckets:
            buckets[p] = []
        buckets[p].append(secret)

    if buckets:
        largest_group = max(len(sub) for sub in buckets.values())

    for p, sub_pool in buckets.items():
        if p == "ggggg":
            total_turns += eval_turn * len(sub_pool)
            if eval_turn - 1 < len(stats):
                stats[eval_turn - 1] += len(sub_pool)
            if eval_turn > max_turn_achieved:
                max_turn_achieved = eval_turn
            continue

        if len(sub_pool) == 1:
            res_t = eval_turn + 1
            if res_t > MAX_TURNS:
                missed.extend(sub_pool)
                total_turns += 7 * len(sub_pool)
                if MAX_TURNS < len(stats): stats[MAX_TURNS] += len(sub_pool)
                max_turn_achieved = 7
            else:
                total_turns += res_t * len(sub_pool)
                if res_t - 1 < len(stats): stats[res_t - 1] += len(sub_pool)
                if res_t > max_turn_achieved: max_turn_achieved = res_t
            continue

        # Extract optimal next guess for child sub-pool branch using decremented depth boundary
        child_guess = get_best_move(tuple(sub_pool), is_hard, candidate, p, tuple(history + [(candidate, p)]),
                                    limit_depth=adjusted_depth - 1)

        for secret in sub_pool:
            s_p, s_g, s_t, s_hist = sub_pool.copy(), child_guess, eval_turn + 1, list(history) + [(candidate, p)]
            while s_t <= MAX_TURNS:
                sp_p = get_feedback(secret, s_g)
                s_hist.append((s_g, sp_p))
                if sp_p == "ggggg":
                    total_turns += s_t
                    if s_t - 1 < len(stats): stats[s_t - 1] += 1
                    if s_t > max_turn_achieved: max_turn_achieved = s_t
                    break
                s_p = [w for w in s_p if get_feedback(w, s_g) == sp_p]
                if not s_p: break
                if len(s_p) == 1:
                    res_t = s_t + 1
                    if res_t > MAX_TURNS:
                        missed.append(secret)
                        total_turns += 7
                        if MAX_TURNS < len(stats): stats[MAX_TURNS] += 1
                        max_turn_achieved = 7
                    else:
                        total_turns += res_t
                        if res_t - 1 < len(stats): stats[res_t - 1] += 1
                        if res_t > max_turn_achieved: max_turn_achieved = res_t
                    break
                s_t += 1
                if s_t > MAX_TURNS:
                    missed.append(secret)
                    total_turns += 7
                    if MAX_TURNS < len(stats): stats[MAX_TURNS] += 1
                    max_turn_achieved = 7
                    break
                s_g = get_best_move(tuple(s_p), is_hard, s_g, sp_p, tuple(s_hist), limit_depth=1)

    win_p = (len(pool) - len(missed)) / len(pool) * 100 if pool else 0
    avg_t = total_turns / len(pool) if pool else 0
    pool_tuple = tuple(pool)
    return win_p, avg_t, max_turn_achieved, missed, stats, (candidate in pool), get_entropy_score(candidate, pool_tuple,
                                                                                                  is_hard), largest_group


def evaluate_and_rank_moves(pool, hard, final_word, p, turn, history, limit, show_progress=False):
    pool_tuple = tuple(pool)

    if len(pool_tuple) <= 2:
        return [{
            'word': pool_tuple[0], 'win_p': 100.0, 'exp': 1.0, 'worst': 1,
            'missed': [], 'stats': [0] * (MAX_TURNS + 1), 'isa': 1, 'entropy': 0.0, 'six_games': 0, 'five_p': 0,
            'largest': 0
        }]

    cache_matrix_key = (pool_tuple, hard, limit)
    if cache_matrix_key in BRANCH_PREDICTION_MATRIX:
        return BRANCH_PREDICTION_MATRIX[cache_matrix_key]

    active_pool = full_dictionary if not hard else [c for c in full_dictionary if is_hard_mode_valid(c, final_word, p)]
    entropy_list = sorted([(w, get_entropy_score(w, pool_tuple, hard)) for w in active_pool], key=lambda x: x[1],
                          reverse=True)

    enriched = []
    for i, (w, ent) in enumerate(entropy_list[:limit], 1):
        res = calculate_analytics(w, hard, pool, turn, history, limit_depth=limit)
        six_count = res[4][5] if len(res[4]) > 5 else 0
        five_p_and_above = sum(res[4][4:]) if len(res[4]) > 4 else 0

        enriched.append({
            'word': w, 'win_p': res[0], 'exp': res[1], 'worst': res[2],
            'missed': res[3], 'stats': res[4], 'isa': int(res[5]), 'entropy': res[6],
            'six_games': six_count, 'five_p': five_p_and_above, 'largest': res[7]
        })
        if show_progress:
            sys.stdout.write(f"\rProgress: {int((i / limit) * 100)}% ")
            sys.stdout.flush()

    if len(enriched) < limit:
        needed = limit - len(enriched)
        for _ in range(needed):
            enriched.append({
                'word': "-----", 'win_p': 0.0, 'exp': 0.0, 'worst': 0,
                'missed': [], 'stats': [0] * (MAX_TURNS + 1), 'isa': 0, 'entropy': 0.0,
                'six_games': 99999, 'five_p': 99999, 'largest': 99999
            })

    # Perfect alphabetical tiebreaking constraint verification hierarchy
    enriched.sort(
        key=lambda x: (-x['win_p'], x['exp'], x['worst'], x['six_games'], x['five_p'], x['largest'], x['word']))

    BRANCH_PREDICTION_MATRIX[cache_matrix_key] = enriched
    return enriched


def get_best_move(pool, is_hard, prev_guess, last_p, history_tuple, limit_depth=5, fixed_sequence=None):
    current_turn_index = len(history_tuple)
    if fixed_sequence and current_turn_index < len(fixed_sequence):
        return fixed_sequence[current_turn_index]

    if len(pool) <= 2:
        return pool[0]

    if limit_depth <= 1:
        pool_tuple = tuple(pool)
        active_pool = full_dictionary if not is_hard else [c for c in full_dictionary if
                                                           is_hard_mode_valid(c, prev_guess, last_p)]
        best_shallow = max(active_pool, key=lambda w: get_entropy_score(w, pool_tuple, is_hard))
        return best_shallow

    cache_key = (history_tuple, is_hard, limit_depth)
    if cache_key in tree_memory: return tree_memory[cache_key]

    enriched = evaluate_and_rank_moves(list(pool), is_hard, prev_guess, last_p, len(history_tuple), list(history_tuple),
                                       limit=limit_depth, show_progress=False)
    best_word = enriched[0]['word']
    tree_memory[cache_key] = best_word
    return best_word


def get_share_stats(turns, history):
    emoji_map = {'g': '🟩', 'y': '🟨', '_': '⬛'}
    grid = "".join(["".join(emoji_map[c] for c in p) + "\n" for _, p in history])
    score = "X" if turns > MAX_TURNS else turns
    return f"WOBOT {score}/{MAX_TURNS}\n\n{grid}"


# --- 5. MODE 5 Logic ---
def run_starting_word_test(start_word, hard, limit):
    print(f"\n--- Starting Word Test: {start_word.upper()} ---")
    groups = {}
    for word in proper_word:
        p = get_feedback(word, start_word)
        if p not in groups: groups[p] = []
        groups[p].append(word)

    p_rank = {'_': '0', 'y': '1', 'g': '2'}
    sorted_patterns = sorted(groups.keys(), key=lambda p: "".join(p_rank[c] for c in p))

    total_proper = len(proper_word)
    for p in sorted_patterns:
        sub_pool = groups[p]
        history = ((start_word, p),)
        bits = math.log2(total_proper / len(sub_pool))
        next_move = get_best_move(tuple(sub_pool), hard, start_word, p, history, limit_depth=limit)
        res = calculate_analytics(next_move, hard, sub_pool, 1, history, limit_depth=limit)
        avg_left = res[1] - 1

        print(f"{start_word.upper()} {get_emoji_pattern(p)} -> {next_move.upper()} "
              f"(≤{avg_left:.2f} left, {len(sub_pool)} words left, ~{bits:.2f} bits)")


# --- 6. EXECUTION ---
def run_game(mode, hard, limit, start_word, target=None, fixed_sequence=None):
    pool, turn, history = proper_word.copy(), 0, []
    solve_path_plain, solve_path_colored, full_history = [], [], []
    current_guess, user_manual_guess = start_word, None

    while turn < MAX_TURNS:
        turn += 1
        if mode in [2, 3, 4, 6, 7]:
            p = get_feedback(target, current_guess)
        else:
            while True:
                user_input = input(f"\nPattern for '{current_guess.upper()}': ").lower().strip()
                raw = user_input.split()
                if not raw: continue
                user_manual_guess, p = (raw[0].lower(), raw[1]) if len(raw) > 1 else (None, raw[0])
                if len(p) == 5 and all(c in 'gy_' for c in p): break

        final_word = user_manual_guess if user_manual_guess else current_guess
        solve_path_plain.append(final_word)
        solve_path_colored.append(get_color_terminal(final_word, p))
        full_history.append((final_word, p))

        if mode == 1 and turn > 1:
            u_res = calculate_analytics(final_word, hard, pool, turn - 1, history, limit_depth=limit)
            print(f"Your guess {final_word.upper()} needs an average of ≤{u_res[1] - (turn - 1):.3f}")

        if p == "ggggg": break
        pool = [w for w in pool if get_feedback(w, final_word) == p]
        history.append((final_word, p))

        if turn < MAX_TURNS:
            if fixed_sequence and turn < len(fixed_sequence):
                current_guess = fixed_sequence[turn]
            else:
                state_key = (tuple(pool), hard, limit, final_word, p, turn)
                if mode == 7 and state_key in UNIFIED_COEXISTENCE_CACHE:
                    current_guess = UNIFIED_COEXISTENCE_CACHE[state_key]
                else:
                    enriched = evaluate_and_rank_moves(pool, hard, final_word, p, turn, history, limit,
                                                       show_progress=(mode == 1))
                    if mode == 1:
                        print(f"\n\nWORD          | WIN %   | EXP (DIFF)         | WORST | ANS?   | STATS\n" + "-" * 75)
                        base_exp = enriched[0]['exp']
                        for item in enriched[:limit]:
                            diff = item['exp'] - base_exp
                            print(
                                f"{item['word'].upper():13} | {item['win_p']:7.1f} | {item['exp']:6.3f} ({diff:+.3f})  | {str(item['worst']):5} | {str(bool(item['isa'])):6} | {item['stats']}")
                    current_guess = enriched[0]['word']
                    if mode == 7:
                        UNIFIED_COEXISTENCE_CACHE[state_key] = current_guess

    res_turns = turn if (full_history and full_history[-1][1] == "ggggg") else 7
    if mode in [1, 3]: print("\n" + get_share_stats(res_turns, full_history))
    return res_turns, solve_path_colored, solve_path_plain, full_history, pool


def main():
    global MAX_TURNS
    print(
        "WOBOT - The Wordle Solver\nWORDLISTS (1: Orig, 2: NYT, 3: Alex Selby, 4: Answers only, 5: WordleBot, 6: NYT release for the 2309 wordlist)")
    try:
        wl_choice = int(input("Select Wordlist: "))
        load_data(wl_choice)

        try:
            max_input = input("Set Max Guess limit (Press Enter for default 6): ").strip()
            if max_input:
                MAX_TURNS = int(max_input)
        except ValueError:
            print("Invalid bound value. Defaulting to 6.")
            MAX_TURNS = 6

        print(
            "\n1: Analysis\n2: 500 Random Tests\n3: Bot Playthrough\n4: Cumulative\n5: Starting Word Test\n6: Test Word Pairs Sequence\n7: Exhaustive Whole Cumulative")
        mode = int(input("Select Mode: "))
        hard = input("Hard Mode? (Y/N): ").lower() == 'y'
        limit = int(input("LIMIT (Depth): "))

        fixed_sequence = None
        if mode == 6:
            pair_input = input(
                "Type your explicit test sequence (e.g., parse,clint or stare,cloud,pinky): ").lower().strip()
            fixed_sequence = [w.strip() for w in pair_input.split(",") if len(w.strip()) == 5]
            if not fixed_sequence:
                sys.exit("Error: No valid words found in entry string sequence pattern.")
            start_w = fixed_sequence[0]
        elif mode == 7:
            start_w = ""
        else:
            start_w = input("Starting Word: ").lower().strip()

    except ValueError:
        sys.exit("Invalid Input.")

    if mode == 5:
        run_starting_word_test(start_w, hard, limit)
    elif mode == 1:
        run_game(1, hard, limit, start_w)
    elif mode == 7:
        # --- MODE 7: EXHAUSTIVE WHOLE CUMULATIVE ENGINE ---
        total_wordlist_len = len(word_list)
        print(
            f"\nExecuting Exhaustive Matrix Mode... (Evaluating {total_wordlist_len} Starters × {len(proper_word)} Answers)")
        exhaustive_results = []

        # Start global execution stopwatch tracking total running time profile
        global_start_time = time.perf_counter()

        for s_idx, starter in enumerate(word_list):
            total_turns = 0
            stats = [0] * (MAX_TURNS + 1)
            missed_count = 0
            worst_turn = 0

            # Record puzzle start time profile split
            puzzle_start_time = time.perf_counter()

            buckets = {}
            for target in proper_word:
                p = get_feedback(target, starter)
                if p not in buckets:
                    buckets[p] = []
                buckets[p].append(target)
            starter_largest_group = max(len(sub) for sub in buckets.values()) if buckets else 0

            completion_pct = (s_idx / total_wordlist_len) * 100
            sys.stdout.write(
                f"\r\033[K[Progress: {completion_pct:.2f}%] Processing Starter: {starter} ({s_idx + 1}/{total_wordlist_len})")
            sys.stdout.flush()

            for target in proper_word:
                turns, _, _, _, _ = run_game(7, hard, limit, starter, target=target)

                if turns > MAX_TURNS:
                    missed_count += 1
                    total_turns += 7
                    stats[MAX_TURNS] += 1
                    if 7 > worst_turn:
                        worst_turn = 7
                else:
                    total_turns += turns
                    stats[turns - 1] += 1
                    if turns > worst_turn:
                        worst_turn = turns

            puzzle_end_time = time.perf_counter()
            puzzle_duration_ms = (puzzle_end_time - puzzle_start_time) * 1000

            win_p = ((len(proper_word) - missed_count) / len(proper_word)) * 100
            avg_turns = total_turns / len(proper_word)
            six_games_count = stats[5] if len(stats) > 5 else 0
            five_p_and_above = sum(stats[4:])
            isa_flag = int(starter in proper_word)

            formatted_stats = {}
            for i in range(MAX_TURNS):
                if stats[i] > 0:
                    formatted_stats[i + 1] = stats[i]
            if stats[MAX_TURNS] > 0:
                formatted_stats[MAX_TURNS + 1] = stats[MAX_TURNS]

            sorted_stats_dict = dict(sorted(formatted_stats.items()))

            entry = {
                'word': starter,
                'win_p': win_p,
                'exp': avg_turns,
                'worst': worst_turn,
                'six_games': six_games_count,
                'five_p': five_p_and_above,
                'largest': starter_largest_group,
                'isa': isa_flag,
                'stats_str': str(sorted_stats_dict),
                'total_guesses': total_turns
            }
            exhaustive_results.append(entry)

            # Outputs real log formatting displaying cumulative guess totals along with milliseconds elapsed per starter
            sys.stdout.write(
                f"\r\033[K{s_idx + 1} {starter} {total_turns} ({s_idx + 1}, {avg_turns:.14f}, {sorted_stats_dict}) [{puzzle_duration_ms:.2f} ms]\n")
            sys.stdout.flush()

        exhaustive_results.sort(
            key=lambda x: (-x['win_p'], x['exp'], x['worst'], x['six_games'], x['five_p'], x['largest'], x['word']))

        global_end_time = time.perf_counter()
        global_duration_secs = global_end_time - global_start_time

        output_filename = "exhaustive_stats.txt"
        with open(output_filename, "w", encoding="utf-8") as f:
            for item in exhaustive_results:
                f.write(
                    f"{item['word'].upper()} ({item['word']}, {item['exp']:.14f}, {item['stats_str']}) Total Guesses: {item['total_guesses']}\n")

        print(f"\nExhaustive Run Complete! Master stats successfully exported to '{output_filename}'.")
        print(f"Total Processing Time Taken: {global_duration_secs:.4f} seconds.")
    else:
        targets = []
        if mode == 2:
            targets = random.sample(proper_word, min(500, len(proper_word)))
        elif mode == 3:
            targets = [input("Target word: ").lower().strip()]
        elif mode in [4, 6]:
            targets = proper_word

        total_turns, pdf_data, dist = 0, {}, [0] * 7

        # Execution timing trackers for separate modes
        batch_start_time = time.perf_counter()

        for i, t in enumerate(targets):
            single_start = time.perf_counter()
            turns, path_col, path_plain, hist, final_pool = run_game(mode, hard, limit, start_w, target=t,
                                                                     fixed_sequence=fixed_sequence)
            single_duration = (time.perf_counter() - single_start) * 1000

            idx = min(turns - 1, 6)
            dist[idx] += 1
            total_turns += turns
            pdf_data[t] = hist
            print(f"\n{t.upper()} ({i + 1}/{len(targets)}) [{single_duration:.2f} ms]")
            for row in path_col: print(row)

        batch_duration = time.perf_counter() - batch_start_time

        if mode in [2, 4, 6]:
            print(f"\nFINAL STATISTICS")
            print(f"Total Guesses Taken for {start_w.lower()}: {total_turns}")
            print(f"Avg Steps: {total_turns / len(targets):.4f}")
            print(f"Total Processing Time Taken: {batch_duration:.4f} seconds.")
            print_distribution(dist)
            generate_tree_pdf(start_w, pdf_data)
            export_tree_txt(start_w, pdf_data)


if __name__ == "__main__":
    main()
