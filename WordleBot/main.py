import sys
import os
import random
from functools import lru_cache

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


def get_color_blocks(pattern):
    bg_green = "\033[38;2;83;141;78m"
    bg_yellow = "\033[38;2;181;159;59m"
    bg_gray = "\033[38;2;58;58;60m"
    reset = "\033[0m"
    colored = ""
    for p in pattern:
        if p == 'g':
            colored += f"{bg_green}■{reset}"
        elif p == 'y':
            colored += f"{bg_yellow}■{reset}"
        else:
            colored += f"{bg_gray}■{reset}"
    return colored


def get_color_terminal(word, pattern):
    return f"{word.upper():<7} {get_color_blocks(pattern)}"


# --- 3. ANALYTICS & SAFETY ---
tree_memory = {}


def is_hard_mode_valid(guess, prev_guess, pattern):
    if not prev_guess or not pattern: return True
    for i, p in enumerate(pattern):
        if p == "g" and guess[i] != prev_guess[i]: return False
    req = {}
    for i, p in enumerate(pattern):
        if p in ("g", "y"):
            char = prev_guess[i]
            req[char] = req.get(char, 0) + 1
    for char, count in req.items():
        if guess.count(char) < count: return False
    return True


def get_best_move(pool, is_hard, prev_guess, last_p, history_tuple):
    cache_key = (history_tuple, is_hard)
    if cache_key in tree_memory: return tree_memory[cache_key]
    if len(pool) <= 2: return pool[0]

    candidates = full_dictionary
    if is_hard:
        candidates = [c for c in full_dictionary if is_hard_mode_valid(c, prev_guess, last_p)]

    best_word, best_score = None, -1
    for cand in candidates:
        groups = {}
        for secret in pool:
            p = get_feedback(secret, cand)
            groups[p] = groups.get(p, 0) + 1
        score = len(groups) - (sum(v * v for v in groups.values()) / 100000)
        if cand in pool: score += 0.4
        if score > best_score:
            best_score, best_word = score, cand

    tree_memory[cache_key] = best_word
    return best_word


def calculate_analytics(candidate, is_hard, pool, turn, history):
    total_turns, missed, stats = 0, [], [0] * 7
    for secret in pool:
        s_p, s_g, s_t, s_hist = list(pool), candidate, turn, list(history)
        while s_t <= 6:
            p = get_feedback(secret, s_g)
            s_hist.append((s_g, p))
            if p == "ggggg":
                total_turns += s_t
                stats[s_t - 1] += 1
                break
            s_p = [w for w in s_p if get_feedback(w, s_g) == p]
            if not s_p: break
            if len(s_p) == 1:
                res_t = s_t + 1
                if res_t > 6:
                    missed.append(secret);
                    total_turns += 7;
                    stats[6] += 1
                else:
                    total_turns += res_t;
                    stats[res_t - 1] += 1
                break
            s_t += 1
            if s_t > 6:
                missed.append(secret);
                total_turns += 7;
                stats[6] += 1
                break
            s_g = get_best_move(tuple(s_p), is_hard, s_g, p, tuple(s_hist))

    win_pct = (len(pool) - len(missed)) / len(pool) * 100
    avg_exp = total_turns / len(pool)
    worst = 7 if missed else max([i + 1 for i, s in enumerate(stats) if s > 0], default=0)
    return win_pct, avg_exp, worst, missed, (candidate in pool)


