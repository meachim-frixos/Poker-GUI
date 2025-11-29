# self.cards = draw_cards(5 + num_p * 2)
"""""""""
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


def decides(self, game):
    self.decision = None
    self.bet_amount = 0
    self.raise_amount = 0

    if self.pre_flop_rank < 0.1 and self.bet < game.current_bet and len(game.hand_players) != 1:
        self.decision = "fold"
    elif self.pre_flop_rank < 0.5:
        if self.bet == game.current_bet:
            self.decision = "check"
        else:
            self.decision = "call"
    elif self.pre_flop_rank < 0.8:
        if game.pot <= 50:
            self.decision = "bet"
            self.bet_amount = max(game.big_blind_amount, game.pot * 0.5)
            # self.bet_amount = game.big_blind_amount * 0.5
        elif self.bet == game.current_bet:
            self.decision = "check"
        elif (game.current_bet - self.bet) / (game.pot / len(
                game.hand_players)) < 1:  # If amount needed to call is less than pot/num players in game.
            self.decision = "call"
        else:
            self.decision = "fold"
    elif self.pre_flop_rank >= 0.8 and self.chips > 0:
        self.decision = "all-in"
    else:
        pass
    self.check_valid_choice(game)
    if self.valid_choice:
        pass
    else:
        pass
        # print("Invalid Choice was entered")  # TODO# If invalid choice is made, should ask player for another choice
    if self.decision is None:
        pass
        # print("Choice is none")

def decides_2(self, game):
    self.decision = None
    self.bet_amount = 0
    self.raise_amount = 0

    player = self
    if game.state == 'pre_flop':
        bet_limit = player.pre_flop_range
    elif game.state == 'flop':
        bet_limit = player.flop_range
    elif game.state == 'turn':
        bet_limit = player.turn_range
    elif game.state == 'river':
        bet_limit = player.river_range
    elif game.state == "showdown":
        bet_limit = player.showdown_range
    else:
        bet_limit = 1
        print("----------------------UNKNOWN GAME STATE-----------------")

    # If bad hand, and can't check, and opponents exist
    if bet_limit < 0.25 and self.bet < game.current_bet and len(game.hand_players) != 1:
        self.decision = "fold"
    # Else if mediocre
    elif bet_limit >= 0.25:
        # If can check, check
        if self.bet == game.current_bet:
            self.decision = "check"
        # If can't, call
        else:
            self.decision = "call"
    elif bet_limit < 0.8:
        if game.pot <= 50:
            self.decision = "bet"
            self.bet_amount = max(game.big_blind_amount, game.pot * 0.5)
            # self.bet_amount = game.big_blind_amount * 0.5
        elif self.bet == game.current_bet:
            self.decision = "check"
        elif (game.current_bet - self.bet) / (game.pot / len(
                game.hand_players)) < 1:  # If amount needed to call is less than pot/num players in game.
            self.decision = "call"
        else:
            self.decision = "fold"
    elif bet_limit >= 0.8 and self.chips > 0:
        self.decision = "all-in"
    else:
        pass
    self.check_valid_choice(game)
    if self.valid_choice:
        pass
    else:
        pass
        # print("Invalid Choice was entered")  # TODO# If invalid choice is made, should ask player for another choice
    if self.decision is None:
        pass
        # print("Choice is none")

def new_decides(self, game):
    player = self
    if game.state == 'pre_flop':
        bet_limit = player.pre_flop_range
    elif game.state == 'flop':
        bet_limit = player.flop_range
    elif game.state == 'turn':
        bet_limit = player.turn_range
    elif game.state == 'river':
        bet_limit = player.river_range
    elif game.state == "showdown":
        bet_limit = player.showdown_range
    else:
        bet_limit = 1
    player.decision = None
    player.bet_amount = 0
    player.raise_amount = 0
    amount_to_call = max(0, game.current_bet - player.bet)

    print(f"{bet_limit},{amount_to_call / (player.chips + player.bet)}")
    if player.chips == 0:
        player.decision = "wait"

    elif amount_to_call / (player.chips + player.bet) > bet_limit:
        player.decision = "check"  # will turn into fold if invalid
        # player.decision="fold"
    elif player.bet / (player.chips + player.bet) <= bet_limit:

        amount = (bet_limit - (player.bet / player.chips)) * player.chips

        if amount > amount_to_call:
            player.decision = "bet"
            player.bet_amount = round(min(2 * game.pot, (amount - amount_to_call) * player.betting_aggression), 0)
            # player.bet_amount = round((amount - amount_to_call) * player.betting_aggression, 0)
        else:
            if player.bet < game.current_bet:
                player.decision = "call"
            elif player.bet >= game.current_bet:
                player.decision = "check"


    else:
        player.decision = "check"

    player.check_valid_choice(game)
    # min(game.big_blind_amount, (amount-amount_to_call) * player.betting_aggression)

"""""""""

