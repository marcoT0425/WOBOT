# WOBOT
WOBOT is one of the most optimal Wordle solvers in the world. It can solve all 2315 puzzles with a limit of 5 guesses for all the puzzles in easy mode with an average of 3.421 guesses. The suggested starting word is SALET.

If you want to run this code, make sure you have already followed these rules shown here:

1. After downloading the word list, make sure that the names should have their correct spelling or space bar, eg "proper word.txt", not "proper-word.txt" or "proper word (1).txt"
<img width="798" height="213" alt="Screenshot 2026-05-02 at 2 18 48 AM" src="https://github.com/user-attachments/assets/85e70241-5ebf-437e-bf8b-a0fe8d23e622" />

2. Next, download `reportlab` to visualise the decision tree. In your terminal, type:

```bash
pip install reportlab
```


to successfully install the package.

There are four modes for the Wordle analysis, which are:
1. The post-game analysis: After playing today's Wordle puzzle, you can type the stats in your input, type like, `salet __gy_`, "g" means "green", "y" means "yellow", "_" means "grey".
2. 500 Random tests: It will randomly pick 500 unique Wordle puzzles with your hard mode suggestions, starting word and the LIMIT (higher is better for precision)
3. There is a bot playthrough, it will default to SALET as the starting word. You must type a word that is included in the answer list. If not, it might cause significant barriers or errors for the bot's runthrough.
4. Cumulative mode: The bot will run through all 2315 puzzles with the settings you've chosen. It might take about 30-45 minutes to do a 100-LIMIT full theoretical, perfect play of the starting word SALET in easy mode. Hard mode might take a shorter time due to the filtering of remaining words. Also a PDF of the decision tree and a .txt file will be automatically exported to your folder, eg /Users/XXXXX/PycharmProjects/WordleBot/main.py. The decision tree can be used for reference for beginner players. You can also change the colour of the tiles with the hex codes manually, though this is highly subjective and optional.
<img width="385" height="631" alt="Screenshot 2026-05-02 at 2 34 25 AM" src="https://github.com/user-attachments/assets/84c1bab6-0999-45c5-bd5a-4425d3f4f5d5" />

<img width="1049" height="845" alt="Screenshot 2026-05-04 at 4 51 49 PM" src="https://github.com/user-attachments/assets/fc80a309-fda0-458e-a181-32996cedd5bf" />

## Results (NOT fully tested) (You may go to https://freshman.dev/wordle/leaderboard?latest=true)

| Starting word | Average | Tree size obtained | Method      | Mode | WordLists  | Worst case |
| ------------- | ------- | ------------------ | ----------- | ---- | ---------- | ---------- |
| salet         | ~3.4212 | 7920               | Tree search | Easy | Std (Orig) | 5          |
| reast         | ~3.4225 | 7923               | Tree search | Easy | Std (Orig) | 5          |
| crate         | ~3.4238 | 7926               | Tree search | Easy | Std (Orig) | 5          |
| trace         | ~3.4238 | 7926               | Tree search | Easy | Std (Orig) | 5          |
| slate         | ~3.4247 | 7928               | Tree search | Easy | Std (Orig) | 6          |
| crane         | ~3.4255 | 7930               | Tree search | Easy | Std (Orig) | 5          |
| carle         | ~3.4286 | 7937               | Tree search | Easy | Std (Orig) | 6          |
| slane         | ~3.4312 | 7943               | Tree search | Easy | Std (Orig) | 6          |
| carte         | ~3.4337 | 7949               | Tree search | Easy | Std (Orig) | 6          |
| torse         | ~3.4342 | 7950               | Tree search | Easy | Std (Orig) | 5          |
| slant         | ~3.4346 | 7951               | Tree search | Easy | Std (Orig) | 5          |
| trice         | ~3.4350 | 7952               | Tree search | Easy | Std (Orig) | 5          |
| least         | ~3.4359 | 7954               | Tree search | Easy | Std (Orig) | 6          |
| trine         | ~3.4368 | 7956               | Tree search | Easy | Std (Orig) | 5          |
| prate         | ~3.4376 | 7958               | Tree search | Easy | Std (Orig) | 5          |
| slart         | ~3.4394 | 7962               | Tree search | Easy | Std (Orig) | 5          |
| caret         | ~3.4407 | 7965               | Tree search | Easy | Std (Orig) | 5          |
| clast         | ~3.4424 | 7969               | Tree search | Easy | Std (Orig) | 5          |
| carse         | ~3.4428 | 7970               | Tree search | Easy | Std (Orig) | 6          |
| train         | ~3.4437 | 7972               | Tree search | Easy | Std (Orig) | 5          |
| stare         | ~3.4445 | 7974               | Tree search | Easy | Std (Orig) | 5          |
| peart         | ~3.4476 | 7981               | Tree search | Easy | Std (Orig) | 6          |
| saint         | ~3.4480 | 7982               | Tree search | Easy | Std (Orig) | 5          |
| crone         | ~3.4489 | 7984               | Tree search | Easy | Std (Orig) | 5          |
| stane         | ~3.4493 | 7985               | Tree search | Easy | Std (Orig) | 6          |
| reist         | ~3.4502 | 7987               | Tree search | Easy | Std (Orig) | 5          |
| plate         | ~3.4510 | 7989               | Tree search | Easy | Std (Orig) | 6          |
| soare         | ~3.4545 | 7997               | Tree search | Easy | Std (Orig) | 6          |
| roate         | ~3.4558 | 8000               | Tree search | Easy | Std (Orig) | 5          |
| sault         | ~3.4579 | 8005               | Tree search | Easy | Std (Orig) | 6          |
| arose         | ~3.4605 | 8011               | Tree search | Easy | Std (Orig) | 5          |
| raise         | ~3.4618 | 8014               | Tree search | Easy | Std (Orig) | 5          |
| gamer         | ~3.5478 | 8213               | Tree search | Easy | Std (Orig) | 5          |
| zizit         | ~3.9560 | 9158               | Tree search | Easy | Std (Orig) | 6          |
| salet         | ~3.5093 | 8124               | Tree search | Hard | Std (Orig) | 6          |
| trope         | ~3.5504 | 8219               | Tree search | Hard | Std (Orig) | 6          |
| clasp         | ~3.5728 | 8271               | Tree search | Hard | Std (Orig) | 6          |
| cinqs         | ~3.7733 | 8735               | Tree search | Hard | Std (Orig) | 6          |
| crate         | ~3.4454 | 7976               | Tree search | Easy | Only Ans   | 6          |

Stats:

SALET: Easy mode
1. 0
2. 78
3. 1223
4. 975
5. 39
6. 0

SALET: Hard mode
1. 0
2. 121
3. 1041
4. 1014
5. 131
6. 8

