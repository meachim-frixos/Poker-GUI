import random
import time
import numpy as np
import pandas as pd

from card import combinations, value_cards, best_cards


class Player:
    def __init__(self, name, chips, cards, seat_number,avatar_image):
        self.name = name
        self.avatar_image= avatar_image
        self.chips = chips
        self.turn = 0
        self.cards = cards
        self.showdown_value = 0

        self.seat_number = seat_number
        self.bet = 0
        self.best_five = cards
        self.decision = None
        self.raise_amount = 0
        self.bet_amount = 0
        self.valid_choice = None
        self.playing_for = 0

        self.valid_actions = []

        self.pre_flop_rank = 0
        self.flop_rank = 0
        self.turn_rank = 0
        self.river_rank = 0
        self.showdown_rank = 0

        self.current_rank = self.pre_flop_rank
        # Numbers should? be bellow 0.9 because playing the 10% best hands is the "tightest" a player should be
        # TODO # Maybe these should change every X games to make players less predictable...
        self.pre_flop_range = round(random.random() * 0.5 + 0.35, 2)
        self.flop_range = round(random.random() * 0.5 + 0.4, 2)
        self.turn_range = round(random.random() * 0.4 + 0.5, 2)
        self.river_range = round(random.random() * 0.3 + 0.6, 2)

        self.current_range = self.pre_flop_range

        self.bluff_probability = round(random.random() * 0.1, 2)  # likelihood of player bluffing
        self.limp_probability = round(random.random(), 2) * 0.4 + 0.6  # likelihood of player limping
        self.betting_aggression = round(random.random() * 1, 2)

        self.bluff = False
        self.limp = False
        self.bet_limit = 0

    def find_valid_actions(self, game):
        p = self
        p.valid_actions = []
        in_game = (p in game.hand_players)
        has_chips = p.chips > 0
        has_opponent = len(game.hand_players) > 1
        opponent_can_bet_more = sum(1 for p in game.hand_players if p.chips > 0) > 1
        has_max_bet = p.bet >= game.current_bet
        enough_to_call = p.chips > game.current_bet - p.bet
        minimum_bet = game.big_blind_amount
        minimum_raise = max(minimum_bet, game.previous_bet_amount)
        enough_to_bet = p.chips - game.current_bet + p.bet > minimum_bet
        enough_to_raise = p.chips - game.current_bet + p.bet > minimum_raise

        # TODO # Unable to fold if you have max bet makes sense logic wise, but game wise you should be able to fold
        #  whenever you want.

        if not in_game or not has_chips or not has_opponent or (has_max_bet and not opponent_can_bet_more):
            p.valid_actions = ["wait"]
            return

        if has_max_bet:
            p.valid_actions.append("check")
        elif not has_max_bet:
            p.valid_actions.append("fold")
            if enough_to_call:
                p.valid_actions.append("call")

        if enough_to_bet and not game.previous_bet:
            p.valid_actions.append("bet")
        elif enough_to_raise and game.previous_bet:
            p.valid_actions.append("raise")

        p.valid_actions.append("all-in")
        return

    def update_rank_range(self, game):
        player = self
        if game.state == 'pre_flop':
            player.current_range = player.pre_flop_range
            player.current_rank = player.pre_flop_rank
        elif game.state == 'flop':
            player.current_range = player.flop_range
            player.current_rank = player.flop_rank
        elif game.state == 'turn':
            player.current_range = player.turn_range
            player.current_rank = player.turn_rank
        elif game.state == 'river':
            player.current_range = player.river_range
            player.current_rank = player.river_rank
        else:
            print("----------------------UNKNOWN GAME STATE-----------------")
            player.current_range = 0
            player.current_rank = 0

    def decide_bet_limit(self, game):
        player = self
        if player.current_rank >= 0.75:
            player.bet_limit = 1
        elif player.current_rank > 0.4:
            player.bet_limit = np.exp(1.2 * player.current_rank) - 1.6
        else:
            player.bet_limit = 0

        if player.bluff:
            player.bet_limit += player.betting_aggression / 10

        player.bet_limit = round(player.bet_limit, 2)

        # If you are 90% in and someone raises you the remainder, you should probably be willing to put the rest in
        # regardless of what you have.
        if player.bet>0:
            if player.chips / player.bet < 0.1:
                player.bet_limit = 1

            elif player.chips / player.bet < 0.3 and player.current_rank >= 0.8:
                player.bet_limit = 1

    # If player choice is bet/raise, appropriately modifies bet/raise size
    def decide_bet_size(self, game):
        player = self
        amount_to_call = player.bet - game.current_bet
        minimum_bet = max(game.big_blind_amount, game.previous_bet_amount)
        bet_size_options = [minimum_bet, 4 * game.big_blind_amount, 0.3 * game.pot, 0.5 * game.pot, 0.75 * game.pot,
                            1 * game.pot, 2 * game.pot, 3 * game.pot,
                            4 * game.pot, player.chips]

        # If option is smaller than minimum bet ( pot is 3 and 0.3*3 =0.9< minimum bet), convert to minimum
        # If options is more than player can afford, convert to maximum (all-in)
        for i in range(0, len(bet_size_options)):
            if bet_size_options[i] < minimum_bet:
                bet_size_options[i] = minimum_bet

            if bet_size_options[i] + amount_to_call > player.chips:
                bet_size_options[i] = min(0, player.chips - amount_to_call)

        ####
        draw = round(random.random(), 2)
        if draw < player.current_rank:
            choice = (player.current_rank - draw) * (player.current_rank + 1) ** 4  # yields between 1 and 10 approx
            choice = np.clip(choice, 1, 10) - 1  # convert to 0-9 to be used as pointer for bet_size_options

        else:  # bet minimum
            choice = 0

        # Max number of chips player is willing to place in the game. Bet limit is 0-1 , multiplied by total player
        # chips in game
        chip_limit = player.bet_limit * (player.bet + player.chips)

        while bet_size_options[choice] + amount_to_call + player.bet > chip_limit:
            # Try next smaller choice of bet
            choice = max(0, choice - 1)
            # Should not run forever since one choice should be player all-in, This happens because in order to
            # decide player bet_size_options, we have first checked that a bet is possible

        bet_amount_choice = bet_size_options[choice]

        if player.decision == "bet":
            player.bet_amount = bet_amount_choice
        elif player.decision == "raise":
            player.raise_amount = bet_amount_choice

    # Decides what to do: check/fold,call,raise/bet/all-in
    def decides(self, game):
        """""""""
        # If current rank is within range:
            # Player wants to continue
                # If limp
                    # If can check, check
                    # Else call
                # Else IF player.bet/player.chips <= player bet limit
                    # Bet/raise
        # Else he wants to fold/check OR Bluff
            # If bluff, bluff
            # else 
                # If can check, check
                # If not, fold
        """""""""
        self.decision = None
        self.bet_amount = 0
        self.raise_amount = 0
        player = self
        player.limp = (random.random() > self.limp_probability)
        player.bluff = (random.random() * 0.5 > self.bluff_probability)

        amount_to_call = game.current_bet - player.bet

        player.update_rank_range(game)
        player.decide_bet_limit(game)

        player.find_valid_actions(game)
        # If wait is an option, always wait (should only happen when all other options are invalid)
        if "wait" in player.valid_actions:
            player.decision = "wait"
            return

        if player.current_rank >= player.current_range:
            if player.limp:
                if "check" in player.valid_actions:
                    player.decision = "check"
                elif "call" in player.valid_actions:
                    player.decision = "call"
                else:
                    player.decision = "fold"

            # TODO # Work on this elif statement
            elif player.bet / (player.chips + player.bet) < player.bet_limit:
                if "bet" in player.valid_actions:
                    player.decision = "bet"
                    player.bet_amount = game.pot * player.betting_aggression
                elif "raise" in player.valid_actions:
                    player.decision = "raise"
                    player.raise_amount = game.pot * player.betting_aggression * 2 ** player.betting_aggression
                elif "all-in" in player.valid_actions:
                    player.decision = "all-in"

                # If decided bet/raise is higher than player chips, convert to all-in
                if player.bet_amount >= player.chips - (
                        game.current_bet - player.bet) or player.raise_amount >= player.chips - (
                        game.current_bet - player.bet):
                    player.decision = "all-in"
                    player.bet_amount = 0
                    player.raise_amount = 0
            elif "check" in player.valid_actions:
                player.decision = "check"
            else:
                player.decision = "fold"
        else:
            if player.bluff:
                if "bet" in player.valid_actions:
                    player.decision = "bet"
                    player.bet_amount = game.pot * player.betting_aggression
                elif "raise" in player.valid_actions:
                    player.decision = "raise"
                    player.raise_amount = game.pot * player.betting_aggression
                elif "all-in" in player.valid_actions:
                    player.decision = "all-in"
                # Player bet/raise must be at least minimum (big blind or previous raise amount)
                player.bet_amount = max(game.big_blind_amount, player.bet_amount)
                player.raise_amount = max(game.previous_bet_amount, player.raise_amount)
                # If decided bet/raise is higher than player chips, convert to all-in
                if player.bet_amount >= player.chips - (
                        game.current_bet - player.bet) or player.raise_amount >= player.chips - (
                        game.current_bet - player.bet):
                    player.decision = "all-in"
                    player.bet_amount = 0
                    player.raise_amount = 0
            else:
                if "check" in player.valid_actions:
                    player.decision = "check"
                else:
                    player.decision = "fold"

        # TESTING
        d=random.random()
        if "check" in player.valid_actions:

            if d>0.6 and "bet" in player.valid_actions:
                player.decision="bet"
                player.bet_amount=game.big_blind_amount*(1+player.current_rank)
            elif player.current_rank>0.7 and "bet" in player.valid_actions:
                player.decision = "bet"
                player.bet_amount = game.big_blind_amount ** (1 + player.current_rank)
            else:
                player.decision="check"
        elif "call" in player.valid_actions:
            if d>0.5:
                player.decision="call"
            else:
                player.decision="fold"
        #TESTING


        # In any case, round bet amounts to whole numbers
        player.bet_amount = round(player.bet_amount)
        player.raise_amount = round(player.raise_amount)

    def decides_new(self, game):
        self.decision = None
        self.bet_amount = 0
        self.raise_amount = 0
        player = self
        rank = player.current_rank
        range = player.current_rank

        player.limp = (random.random() > self.limp_probability)
        player.bluff = (random.random() * 0.5 > self.bluff_probability)

        player.update_rank_range(game)
        player.decide_bet_limit(game)
        player.find_valid_actions(game)

        # If wait is an option, always wait (should only happen when all other options are invalid)
        if "wait" in player.valid_actions:
            player.decision = "wait"
            return

        # Pick "decision" based on Rank, Range
        if rank > range:
            if player.limp:
                pass
            else:
                pass
        else:  # (rank<=range)
            pass
            if player.bluff:
                pass
            else:
                pass

        # In any case, round bet amounts to whole numbers
        player.bet_amount = round(player.bet_amount)
        player.raise_amount = round(player.raise_amount)

    def rank_flop(self, game):
        # Return ranking of player hand against all possible hands creatable with specific flop
        # Create dataframe containing value of current flop (3)+(2)all possible hands
        # 47 choose 2 entries (52 minus flop minus player cards)
        # Whole deck
        deck_c = game.deck.copy()
        flop_cards = deck_c[0:3]
        player_cards = self.cards
        # Remove seen cards
        for card in flop_cards:
            deck_c.remove(card)
        for card in player_cards:
            deck_c.remove(card)
        possible_opponent_hands = combinations(deck_c, 2)
        # Prepare dataframe
        df = pd.DataFrame(index=range(0, len(possible_opponent_hands)))
        df["Hands"] = [[flop_cards[0], flop_cards[1], flop_cards[2]]] * len(possible_opponent_hands)
        hand_list = [[tup[0], tup[1]] for tup in possible_opponent_hands]

        df["POP"] = hand_list
        df["Combos"] = df["Hands"] + df["POP"]
        del df["POP"], df["Hands"]
        df["Score"] = df["Combos"].apply(value_cards)

        player_hand = flop_cards + player_cards
        player_flop_value = value_cards(player_hand)

        count = df['Score'].apply(lambda score: 1 if score <= player_flop_value else 0).sum()
        percentage_beat = count / len(possible_opponent_hands)

        self.flop_rank = round(percentage_beat, 4)

    def rank_turn(self, game):
        # Return ranking of player hand against all possible hands creatable with specific turn
        # Create dataframe containing value of current turn (4)+(2) all possible hands

        # Whole deck
        deck_c = game.deck.copy()
        turn_cards = deck_c[0:4]
        player_cards = self.cards
        # Remove seen cards
        for card in turn_cards:
            deck_c.remove(card)
        for card in player_cards:
            deck_c.remove(card)
        possible_opponent_hands = combinations(deck_c, 2)
        # Prepare dataframe
        df = pd.DataFrame(index=range(0, len(possible_opponent_hands)))
        df["Hands"] = [[turn_cards[0], turn_cards[1], turn_cards[2], turn_cards[3]]] * len(possible_opponent_hands)
        hand_list = [[tup[0], tup[1]] for tup in possible_opponent_hands]

        df["POP"] = hand_list
        df["Combos"] = df["Hands"] + df["POP"]
        del df["POP"], df["Hands"]
        df["Score"] = df["Combos"].apply(lambda cards: best_cards(cards)[1])

        player_hand = turn_cards + player_cards
        player_turn_value = best_cards(player_hand)[1]

        count = df['Score'].apply(lambda score: 1 if score <= player_turn_value else 0).sum()
        percentage_beat = count / len(possible_opponent_hands)
        self.turn_rank = round(percentage_beat, 4)

    def rank_river(self, game):
        # Return ranking of player hand against all possible hands creatable with specific river
        # Create dataframe containing value of current river (5)+(2) all possible hands

        # Whole deck
        deck_c = game.deck.copy()
        river_cards = deck_c[0:5]
        player_cards = self.cards
        # Remove seen cards
        for card in river_cards:
            deck_c.remove(card)
        for card in player_cards:
            deck_c.remove(card)
        possible_opponent_hands = combinations(deck_c, 2)
        # Prepare dataframe
        df = pd.DataFrame(index=range(0, len(possible_opponent_hands)))
        df["Hands"] = [[river_cards[0], river_cards[1], river_cards[2], river_cards[3], river_cards[4]]] * len(
            possible_opponent_hands)
        hand_list = [[tup[0], tup[1]] for tup in possible_opponent_hands]

        df["POP"] = hand_list
        df["Combos"] = df["Hands"] + df["POP"]
        del df["POP"], df["Hands"]
        df["Score"] = df["Combos"].apply(lambda cards: best_cards(cards)[1])

        player_hand = river_cards + player_cards
        player_river_value = best_cards(player_hand)[1]

        count = df['Score'].apply(lambda score: 1 if score <= player_river_value else 0).sum()
        percentage_beat = count / len(possible_opponent_hands)
        self.river_rank = round(percentage_beat, 4)

    def rank_starting_hand(self, data_loc="Data/hand_rankings_500.xlsx"):
        df = pd.read_excel(data_loc)
        search = [self.cards[0].value, self.cards[0].suit, self.cards[1].value, self.cards[1].suit]
        mask = df.apply(lambda row: all(row.iloc[i] == search[i] for i in range(len(search))), axis=1)
        result = df[mask]
        # print(f"Length result is"{len(result)})
        # print(len(result.iloc[0]))
        if result.empty:
            print(f"The valuing function failed, while searching for:{search}")
            print(f"Result was:")
            # print(result)
            self.pre_flop_rank = 0
        else:
            self.pre_flop_rank = round(result.iloc[0, 4], 4)

    def check_valid_choice(self, game):
        player = self
        in_game = (player in game.hand_players)
        has_chips = player.chips > 0
        has_opponent = len(game.hand_players) > 1
        opponent_can_bet_more = sum(1 for p in game.hand_players if p.chips > 0) > 1
        player_has_max_bet = player.bet >= game.current_bet
        # TODO # Sometimes player bets without opponent that can reply...
        if in_game and has_chips and has_opponent and (
                opponent_can_bet_more or (not opponent_can_bet_more and not player_has_max_bet)):
            # If player in game, and player has chips, and opponents exist, and (opponent has chips to bet or
            # opponent doesn't, and acting player can call)

            # Move to check validity of player decision
            # First check if raise should become bet, or bet should become raise.
            if player.decision == "bet" and game.previous_bet == True:
                # bet becomes raise
                # print("Bet becomes raise.")
                player.decision = "raise"
                player.raise_amount = player.bet_amount
                player.bet_amount = 0
                player.valid_choice = False
            elif player.decision == "raise" and game.previous_bet == False:
                # raise becomes bet
                # print("Raise becomes bet.")
                player.decision = "bet"
                player.bet_amount = player.raise_amount
                player.raise_amount = 0
                player.valid_choice = False

            # Now check for validity
            if player.decision is None or player.decision == "fold":
                player.valid_choice = True  # folding or doing nothing is always valid.
                return
                # Doing nothing should only happen when player is out.
            elif player.decision == "check":
                if player.bet != game.current_bet:  # Can't check if you need to put money in pot
                    # print("Can't check, so you fold instead")
                    # print("Must chose fold or call.")
                    player.decision = "fold"
                    player.valid_choice = False
                else:
                    player.valid_choice = True
                return
            elif player.decision == "call":
                if player.chips < game.current_bet - player.bet:  # Can't call, not enough chips

                    # print(
                    #   "Player chose call, but doesn't have enough chips to cover current bet.")  # p.chips > 0 = True
                    player.decision = "all-in"

                    # print("Player goes all-in instead.")
                    player.valid_choice = False
                else:  # Can call, valid choice
                    player.valid_choice = True
                return
            elif player.decision == "bet":
                # Adjust player bet to minimum
                if player.bet_amount >= game.big_blind_amount:
                    pass
                else:
                    if player.chips > game.big_blind_amount:
                        player.bet_amount = game.big_blind_amount
                        player.valid_choice = False
                        # print("Player tried to bet an amount smaller than the minimum allowed, so his bet was
                        # adjusted")
                    else:
                        player.decision = "all-in"
                        player.bet = 0
                # TODO# In the case of invalid bet amount, player.decision will show as true ( if player has enough
                #  chips ) but choice was not valid.
                if player.chips >= game.current_bet - player.bet + player.bet_amount:  # Has enough to call AND bet
                    player.valid_choice = True
                elif player.chips >= game.current_bet - player.bet:  # Has enough to call only
                    player.decision = "call"
                    print("Player tried to bet, but didn't have enough. Player calls instead.")
                    player.valid_choice = False
                else:  # Chips>0 from beginning
                    player.bet_amount = 0
                    player.decision = "all-in"

                    # print("Player tried to bet, but didn't even have enough to call. Player goes all-in instead")
                    player.valid_choice = False

            elif player.decision == "raise":
                if player.chips >= game.current_bet - player.bet + player.raise_amount:  # Has enough to call AND raise
                    if player.raise_amount >= game.big_blind_amount and player.raise_amount >= game.previous_bet_amount:  # Raise amount is valid
                        player.valid_choice = True

                    else:  # Raise amount is invalid but player has enough to raise the minimum
                        # print("Raise amount was invalid.")
                        # print("Raise amount adjusted to minimum raise amount.")
                        player.raise_amount = max(game.big_blind_amount, game.previous_bet_amount)
                        if player.chips <= game.current_bet - player.bet + player.raise_amount:
                            player.decision = "all-in"
                            player.valid_choice = False

                elif player.chips > game.current_bet - player.bet:  # Has enough to call but not raise
                    # print(F"{player.name} doesn't have enough to raise, they call instead.")
                    player.decision = "call"
                    player.valid_choice = False
                else:  # Has chips>0 but cant raise or call
                    player.decision = "all-in"
                    player.valid_choice = False
            # Since player in game, has opponents and has chips, all-in is always valid.
            elif player.decision == "all-in":
                player.valid_choice = True
            else:
                print("Player decision not recognised")
                player.valid_choice = False
        else:
            # If no opponents exist or player not in game, or player is in game but has 0 chips, player waits

            player.decision = "Wait"
            self.valid_choice = True

    def checks(self):
        pass

    def bets(self, game, bet_amount):
        self.calls(game)
        game.pot += bet_amount
        game.current_bet += bet_amount
        self.bet = game.current_bet
        self.chips -= bet_amount
        game.actions_remaining = len(game.hand_players)
        # Bet and all-in *decisions* have potential to make next player decision and action a raise.
        # Call also uses bet *action*, but decision will be "call" so next player action isn't a raise.
        if self.decision == "bet":
            game.previous_bet = True
            game.previous_bet_amount = bet_amount
        elif self.decision == "all-in" and self.bet > game.current_bet:
            # If bet action is result of all-in and if all in increased current bet, next action is raise not bet.
            game.previous_bet = True
            temp = game.previous_bet_amount
            game.previous_bet_amount = max(bet_amount, temp)
        elif self.decision == "raise":
            game.previous_bet = True
            game.previous_bet_amount = self.raise_amount

    def calls(self, game):
        self.chips -= game.current_bet - self.bet
        game.pot += game.current_bet - self.bet
        self.bet = game.current_bet

    def raises(self, game, raise_amount):
        self.calls(game)
        self.bets(game, raise_amount)
        game.previous_bet_amount = raise_amount

    def folds(self, game):
        game.hand_players.remove(self)
        self.cards = None

    def all_ins(self, game):

        self.bet += self.chips
        game.pot += self.chips
        previous_current_bet = game.current_bet
        game.current_bet = max(previous_current_bet, self.bet)
        self.chips = 0
        # If all in resulted in increased current bet, other players act
        if game.current_bet != previous_current_bet:
            game.actions_remaining = len(game.hand_players)

    def takes_action(self, game,gui,decision, bet_amount=0, raise_amount=0):
        time.sleep(gui.delay)
        if decision == "check":
            self.checks()
            gui.check_sound.play()
        elif decision == "fold":
            self.folds(game)
            gui.fold_sound.play()
        elif decision == 'call':
            self.calls(game)
            gui.call_sound.play()
        elif decision == 'raise':
            self.raises(game, raise_amount=raise_amount)
            gui.raise_sound.play()
        elif decision == "bet":
            self.bets(game, bet_amount=bet_amount)
            gui.bet_sound.play()
        elif decision == 'all-in':
            self.all_ins(game)
            gui.all_in_sound.play()
        elif decision == 'none':
            pass
        game.actions_remaining -= 1


    # TODO # Decision will be function of:
    #  -Player hand ranking at current stage.
    #  -Current size of pot
    #  -Voluntarily put money in pot of each hand player?
    #  -Player location on the table. (Weight decreases as we move from pre-flop -> showdown
    #  -Potential winnings and losses (If heads up against a player with very few chips, his all-in shouldn't scare you.
    #  -

    # TODO # Create player attributes
    #  -Bluff probability: likelihood of other attributes being increased
    #   by some value resulting in betting regardless of hand
    #  -range ( How tight player is pre-flop): Use player.pre_flop_rank.
    #   Range=0.9 means player only plays hands that rank in the top 10%
    #  -projected strength: How likely a player is to stay in a hand that he is not ranked highly

    # TODO -All attributes contribute to player betting limit: 0-1 indicating what percentage of current chips
    #   player is willing to bet this game.