"""""""""
def new_value_cards(cards):
    value = 0.0

    # Sort cards in descending order of value
    cards = sorted(cards, key=lambda card: card.value, reverse=True)
    counts = []
    # Counts occurrences of each card value in 5 cards
    for number in range(2, 15):
        counts.append(sum(1 for card in cards if card.value == number))
    # If there are 5 "1"s in counts, we have only unique values of cards (no pairs,triplets,quads,full house)
    if counts.count(1) == 5:
        flush = False
        straight = False
        # CHECK straight
        if cards[0].value == cards[1].value + 1:
            if cards[0].value == cards[2].value + 2:
                if cards[0].value == cards[3].value + 3:
                    if cards[0].value == cards[4].value + 4:
                        straight = True
        # CHECK flush
        if cards[0].suit == cards[1].suit:
            if cards[0].suit == cards[2].suit:
                if cards[0].suit == cards[3].suit:
                    if cards[0].suit == cards[4].suit:
                        flush = True
        # CHECK straight-flush
        if straight and flush:
            if cards[0].value == 14:
                # Roya flush
                value = 10 * 10 ** 10
                return value
            # base straight-flush value
            value = 8 * 10 ** 10
            # value contribution of each card
            for i in range(1, 6):
                value += cards[i - 1].value * 10 ** (10 - i * 2)
            return value
        elif straight:
            # base straight value
            value = 4 * 10 ** 10
            # value contribution of each card (unnecessary in this case)
            for i in range(1, 6):
                value += cards[i - 1].value * 10 ** (10 - i * 2)
            return value
        elif flush:
            # base flush value
            value = 5 * 10 ** 10
            # value contribution of each card
            for i in range(1, 6):
                value += cards[i - 1].value * 10 ** (10 - i * 2)
            return value
        else:
            # base high card value
            value = 1 * 10 ** 10
            # value contribution of each card
            for i in range(1, 6):
                value += cards[i - 1].value * 10 ** (10 - i * 2)
            return value
    elif counts.count(2) == 1:

        # If there is 1 "2", there exists one pair.
        # One pair or full house
        if counts.count(3) == 1:
            # If there also exists 1 "3", there also exists a triple.
            # Base full house value
            value = 6 * 10 ** 10
            # find the triplet
            triplet_value = counts.index(3) + 2
            value += triplet_value * 8 ** 10
            # find the double
            double_value = counts.index(2) + 2
            value += double_value * 6 ** 10
            return value
        else:
            # Base one pair value
            value = 1 * 10 ** 10
            # find the pair value
            pair_value = counts.index(2) + 2
            value += pair_value * 10 ** 8
            # remove pair from cards
            remove = [card for card in cards if card.value == pair_value]
            cards = [card for card in cards if card not in remove]
            # loop through remaining cards and add value
            for i in range(1, 4):
                value += cards[i - 1].value * 10 ** (10 - (i + 1) * 2)
            return value

    elif counts.count(2) == 2:
        # Base Two pair value
        value = 2 * 10 ** 10
        # find the lowest pair value
        low_pair_value = counts.index(2) + 2
        value += low_pair_value * 10 ** 6
        # remove the lowest pair from cards
        len(cards)
        remove = [card for card in cards if card.value == low_pair_value]
        cards = [card for card in cards if card not in remove]
        len(cards)
        # find the highest pair value
        high_pair_value = counts.index(2) + 2
        value += high_pair_value * 10 ** 8
        # remove the highest pair from cards
        remove = [card for card in cards if card.value == high_pair_value]
        cards = [card for card in cards if card not in remove]
        # add value of kicker
        len(cards)
        value += cards[0].value * 10 ** 4
        return value
    elif counts.count(3) == 1:
        # If there exists 1 "3", but there doesn't exist 1 "2" (since we didn't enter counts.count(2)==1)
        # Base Three of a kind value
        value = 3 * 10 ** 10
        # find the triplet value
        triplets_value = counts.index(3) + 2
        value = triplets_value * 10 ** 8
        # remove triplets from cards
        remove = [card for card in cards if card.value == triplets_value]
        cards = [card for card in cards if card not in remove]
        # loop through remaining cards and add value
        for i in range(1, 2):
            value += cards[i - 1].value * 10 ** (10 - (i + 2) * 2)
        return value

    elif counts.count(4) == 1:
        # If there exists 1 "4", there exists one quad.
        # Base Quads Value
        value = 7 * 10 ** 10
        # find the quad value
        quad_value = counts.index(4) + 2
        value = quad_value * 10 ** 8
        # remove quads from cards
        remove = [card for card in cards if card.value == quad_value]
        cards = [card for card in cards if card not in remove]
        # add kicker value
        value += cards[0].value * 10 ** 6
        return value
    else:
        # Nothing was found, so:
        print("There was an error valuing the hand")
"""""""""
"""""""""""
from card import *
cards=draw_cards(7)

cards[0].make_specific(2, 4)
cards[1].make_specific(4, 4)
cards[2].make_specific(6, 4)
cards[3].make_specific(8, 4)
cards[4].make_specific(14, 1)

cards[5].make_specific(13, 3)
cards[6].make_specific(3, 4)

valued_cards=cards[0:5]

print(new_value_cards(valued_cards))
print(value_cards(valued_cards))

"""""""""
"""""""""
def old_combinations(iterable, r):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i + 1, r):
            indices[j] = indices[j - 1] + 1
        yield tuple(pool[i] for i in indices)
"""""""""

