# Blackjack terminal game without external libraries

class PRNG:
    def __init__(self, seed_text):
        if not seed_text:
            seed_text = "default-seed"
        self.state = self._seed_from_text(seed_text)
        if self.state == 0:
            self.state = 1

    def _seed_from_text(self, text):
        state = 0
        for character in text:
            state = (state * 131) % 2147483647
            state = (state + ord(character)) % 2147483647
        return state

    def next_int(self):
        self.state = (1103515245 * self.state + 12345) % 2147483647
        if self.state <= 0:
            self.state += 2147483646
        return self.state

    def randint(self, low, high):
        if high < low:
            high = low
        value = self.next_int()
        return low + (value % (high - low + 1))


class Card:
    SUIT_NAMES = {
        "S": "Spades",
        "H": "Hearts",
        "D": "Diamonds",
        "C": "Clubs",
    }
    RANK_NAMES = {
        "2": "Two",
        "3": "Three",
        "4": "Four",
        "5": "Five",
        "6": "Six",
        "7": "Seven",
        "8": "Eight",
        "9": "Nine",
        "10": "Ten",
        "J": "Jack",
        "Q": "Queen",
        "K": "King",
        "A": "Ace",
    }

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def value(self):
        if self.rank == "A":
            return 11
        if self.rank in ("K", "Q", "J", "10"):
            return 10
        return int(self.rank)

    def label(self):
        return self.rank + self.suit

    def description(self):
        rank_name = self.RANK_NAMES.get(self.rank, self.rank)
        suit_name = self.SUIT_NAMES.get(self.suit, self.suit)
        return rank_name + " of " + suit_name

    def __str__(self):
        return self.label()


class Hand:
    def __init__(self, owner):
        self.owner = owner
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def best_value(self):
        total = 0
        soft_aces = 0
        for card in self.cards:
            total += card.value()
            if card.rank == "A":
                soft_aces += 1
        while total > 21 and soft_aces > 0:
            total -= 10
            soft_aces -= 1
        return total, soft_aces

    def total(self):
        total, _ = self.best_value()
        return total

    def is_soft(self):
        _, soft_aces = self.best_value()
        return soft_aces > 0

    def is_blackjack(self):
        return len(self.cards) == 2 and self.total() == 21

    def is_bust(self):
        return self.total() > 21

    def show(self, reveal_all=True):
        if not self.cards:
            return "(no cards)"
        if not reveal_all:
            if len(self.cards) < 2:
                return self.cards[0].description()
            remaining = ", ".join(card.description() for card in self.cards[1:])
            return "[Hidden], " + remaining
        return ", ".join(card.description() for card in self.cards)


class Deck:
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    SUITS = ["S", "H", "D", "C"]

    def __init__(self, prng, num_decks):
        self.prng = prng
        self.num_decks = num_decks
        self.cards = []
        self.index = 0
        self.reset()

    def reset(self):
        self.cards = []
        for _ in range(self.num_decks):
            for suit in self.SUITS:
                for rank in self.RANKS:
                    self.cards.append(Card(rank, suit))
        self.shuffle()
        self.index = 0

    def shuffle(self):
        last_index = len(self.cards) - 1
        while last_index > 0:
            swap_index = self.prng.randint(0, last_index)
            self.cards[last_index], self.cards[swap_index] = self.cards[swap_index], self.cards[last_index]
            last_index -= 1

    def draw(self):
        if self.index >= len(self.cards):
            self.reset()
        card = self.cards[self.index]
        self.index += 1
        return card

    def remaining(self):
        return len(self.cards) - self.index