# --- 4. EXECUTION LOOP ---
def run_game(mode, hard, limit, start_word, target=None):
    pool, turn, history = proper_word.copy(), 0, []
    current_guess = start_word
    playthrough_visuals = []

    while turn < 6:
        turn += 1
        p = get_feedback(target, current_guess) if mode in [2, 3, 4] else None

        if mode == 1:
            dist = {}
            for w in pool:
                pat = get_feedback(w, current_guess)
                if pat not in dist: dist[pat] = []
                dist[pat].append(w)
            sorted_dist = sorted(dist.items(), key=lambda x: len(x[1]), reverse=True)

            print(f"\nDISTRIBUTION FOR '{current_guess.upper()}':")
            print(f"{'PATTERN':<10} | {'CHANCE':<6} | {'COUNT':<5} | {'CANDIDATE WORDS'}")
            print("-" * 85)
            for pat, words in sorted_dist:
                prob = (len(words) / len(pool)) * 100
                count = len(words)
                # Show max 10 words, then ...
                display_words = ", ".join(words[:10])
                if count > 10:
                    display_words += " ..."
                print(f"{get_color_blocks(pat):<19} | {prob:>5.1f}% | {count:>5} | {display_words}")

            while True:
                u_in = input(f"\nPattern for '{current_guess.upper()}': ").lower().strip()
                input_parts = u_in.split()
                if not input_parts: continue
                p = input_parts[-1]
                if len(p) == 5 and all(c in 'gy_' for c in p): break

        playthrough_visuals.append(get_color_terminal(current_guess, p))
        if p == "ggggg": break

        pool = [w for w in pool if get_feedback(w, current_guess) == p]
        history.append((current_guess, p))

        if turn < 6:
            cands = full_dictionary
            if hard: cands = [c for c in full_dictionary if is_hard_mode_valid(c, current_guess, p)]

            recs = []
            for c in cands:
                pg = {}
                for s in pool:
                    ps = get_feedback(s, c);
                    pg[ps] = pg.get(ps, 0) + 1
                score = len(pg) - (sum(v * v for v in pg.values()) / 100000)
                if c in pool: score += 0.4
                recs.append((c, score))

            recs.sort(key=lambda x: x[1], reverse=True)
            enriched = []
            for i, (w, sc) in enumerate(recs[:min(len(recs), limit)], 1):
                win_p, exp, worst, missed, isa = calculate_analytics(w, hard, pool, turn + 1, history)
                enriched.append({'word': w, 'win_p': win_p, 'exp': exp, 'worst': worst, 'isa': isa, 'missed': missed})
                if mode == 1:
                    sys.stdout.write(f"\rAnalysing Suggestions: {int((i / min(len(recs), limit)) * 100)}% ")
                    sys.stdout.flush()

            enriched.sort(key=lambda x: (-x['win_p'], x['exp'], x['worst'], -x['isa'], x['word']))

            if mode == 1:
                print(f"\n\n{'WORD':<8} | {'WIN %':<8} | {'EXP':<6} | {'WORST':<5} | {'!LOSES ON!'}")
                for item in enriched[:limit]:
                    print(
                        f"{item['word'].upper():<8} | {item['win_p']:>7.1f}% | {item['exp']:>6.3f} | {item['worst']:>5} | {', '.join(item['missed'][:3])}")

            current_guess = enriched[0]['word']

    return turn, playthrough_visuals


def main():
    load_data()
    print("WOBOT ANALYTICS\n1: Interactive\n2: 500 Random Tests\n3: Specific Solve\n4: Full Dictionary")
    mode_in = input("Select Mode: ")
    if not mode_in: return
    mode = int(mode_in)
    hard = input("Hard Mode? (Y/N): ").lower() == 'y'
    limit = int(input("Suggestion Depth (Limit): "))
    start_w = input("Start Word (e.g., CRANE): ").lower().strip() or "crane"

    targets = []
    if mode == 2:
        targets = random.sample(proper_word, 500)
    elif mode == 3:
        targets = [input("Target Word: ").lower().strip()]
    elif mode == 4:
        targets = proper_word

    if mode == 1:
        run_game(1, hard, limit, start_w, target="xxxxx")
    else:
        total_turns = 0
        for i, t in enumerate(targets):
            turns, visuals = run_game(mode, hard, limit, start_w, target=t)
            total_turns += turns
            print(f"\nTARGET: {t.upper()} ({i + 1}/{len(targets)})")
            for row in visuals: print(row)
            print(f"Turns: {turns} | Avg: {total_turns / (i + 1):.4f}")


if __name__ == "__main__":
    main()