"""""""""
def decide winner
for player in self.players:  # Assign all players their best cards and the showdown value of these cards
    if player in self.hand_players:  # Player participating in showdown
        valued_cards = player.cards + self.cards[0:5]
        player.best_five, player.showdown_value = best_cards(valued_cards)
    else:  # player is not playing so no cards and negative value for redundancy
        player.best_five, player.showdown_value = [], -1
# Sort according to showdown value, with
self.hand_players = sorted(self.hand_players, key=lambda p: p.showdown_value, reverse=True)
# Players participating in showdown are sorted in descending showdown value

if self.hand_players[0].bet == self.current_bet:
    if len(self.hand_players) > 1:
        if self.hand_players[0].showdown_value != self.hand_players[1].showdown_value
            self.winner_num = self.hand_players[0].seat_number

# highest_showdown_value=self.hand_players[0].showdown_value

for player in self.hand_players:
    # for each player still playing
    for paying_player in self.hand_players:
        # go through OTHER players
        if player != paying_player:
            player.playing_for += min(paying_player.bet, player.bet)
            # find how much player is playing for. It's min of their own bet, and other player bet

while self.pot > 0:
    paid_players = []  # find which player(s) have top score
    for player in self.hand_players:
        # player has top score so is in winners
        if player.showdown_value == self.hand_players[0].showdown_value:
            paid_players.append(player)

    # (Current) Top score players have been found.
    # Loop through them and give them min (their fraction of the pot, what they are playing for)
    for player in paid_players:
        # player gets what they are playing for, or their share of pot
        player.chips += min(player.playing_for, self.pot / len(paid_players))
        # remove same amount from pot
        self.pot -= min(player.playing_for, self.pot / len(paid_players))
        # player has been paid so remove.
        paid_players.remove(player)

for player in self.players:
    player.bet = 0

self.winners_found = True
"""""""""
"""""""""
if self.dealer_loc < self.num_p - 2:
    self.players[self.dealer_loc + 1].bets(self, self.small_blind_amount)
    self.players[self.dealer_loc + 2].bets(self, self.big_blind_amount)
elif self.dealer_loc < self.num_p - 1:
    self.players[self.dealer_loc + 1].bets(self, self.small_blind_amount)
    self.players[0].bets(self, self.big_blind_amount)
else:
    self.players[0].bets(self, self.small_blind_amount)
    self.players[1].bets(self, self.big_blind_amount)

"""""""""