class BlackjackGame:
    def __init__(self):
        self.player_name = self.prompt_player_name()
        self.prng = PRNG(self.prompt_seed())
        self.deck = Deck(self.prng, 6)
        self.chips = 200
        self.round_number = 1
        self.stats = {
            "wins": 0,
            "losses": 0,
            "pushes": 0,
            "blackjacks": 0,
        }

    def prompt_player_name(self):
        print("Welcome to Blackjack!")
        print("Leave the name empty to use 'Player'.")
        name = input("Enter your name: ").strip()
        if not name:
            name = "Player"
        return name

    def prompt_seed(self):
        print()
        print("Before we begin, type a random phrase to shuffle the deck.")
        print("The game does not use Python's random module, so your input seeds the cards.")
        seed = input("Enter seed text (or press Enter to accept default): ")
        if not seed:
            seed = "default-seed"
        print()
        return seed

    def explain_rules(self):
        print("--------- Game Rules ---------")
        print("- Beat the dealer by getting as close to 21 as possible without going over.")
        print("- Face cards count as 10, Aces count as 1 or 11, other cards are face value.")
        print("- Dealer hits on soft 17 (Ace counted as 11).")
        print("- Blackjack pays 3:2, regular wins pay 1:1, pushes return your bet.")
        print("- You start with 200 chips. Minimum bet is 1 chip per hand.")
        print("- Commands: 'h' to hit, 's' to stand, 'd' to double (first action only).")
        print("- Type 'q' during betting to leave the table.")
        print("--------------------------------")
        print()

    def ensure_deck_depth(self):
        if self.deck.remaining() < 15:
            print("Shuffling a fresh shoe...")
            self.deck.reset()
            print()

    def take_bet(self):
        while True:
            print(self.player_name + ", you have " + str(self.chips) + " chips.")
            bet_input = input("Place your bet (or 'q' to quit): ").strip().lower()
            if bet_input == "q":
                return None
            if not bet_input:
                print("Please enter a number.")
                continue
            if not self.is_integer(bet_input):
                print("Bets must be whole numbers.")
                continue
            bet = int(bet_input)
            if bet <= 0:
                print("Bet must be at least 1 chip.")
                continue
            if bet > self.chips:
                print("You cannot bet more chips than you have.")
                continue
            return bet

    def is_integer(self, text):
        if text.startswith("-"):
            return text[1:].isdigit()
        return text.isdigit()

    def show_table(self, player_hand, dealer_hand, hide_dealer=True):
        print("Dealer's hand:")
        print("  " + dealer_hand.show(reveal_all=not hide_dealer))
        if hide_dealer:
            print("  Total: ?")
        else:
            print("  Total: " + str(dealer_hand.total()))
        print()
        print(self.player_name + "'s hand:")
        print("  " + player_hand.show())
        print("  Total: " + str(player_hand.total()))
        print()

    def player_action(self, player_hand, dealer_hand, bet):
        while True:
            allow_double = (len(player_hand.cards) == 2 and self.chips >= bet)
            prompt = "Choose action: (h)it, (s)tand"
            if allow_double:
                prompt += ", (d)ouble"
            prompt += ": "
            choice = input(prompt).strip().lower()
            if choice in ("hit", "h"):
                new_card = self.deck.draw()
                player_hand.add_card(new_card)
                print("You draw: " + new_card.description())
                print("New total: " + str(player_hand.total()))
                print()
                if player_hand.is_bust():
                    return bet
                continue
            if choice in ("stand", "s"):
                return bet
            if allow_double and choice in ("double", "d"):
                self.chips -= bet
                bet *= 2
                new_card = self.deck.draw()
                player_hand.add_card(new_card)
                print("You double down and draw: " + new_card.description())
                print("Final total: " + str(player_hand.total()))
                print()
                return bet
            print("Invalid choice, try again.")

    def dealer_turn(self, dealer_hand):
        print("Dealer reveals their hidden card...")
        print("Dealer's hand: " + dealer_hand.show())
        print("Dealer total: " + str(dealer_hand.total()))
        print()
        while True:
            total = dealer_hand.total()
            if total > 21:
                print("Dealer busts!")
                print()
                break
            if total < 17:
                new_card = self.deck.draw()
                dealer_hand.add_card(new_card)
                print("Dealer hits and draws: " + new_card.description())
                continue
            if total == 17 and dealer_hand.is_soft():
                new_card = self.deck.draw()
                dealer_hand.add_card(new_card)
                print("Dealer hits soft 17 and draws: " + new_card.description())
                continue
            print("Dealer stands with " + str(total) + ".")
            print()
            break

    def settle_round(self, player_hand, dealer_hand, bet, player_busted):
        player_total = player_hand.total()
        dealer_total = dealer_hand.total()
        if player_busted:
            print("You bust and lose " + str(bet) + " chips.")
            self.stats["losses"] += 1
            return -bet
        if dealer_hand.is_bust():
            winnings = bet * 2
            self.chips += winnings
            print("Dealer busts. You win " + str(winnings - bet) + " chips!")
            self.stats["wins"] += 1
            return bet
        if player_total > dealer_total:
            winnings = bet * 2
            self.chips += winnings
            print("You win the hand! Payout: " + str(winnings - bet) + " chips.")
            self.stats["wins"] += 1
            return bet
        if player_total == dealer_total:
            self.chips += bet
            print("Push. Your bet is returned.")
            self.stats["pushes"] += 1
            return 0
        print("Dealer wins. You lose " + str(bet) + " chips.")
        self.stats["losses"] += 1
        return -bet

    def play_round(self):
        self.ensure_deck_depth()
        bet = self.take_bet()
        if bet is None:
            return False
        self.chips -= bet
        print()
        player_hand = Hand(self.player_name)
        dealer_hand = Hand("Dealer")
        player_hand.add_card(self.deck.draw())
        dealer_hand.add_card(self.deck.draw())
        player_hand.add_card(self.deck.draw())
        dealer_hand.add_card(self.deck.draw())
        self.show_table(player_hand, dealer_hand, hide_dealer=True)
        if player_hand.is_blackjack():
            print("Blackjack! Let's check the dealer...")
            if dealer_hand.is_blackjack():
                print("Dealer also has blackjack. It's a push.")
                self.chips += bet
                self.stats["pushes"] += 1
            else:
                payout = bet + ((bet * 3) // 2)
                self.chips += payout
                print("You are paid " + str(payout - bet) + " chips for blackjack!")
                self.stats["wins"] += 1
                self.stats["blackjacks"] += 1
            print()
            return True
        if dealer_hand.is_blackjack():
            print("Dealer reveals blackjack. You lose your bet of " + str(bet) + " chips.")
            self.stats["losses"] += 1
            print()
            return True
        bet = self.player_action(player_hand, dealer_hand, bet)
        player_busted = player_hand.is_bust()
        if player_busted:
            print("You bust with " + str(player_hand.total()) + ".")
            self.stats["losses"] += 1
            print()
            return True
        self.dealer_turn(dealer_hand)
        self.settle_round(player_hand, dealer_hand, bet, player_busted)
        print()
        return True

    def show_stats(self):
        print("--------- Session Summary ---------")
        print("Chips remaining: " + str(self.chips))
        print("Rounds played: " + str(self.stats["wins"] + self.stats["losses"] + self.stats["pushes"]))
        print("Wins: " + str(self.stats["wins"]))
        print("Losses: " + str(self.stats["losses"]))
        print("Pushes: " + str(self.stats["pushes"]))
        print("Blackjacks hit: " + str(self.stats["blackjacks"]))
        print("-----------------------------------")

    def wants_to_continue(self):
        if self.chips <= 0:
            print("You have run out of chips.")
            return False
        answer = input("Play another round? (y/n): ").strip().lower()
        return answer in ("y", "yes", "")

    def run(self):
        self.explain_rules()
        playing = True
        while playing and self.chips > 0:
            played = self.play_round()
            if not played:
                break
            playing = self.wants_to_continue()
            print()
        self.show_stats()
        print("Thanks for playing, " + self.player_name + "!")


def main():
    game = BlackjackGame()
    game.run()


if __name__ == "__main__":
    main()
