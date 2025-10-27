# Blackjack Terminal

A self-contained blackjack experience for the command line. The game mimics a casino six-deck shoe, runs entirely on the standard library, and even ships with its own pseudo-random number generator that is seeded by whatever phrase you type before play begins.

## Features
- Six-deck shoe with manual reshuffle when fewer than 15 cards remain
- Custom PRNG seeded from player input for deterministic replays when the same seed is used
- Player bankroll management starting at 200 chips with configurable bets and double downs
- Blackjack-specific rules: dealer hits soft 17, blackjacks pay 3:2, pushes return the bet
- Round-by-round narration and an end-of-session stats summary (wins/losses/pushes/blackjacks)

## Getting Started
1. Ensure Python 3.8+ is available.
2. From this directory run:

```bash
python main.py
```

3. Enter a player name (press Enter for the default) and provide any phrase to seed the shoe. Using the same phrase reproduces the same card order.

## Controls & Flow
- At the start of each round you must place a whole-number bet (`q` quits the game).
- During your turn choose: `h` to hit, `s` to stand, or `d` to double (only on the first decision when you have enough chips).
- The dealer reveals their hand after you stand or bust, hits until reaching at least 17, and draws on soft 17.
- Winnings are automatically paid out, and the game continues until you quit or run out of chips. A session summary appears at the end.

Use the project as a drop-in terminal game, a base for experimenting with blackjack logic, or a reference for simple PRNG implementations without third-party dependencies.
