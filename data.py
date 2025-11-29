import matplotlib.pyplot as plt

import pandas as pd

from card import draw_cards, Card, best_cards, combinations
# TODO # Create large(er) simulation for starting hands

def swap_values(row):
    if row['Card_1_Value'] == row['Card_2_Value'] and row['Card_1_Suit'] < row['Card_2_Suit']:
        row['Card_1_Suit'], row['Card_2_Suit'] = row['Card_2_Suit'], row['Card_1_Suit']
    return row


def all_possible_starting_hands(output_location="Data/starting_hands"):
    p_hands = []
    count = 0
    while len(p_hands) != 1326 and count <= 20000:
        count += 1
        hand = draw_cards(2)
        temp = (hand[0].value, hand[0].suit, hand[1].value, hand[1].suit)
        temp_mirror = (hand[1].value, hand[1].suit, hand[0].value, hand[0].suit)
        if temp not in p_hands and temp_mirror not in p_hands:
            p_hands.append(temp)
            print(f"Found {len(p_hands)} combinations after {count} iterations")

    df = pd.DataFrame(p_hands, columns=['Card_1_Value', 'Card_1_Suit', 'Card_2_Value', 'Card_2_Suit'])
    df = df.sort_values(by=['Card_2_Suit', 'Card_1_Suit', 'Card_1_Value', 'Card_2_Value'])
    df.to_excel(output_location, index=False)
    return p_hands


def create_card_objects(dataframe):
    dataframe['Card_1'] = None
    dataframe['Card_2'] = None

    for index, hand in dataframe.iterrows():
        card_1 = Card()
        card_2 = Card()
        card_1.make_specific(hand.iloc[0], hand.iloc[1])
        card_2.make_specific(hand.iloc[2], hand.iloc[3])
        dataframe.iloc[index, 4] = card_1
        dataframe.iloc[index, 5] = card_2
    return dataframe


"""""""""
NOTE: Do not change the format of hand_rankings file. 
Hand are not sorted by "score", but are instead sorted so that Card_1_Value is higher than Card_2_Value
This is due to how the value function works.
"""""""""


def simulate(n_hands=1, n_common_cards=5, starting_hands_file_path="Data/starting_hands_sorted.xlsx",
             output_save_loc="Data/placeholder.xlsx"):
    df = pd.read_excel(starting_hands_file_path, index_col=0)
    df = df.reset_index(drop=True)
    print("Creating card objects...")
    df = create_card_objects(df)
    print("Card objects created")
    df['Temp_hand_value'] = float(0.01)
    df["Score"] = 0

    for i in range(0, n_hands):
        df['Temp_hand_value'] = float(0)
        common_cards = draw_cards(n_common_cards)
        print(f"Checking:{i}th game")
        for index, hand in df.iterrows():
            if (hand.iloc[0] not in common_cards) and (hand.iloc[1] not in common_cards):
                valued_cards = [hand.iloc[4], hand.iloc[5]] + common_cards
                temp_float = float(best_cards(valued_cards)[1])
                df.iloc[index, 6] += temp_float
        df = df.sort_values(by="Temp_hand_value", ascending=False)
        df = df.reset_index(drop=True)
        df["Score"] += (1326 - df.index) / 1326  # Ratio of hands beaten/total hands with these common cards
    df["Score"] = df["Score"] / n_hands  # Average over n_hands common card combinations
    print("Ranking Complete")
    df = df.sort_values(by="Score", ascending=False)
    df.drop(columns=["Temp_hand_value", "Card_1", "Card_2"], inplace=True)
    df = df.reset_index(drop=True)
    df = df.sort_values(by=["Card_2_Suit", "Card_1_Suit", "Card_2_Value", "Card_1_Value"])

    # Apply the swapping function to each row so that (14,2),(14,3) ->(14,3),(14,2)
    df = df.apply(swap_values, axis=1)

    df.to_excel(output_save_loc, index=False)
    print(f"File has been saved as:{output_save_loc}")
    return df


def plot_frequencies(data_loc="Data/hand_rankings_500.xlsx"):
    df = pd.read_excel(data_loc)
    plt.figure(figsize=(10, 6))
    plt.hist(df['Score'], bins=100, range=(0, 1), edgecolor='black', alpha=0.7)
    plt.xlabel('Score')
    plt.ylabel('Frequency')
    plt.title('Frequency of Scores')
    plt.grid(True)
    plt.show()