#########################
"""""""""
    def update_acting_player(self):
        dealer = self.players[self.dealer_loc]
        if self.acting_player is None:
            actor_index = (self.hand_players.index(dealer) + 3) % (len(self.hand_players))
            self.acting_player = self.hand_players[actor_index]

        if self.state == "pre-flop" or "not_started":
            increment = 2
        else:
            increment = 1

        actor_index = (self.hand_players.index(dealer) + increment) % (len(self.hand_players))
        print(f"WTF:{actor_index}")
        #print(f"{self.state},seat:{actor_index},{self.acting_player.seat_number},{(self.hand_players.index(dealer) + increment)},{len(self.hand_players)}")
        self.acting_player = self.hand_players[actor_index]
    """""""""

"""""""""
while self.hand_players[
    0].bet != self.current_bet:  # stop if next winner on list has full bet (someone is guaranteed to have it)
    paid_player = self.hand_players[0]
    for paying_player in self.hand_players[
                         1:]:  # go through players with lower score than paid_player to determine how much they "pay"
        paid_player.chips += min(paying_player.bet,
                                 paid_player.bet)  # player gets their own bet if paying player has enough, else they get paying_player bet.
    self.hand_players.remove(paid_player)  # remove paid player so first on list changes
    # loop exits if next paid player has max bet, so pay him
# paid player is again  the highest player on list
paid_player = self.hand_players[0]
for paying_player in self.hand_players[
                     1:]:  # go through (other) players with lower score than paid_player to determine how much they "pay"
    paid_player.chips += min(paying_player.bet,
                             paid_player.bet)  # player gets their own bet if paying player has enough, else they get paying_player bet.
"""""""""
"""""""""""
check_equal_bets = True
# If everyone has the same (full) bet, and there is a single winner: winner takes whole pot
for player in self.hand_players:
    if player.bet != self.current_bet:
        check_equal_bets = False

if check_equal_bets and self.hand_players[
    1].showdown_value != highest_showdown_value:  # If all bets are equal, and top score is unique
    paid_player = self.hand_players[0]
    paid_player.chips += self.pot  # singular winner takes the whole pot
    self.pot = 0
########################
else:  # bets are not equal
# while pot still has some in it..
# find players that have the highest value.
# loop through players with highest value...split the winnings


# if there are different size bets...split accordingly

# If everyone has the same (full) bet, and there are multiple winners:
"""""
#

"""""""""

for player in self.hand_players:
    if player.showdown_value ==highest_showdown_value:
        winners.append(player)
    #TODO# If some of these players don't have the full bet...?

smaller_winners=[]
different_size_pots = False
for player in winners:
    if player.bet != self.current_bet: # player has bet less than the others
        smaller_winners.append(player)

smaller_winners=sorted(smaller_winners,key=lambda winner:winner.bid,reverse=False) #sort smaller winners in ascending order
for index,player in enumerate(smaller_winners):
    #first one gets his bet * number of TOTAL players spliting including the full winners
    #second one gets his bet * total winning players,
"""""""""
"""""""""
for player in smaller_winners:
    player.chips+= player.bet*(len(smaller_winners)+number_big_winners)#+ #pay smallest winner first, so they get "paid" by everyone 
    self.pot-= player.bet*len(smaller_winners)
    smaller_winners.remove(player)
    #remove this player
"""""""""

""""""""""

    data_loc="Data/hand_rankings_1000.xlsx"
    df = pd.read_excel(data_loc)

    search = [g.players[0].cards[0].value, g.players[0].cards[0].suit, g.players[0].cards[1].value, g.players[0].cards[1].suit]

    mask = df.apply(lambda row: all(row[i] == search[i] for i in range(len(search))), axis=1)
    result = df[mask]
    hand_score=result.iloc[0,4]

"""""""""""

"""""""""
df = pd.read_excel("Data/starting_hands_sorted.xlsx", index_col=0)
df = df.reset_index(drop=True)

df['Temp_hand_value'] = float(0.01)  # 6
df["Score"] = 0  # 7

for i in range(0, 50000):
    df['Temp_hand_value'] = float(0)
    common_cards = draw_cards(5)
    print(f"Checking:{i}th game")
    for index, hand in df.iterrows():
        if (hand.iloc[0] not in common_cards) and (hand.iloc[1] not in common_cards):
            valued_cards = [hand.iloc[4], hand.iloc[5]] + common_cards
            # for card in valued_cards:
            #    print(card.combo)
            # print(f"Has value:{best_cards(valued_cards)[1]}")
            temp_float = float(best_cards(valued_cards)[1])
            # print(type(temp_float))
            df.iloc[index, 6] += temp_float

    df = df.sort_values(by="Temp_hand_value", ascending=False)
    df = df.reset_index(drop=True)
    df["Score"] += (1326 - df.index) / 1326
print("DONE")

df = df.sort_values(by="Score", ascending=False)

df.to_csv('Data/ranked_starters_50k.xlsx')
"""""""""

