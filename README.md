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
