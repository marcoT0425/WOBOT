#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_TURNS 6
#define PATTERN_SPACE 243
#define BATCH_SIZE 50

typedef struct { char str[6]; } Word;
typedef struct { Word* data; size_t size; size_t capacity; } WordVector;

typedef struct {
    char word[6];
    long total_turns;
    double avg_turns;
    int stats[8];
    int worst;
} MassTestResult;

typedef struct CacheNode {
    size_t pool_hash;
    char best_word[6];
    struct CacheNode* next;
} CacheNode;

#define HASH_SIZE 131072
CacheNode* memo_table[HASH_SIZE];

WordVector targets;
WordVector dictionary;

/* --- HARD MODE LOGIC --- */

// Checks if 'guess' is a valid hard mode play given 'prev_guess' resulted in 'pattern_int'
bool is_hard_mode_valid(const char* guess, const char* prev_guess, int pattern_int) {
    if (prev_guess == NULL) return true;

    int p[5];
    int temp = pattern_int;
    for (int i = 0; i < 5; i++) {
        p[i] = temp % 3;
        temp /= 3;
    }

    // 1. Green Constraint: Must match position
    for (int i = 0; i < 5; i++) {
        if (p[i] == 2 && guess[i] != prev_guess[i]) return false;
    }

    // 2. Yellow/Green Constraint: Must contain at least the same count of revealed letters
    int req_counts[26] = {0};
    for (int i = 0; i < 5; i++) {
        if (p[i] > 0) { // Yellow (1) or Green (2)
            req_counts[prev_guess[i] - 'a']++;
        }
    }

    int guess_counts[26] = {0};
    for (int i = 0; i < 5; i++) {
        guess_counts[guess[i] - 'a']++;
    }

    for (int i = 0; i < 26; i++) {
        if (guess_counts[i] < req_counts[i]) return false;
    }

    return true;
}

/* --- CORE ENGINE --- */

int get_pattern_int(const char* secret, const char* guess) {
    int res[5] = {0, 0, 0, 0, 0};
    char s_tmp[6], g_tmp[6];
    memcpy(s_tmp, secret, 6); memcpy(g_tmp, guess, 6);

    for (int i = 0; i < 5; i++) {
        if (g_tmp[i] == s_tmp[i]) { res[i] = 2; s_tmp[i] = g_tmp[i] = '*'; }
    }
    for (int i = 0; i < 5; i++) {
        if (g_tmp[i] != '*') {
            for (int j = 0; j < 5; j++) {
                if (s_tmp[j] == g_tmp[i]) { res[i] = 1; s_tmp[j] = '*'; break; }
            }
        }
    }
    return res[0] + 3*res[1] + 9*res[2] + 27*res[3] + 81*res[4];
}

void vec_init(WordVector* v, size_t cap) {
    v->size = 0; v->capacity = cap;
    v->data = (Word*)malloc(v->capacity * sizeof(Word));
}

void vec_push(WordVector* v, const char* s) {
    if (v->size >= v->capacity) return;
    for (int i = 0; i < 5; i++) v->data[v->size].str[i] = (char)tolower(s[i]);
    v->data[v->size].str[5] = '\0';
    v->size++;
}

size_t hash_pool(const WordVector* v) {
    size_t h = 14695981039346656037ULL;
    for (size_t i = 0; i < v->size; i++) {
        for (int j = 0; j < 5; j++) {
            h ^= (size_t)v->data[i].str[j];
            h *= 1099511628211ULL;
        }
    }
    return h;
}

double get_entropy(const char* word, const WordVector* pool) {
    int counts[PATTERN_SPACE] = {0};
    for (size_t i = 0; i < pool->size; i++) {
        counts[get_pattern_int(pool->data[i].str, word)]++;
    }
    double entropy = 0;
    for (int i = 0; i < PATTERN_SPACE; i++) {
        if (counts[i] > 0) {
            double p = (double)counts[i] / (double)pool->size;
            entropy -= p * log2(p);
        }
    }
    return entropy;
}