"""""""""""""""# Define a function to perform the required swapping
    def swap_values(row):
        if row['Card_1_Value'] < row['Card_2_Value']:
            row['Card_1_Value'], row['Card_2_Value'] = row['Card_2_Value'], row['Card_1_Value']
            row['Card_1_Suit'], row['Card_2_Suit'] = row['Card_2_Suit'], row['Card_1_Suit']
        return row


    # Apply the swapping function to each row
    df = df.apply(swap_values, axis=1)

    df = df.sort_values(by=['Card_2_Suit', 'Card_1_Suit', 'Card_1_Value', 'Card_2_Value'], ascending=False)

    df.to_excel('Data/starting_hands_sorted.xlsx')
"""""""""

"""""""""
# Returns the value of 5 cards
def value_cards(cards):
    value = None
    if len(cards) == 5:
        cards_value = [0, 0, 0, 0, 0]
        cards_suit = [0, 0, 0, 0, 0]
        value = max(cards_value)
        for x in range(0, 5):
            cards_value[x] = cards[x].value
            cards_suit[x] = cards[x].suit

        counts_store = [0] * 14
        for i in range(1, 15):  # from 2 to 14 counts how many of "2" or "3" etc there are
            counts_store[i - 2] = cards_value.count(i)

            # We can now find all the pairs, triples, four of a kind and full houses  .
            # If there are only "1"'s there are no pairs.
            # If there is 1 "2" there is couple .
            # If there is 1 "3" it's a three of a kind.
            # If there is 1 "4" it's a four of a kind.
            # If there is 1 "2" and 1 "3" there is a full house.
            # If there are 2 "2" and 2 "2" there are two pairs   .

        sorted_cards = sorted(cards_value)
        value = sorted_cards[-1]  # Minimum value equal to high card?

        #####################IF ALL CARDS HAVE DIFFERENT VALUES(str,fl,strfl#############
        if counts_store.count(1) == 5:
            straight = False
            flush = False
            if sorted_cards[0] == sorted_cards[1] - 1:
                if sorted_cards[0] == sorted_cards[2] - 2:
                    if sorted_cards[0] == sorted_cards[3] - 3:
                        if sorted_cards[0] == sorted_cards[4] - 4:
                            straight = True
                            value = 4000
                            value = value + sorted_cards[4]
                            # print("straight")

            if cards_suit[0] == cards_suit[1] == cards_suit[2] == cards_suit[3] == cards_suit[4]:
                # print("flush")
                value = 5000 + sorted_cards[-1]
                flush = True

            if flush == True and straight == True:
                value = 8000
                # print("straight flush")
                if cards_value.count(14) == 1:
                    value = 10000
                    # print("royal flush! HOLY SHIT!")

        #####################MIXED VALUES (all other combos)######################
        elif counts_store.count(2) == 1:
            if counts_store.count(3) == 1:
                value = 6000
                for i in range(1, 15):
                    if counts_store[i - 1] == 3:
                        value = value + (i-1) * 10
                        ###the triple is valued higher than double
                    elif counts_store[i - 1] == 2:
                        value = value + i-1
                # print("full house")
            else:
                value = 1000
                for i in range(1, 15):
                    if counts_store[i - 1] == 2:
                        value = value + (i-1) * 10
                        print(f"GOES IN{i-1}x10")
                    elif counts_store[i - 1] == 1:
                        value = value + i-1
                # print("one pair")

        elif counts_store.count(2) == 2:
            # print("two_pairs")
            value = 2000
            for i in range(1, 15):
                if counts_store[i - 1] == 2:
                    print(f"GOES IN{i-1}x10")
                    value = value + (i-1) * 10
                elif counts_store[i - 1] == 1:
                    value = value + i-1
                    print(f"GOES IN +{i}")
        elif counts_store.count(3) == 1:
            value = 3000
            # print("three of a kind")
            for i in range(1, 15):
                if counts_store[i - 1] == 3:
                    value = value + (i-1) * 10
                    print(f"GOES IN{i-1}x10")
                elif counts_store[i - 1] == 1:
                    value = value + i-1

        elif counts_store.count(4) == 1:
            value = 7000
            # print("four of a kind")
            for i in range(1, 15):
                if counts_store[i - 1] == 4:
                    value = value + (i-1) * 10
                    print(f"GOES IN{i-1}x10")
                elif counts_store[i - 1] == 1:
                    value = value + i-1
    elif len(cards) == 2:
        print("not implemented for 2 cards")
    elif len(cards) == 6:
        print("not implemented for 6 cards")
    elif len(cards) == 7:
        print("not implemented for 7 cards")
    return value

"""""""""

