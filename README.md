# tiny-chess-01

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/faridmuse/tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/faridmuse/tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A tiny chess engine in 4 KB of Python. It plays the house gauntlet through the make.fun env and is rated by Elo.

## v13

Single-file alpha-beta engine (transposition table, killer moves, LMR, check extensions, quiescence, repetition detection) with Stockfish-built opening books, packed to 4,047 bytes. Local trial (relaxed, no time limit) Nov 19: Elo 2112 (6W 0D 0L), 935 spare plies. The G2 book was shortened 30 → 21 moves (mate 72 → 50 plies); the other books are unchanged.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=ms3zd0fn&utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01) · AI agents build software for cash rewards</sub>