// Added hard_mode parameters to filter available dictionary guesses
void pick_best(const WordVector* pool, char* out, const char* prev_guess, int prev_pattern) {
    if (pool->size <= 2) { strcpy(out, pool->data[0].str); return; }

    size_t h = hash_pool(pool);
    size_t idx = h % HASH_SIZE;
    CacheNode* curr = memo_table[idx];
    while (curr) {
        if (curr->pool_hash == h) { strcpy(out, curr->best_word); return; }
        curr = curr->next;
    }

    double best_s = -1.0;
    for (size_t i = 0; i < dictionary.size; i++) {
        // HARD MODE FILTER
        if (!is_hard_mode_valid(dictionary.data[i].str, prev_guess, prev_pattern)) continue;

        double s = get_entropy(dictionary.data[i].str, pool);
        for(size_t k=0; k < pool->size; k++) {
            if(strcmp(dictionary.data[i].str, pool->data[k].str) == 0) { s += 0.05; break; }
        }
        if (s > best_s) { best_s = s; strcpy(out, dictionary.data[i].str); }
    }

    CacheNode* node = malloc(sizeof(CacheNode));
    node->pool_hash = h; memcpy(node->best_word, out, 6);
    node->next = memo_table[idx]; memo_table[idx] = node;
}

int play_game(const char* starter, const char* target) {
    char guess[6]; strcpy(guess, starter);
    WordVector pool;
    vec_init(&pool, targets.size);
    memcpy(pool.data, targets.data, targets.size * sizeof(Word));
    pool.size = targets.size;

    char prev_guess[6];
    int last_pattern = -1;

    for (int turn = 1; turn <= MAX_TURNS; turn++) {
        int p = get_pattern_int(target, guess);
        if (p == 242) { free(pool.data); return turn; }
        if (turn == MAX_TURNS) { free(pool.data); return 7; }

        size_t next_idx = 0;
        for (size_t i = 0; i < pool.size; i++) {
            if (get_pattern_int(pool.data[i].str, guess) == p) {
                pool.data[next_idx++] = pool.data[i];
            }
        }
        pool.size = next_idx;

        strcpy(prev_guess, guess);
        last_pattern = p;

        pick_best(&pool, guess, prev_guess, last_pattern);
    }
    free(pool.data); return 7;
}

int compare_res(const void* a, const void* b) {
    MassTestResult* r1 = (MassTestResult*)a;
    MassTestResult* r2 = (MassTestResult*)b;
    if (r1->avg_turns < r2->avg_turns) return -1;
    if (r1->avg_turns > r2->avg_turns) return 1;
    return 0;
}

int main() {
    vec_init(&targets, 2315);
    vec_init(&dictionary, 12972);

    const char* p_path = "/Users/marco/CLionProjects/untitled1/proper word.txt";
    const char* l_path = "/Users/marco/CLionProjects/untitled1/word list.txt";

    FILE *f1 = fopen(p_path, "r"), *f2 = fopen(l_path, "r");
    if (!f1 || !f2) { printf("Error: Dictionary files not found.\n"); return 1; }

    char buf[256];
    while (fscanf(f1, "%s", buf) != EOF && targets.size < 2315) {
        if(strlen(buf) == 5) vec_push(&targets, buf);
    }
    while (fscanf(f2, "%s", buf) != EOF && dictionary.size < 12972) {
        if(strlen(buf) == 5) vec_push(&dictionary, buf);
    }
    fclose(f1); fclose(f2);

    MassTestResult* results = calloc(dictionary.size, sizeof(MassTestResult));
    int row_count = 0;

    for (size_t i = 0; i < dictionary.size; i++) {
        memcpy(results[i].word, dictionary.data[i].str, 6);
        for (size_t j = 0; j < targets.size; j++) {
            int t = play_game(dictionary.data[i].str, targets.data[j].str);
            results[i].stats[t > 6 ? 7 : t]++;
            results[i].total_turns += (t > 6 ? 7 : t);
        }
        results[i].avg_turns = (double)results[i].total_turns / (double)targets.size;

        printf("%-5zu %-6s (%.15f, {1: %d, 2: %d, 3: %d, 4: %d, 5: %d, 6: %d, X: %d})\n",
               i + 1, results[i].word, results[i].avg_turns,
               results[i].stats[1], results[i].stats[2], results[i].stats[3],
               results[i].stats[4], results[i].stats[5], results[i].stats[6], results[i].stats[7]);

        if (++row_count == BATCH_SIZE) {
            for (int r = 0; r < BATCH_SIZE; r++) printf("\033[A");
            row_count = 0;
        }
    }

    qsort(results, dictionary.size, sizeof(MassTestResult), compare_res);

    FILE* out = fopen("wobot_results.txt", "w");
    for (size_t i = 0; i < dictionary.size; i++) {
        fprintf(out, "%zu %s (%.15f, {1: %d, 2: %d, 3: %d, 4: %d, 5: %d, 6: %d, X: %d})\n",
                i + 1, results[i].word, results[i].avg_turns,
                results[i].stats[1], results[i].stats[2], results[i].stats[3],
                results[i].stats[4], results[i].stats[5], results[i].stats[6], results[i].stats[7]);
    }
    fclose(out);
    return 0;
}