"""""""""
df["Score"]=0
for i in range(0,2):
    df['Temp_hand_value'] = 0
    common_cards=draw_cards(5)
    print(f"Checking:{i}th game")
    for index,hand in df.iterrows():
        if (hand.iloc[0] not in common_cards) and (hand.iloc[1] not in common_cards):
            valued_cards=[hand.iloc[0],hand.iloc[1]]+common_cards
            hand.iloc[2]=value_cards(valued_cards)

    df = df.sort_values(by="Temp_hand_value",ascending=False)
    df["Score"] += (1326 - df.index)

print("DONE")
"""""""""

"""""""""
#data=data_all.head(10).copy()
#test_data = data.head(20).copy()
data['average_value'] = 0
# for i in range(0, 1):
#    for hand in data[0:1]:
start_time = time.time()
for index, hand in data.iterrows():

    hand_value_sum = 0
    card_1=Card()
    card_2=Card()
    card_1.make_specific(hand.iloc[0], hand.iloc[1])
    card_2.make_specific(hand.iloc[2], hand.iloc[3])
    hand_cards=[card_1,card_2]

    print(f"Checking hand:{index}")
    for i in range(0,1000):
        table_cards=draw_cards(5)
        while (hand_cards[0] in table_cards) or (hand_cards[1] in table_cards):
            print((hand_cards[0] in table_cards),(hand_cards[1] in table_cards))
            table_cards=draw_cards(5)

        valued_cards=hand_cards+table_cards
        #print(best_cards(valued_cards)[1])
        hand_value_sum+=best_cards(valued_cards)[1]-value_cards(table_cards)
    print(hand_value_sum/(i+1))
    data.iloc[index,4]=int(hand_value_sum/(i+1))

sorted_data=data.sort_values(by='average_value',ascending=False)
sorted_data.to_excel("ranked_1000_minus_table_upto_575.xlsx")
print(f"Finished in:{time.time()-start_time}")
''''''''"""

"""""""""
width = 1920 / 2
height = 1080 / 2
gui = pygame.display.set_mode((width, height))
pygame.display.set_caption("Texas Holdem")
pygame.font.init()
font = pygame.font.SysFont('comicsans', 30)
background = pygame.transform.scale(pygame.image.load('Images/poker_table.jpeg'),(width, height))
"""""""""
"""""""""""""""
pairs_list = []

# Iterate over each row in the DataFrame
for index, row in p_hands.iterrows():
    # Extract values from columns 1 and 2
    pair1 = (row['Card_1_Value'], row['Card_1_Suit'])
    # Extract values from columns 3 and 4
    pair2 = (row['Card_2_Value'], row['Card_2_Suit'])
    # Append the pairs to the list
    pairs_list.append([pair1, pair2])
"""""""""""

"""""""""""
for hand in p_hands:
    card_1=Card()
    card_1.make_specific(hand[""],hand[1])
    card_2 = Card()
    card_2.make_specific(hand[2], hand[3])
"""""""""

import numpy as np
import matplotlib.pyplot as plt


# Define the function
scale=1.8
def func(x):
    return np.exp(scale*x) - 2.5


# Generate values for x
x_values = np.linspace(0, 1, 100)  # Generates 100 equally spaced points between 0 and 1

# Calculate corresponding y values
y_values = func(x_values)
y_values =np.clip(y_values,0,1)
# Plotting
plt.plot(x_values, y_values, label='y = e^x - 1.5')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Plot of y = e^x - 1.5')
plt.grid(True)
plt.legend()
plt.show()
