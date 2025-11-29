import time
import random

import pygame

from card import categorize_value
from constants import *


# TODO # slider functionality
# TODO # When both players are all in and the player with least chips wins, the pot is "split" because the player
#  with more chips gets his extra back..
def super_sample(image, new_height, new_width, factor, rotation_angle=0):
    # image_width, image_height = image.get_size()
    image_height = new_height
    image_width = new_width

    rescaled_width = image_width * factor
    rescaled_height = image_height * factor
    rescaled_image = pygame.transform.smoothscale(image, (rescaled_width, rescaled_height))

    rotated_image = pygame.transform.rotate(rescaled_image, rotation_angle)

    final_image = pygame.transform.smoothscale(rotated_image, (image_width, image_height))

    # image_rect = final_image.get_rect(center=loc)

    # self.display.blit(final_image, image_rect)
    return final_image


class GUI:
    def __init__(self, delay=1):
        self.delay = delay

        self.width = DISPLAY_WIDTH
        self.height = DISPLAY_HEIGHT
        self.card_width = CARD_WIDTH
        self.card_height = CARD_HEIGHT

        self.circle_radius = PLAYER_CIRCLE_RADIUS

        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Texas Holdem")
        pygame.font.init()
        font_size = int(DISPLAY_WIDTH * (1 / 64))
        self.font = pygame.font.SysFont('comicsans', font_size)

        self.button_font_size = int(3 * DISPLAY_WIDTH / 160)

        self.background = pygame.transform.scale(pygame.image.load('Images/no back wood d2.png'),
                                                 (self.width * 0.8, self.height * 0.8))
        ##########################
        mid_width = self.width / 2
        mid_table_up_h = self.height / 8.2
        mid_table_down_h = self.height - mid_table_up_h
        right_width = 8.15 * self.width / 10
        left_width = self.width - right_width
        mid_one_height = self.height / 4
        mid_two_height = self.height - mid_one_height

        self.seat_positions = [(mid_width, mid_table_up_h),
                               (right_width, mid_one_height),
                               (right_width, mid_two_height),
                               (mid_width, mid_table_down_h),
                               (left_width, mid_two_height),
                               (left_width, mid_one_height)]

        horizontal_offset = DISPLAY_HEIGHT * 0.125
        diagonal_offset = DISPLAY_HEIGHT * 0.10

        self.bet_positions = [(mid_width, mid_table_up_h + horizontal_offset),
                              (right_width - diagonal_offset, mid_one_height + diagonal_offset),
                              (right_width - diagonal_offset, mid_two_height - diagonal_offset),
                              (mid_width, mid_table_down_h - horizontal_offset),
                              (left_width + diagonal_offset, mid_two_height - diagonal_offset),
                              (left_width + diagonal_offset, mid_one_height + diagonal_offset)]

        horizontal_offset = horizontal_offset * 2
        diagonal_offset = diagonal_offset * 1

        self.dealer_positions = [(mid_width + horizontal_offset * 0.1, mid_table_up_h + horizontal_offset * 0.5),
                                 (right_width - diagonal_offset * 2, mid_one_height + diagonal_offset),
                                 (right_width - diagonal_offset * 2, mid_two_height - diagonal_offset * 1.2),
                                 (mid_width - horizontal_offset * 0.25, mid_table_down_h - horizontal_offset * 0.78),
                                 (left_width + diagonal_offset * 1.2, mid_two_height - diagonal_offset * 1.2),
                                 (left_width + diagonal_offset * 1.2, mid_one_height + diagonal_offset)]
        self.dealer_image = pygame.image.load("Images/dealer.png")
        ####################
        # self.joker = pygame.transform.scale(pygame.image.load("Cards/red_joker.png"),
        #                                    (self.card_width, self.card_height))

        self.joker = pygame.image.load("Cards/red_joker.png")

        self.green_chip = pygame.transform.scale(pygame.image.load("Images/Chips/green_chip.png"),
                                                 (CHIP_WIDTH, CHIP_HEIGHT))
        self.blue_chip = pygame.transform.scale(pygame.image.load("Images/Chips/blue_chip.png"),
                                                (CHIP_WIDTH, CHIP_HEIGHT))
        self.red_chip = pygame.transform.scale(pygame.image.load("Images/Chips/red_chip.png"),
                                               (CHIP_WIDTH, CHIP_HEIGHT))

        self.purple_chip = pygame.transform.scale(pygame.image.load("Images/Chips/purple_chip.png"),
                                                  (CHIP_WIDTH, CHIP_HEIGHT))
        self.chip_images = [self.green_chip, self.blue_chip, self.red_chip, self.purple_chip]

        # self.red_chip_3d = pygame.transform.scale(pygame.image.load("Images/Chips/red_chip_3d.png"),
        #                                          (CHIP_WIDTH, CHIP_HEIGHT))
        # self.stack_10_green = pygame.transform.scale(pygame.image.load("Images/Chips/10_stack_green.png"),
        #                                             (CHIP_WIDTH, CHIP_HEIGHT))
        # self.stack_5_green = pygame.transform.scale(pygame.image.load("Images/Chips/5_stack_green.png"),
        #                                            (CHIP_WIDTH, CHIP_HEIGHT))
        # self.stack_10_red = pygame.transform.scale(pygame.image.load("Images/Chips/10_stack_red.png"),
        #                                          (CHIP_WIDTH, CHIP_HEIGHT))

        self.handle_x = BAR_X
        self.slider_value = 0

        self.call_button_pressed = False
        self.fold_button_pressed = False

        self.button_one_text = "Call"
        self.slider_left = False
        self.slider_right = False

        self.handle_clicked = False

        pygame.mixer.init()
        self.check_sound = pygame.mixer.Sound("Audio/check_2.wav")
        self.call_sound = pygame.mixer.Sound("Audio/call.wav")
        self.fold_sound = pygame.mixer.Sound("Audio/fold.wav")
        self.raise_sound = pygame.mixer.Sound("Audio/raise.wav")
        self.bet_sound = pygame.mixer.Sound("Audio/bet.wav")
        self.all_in_sound = pygame.mixer.Sound("Audio/all in.wav")
        self.card_sound = pygame.mixer.Sound("Audio/dealing_card_f4ngy.wav")

    def render_gui(self, game):
        self.render_bg()
        self.render_seats()
        self.render_player_avatars(game)
        self.render_pot(game)
        # self.render_pot_chips(chip_counts=self.count_pot_chips(game)
        # self.render_back_end_info(game)
        self.render_dealer(game)
        self.stage_dependant_renders(game)
        self.render_players_info(game)

        self.render_call_check_bet_raise_button(game)
        self.render_raise_sliding_bar(game)
        self.render_fold_button()

        self.render_request_human_input(game)
        # self.render_chips_test((DISPLAY_WIDTH / 5, DISPLAY_HEIGHT / 8))
        self.render_common_cards(game)

        self.render_winners(game)

        self.render_new_game_timer(game)

        self.render_pot_chips([0,1,2,3])

        pygame.display.update()

    def stage_dependant_renders(self, game):

        if game.state == 'not_started':
            game.common_cards_shown = 0
        elif game.state == "pre_flop":
            game.common_cards_shown = 0
            self.render_hidden_cards(game)
        elif game.state == "flop":
            game.common_cards_shown = 3
            self.render_hidden_cards(game)
        elif game.state == "turn":
            game.common_cards_shown = 4
            self.render_hidden_cards(game)
        elif game.state == "river":
            game.common_cards_shown = 5
            self.render_hidden_cards(game)
        elif game.state == "showdown":
            game.common_cards_shown = 5
            self.render_shown_cards(game)
            # game.decide_winner()

    def render_common_cards(self, game):
        card_position = 0
        for card in game.deck[0:game.common_cards_shown]:
            self.display.blit(card.image, (
                self.width / 2.08 + card_position * (self.card_width * 1.2) - 2.5 * self.card_width,
                (self.height / 2) - 0.5 * self.card_height))
            card_position += 1

    def render_hidden_cards(self, game):
        card_squeeze_offset = CARD_WIDTH * 0.5
        offset = PLAYER_CIRCLE_RADIUS - CARD_WIDTH + card_squeeze_offset / 2
        y_offset = CARD_HEIGHT * 0.15

        joker_left = super_sample(self.joker, CARD_HEIGHT, CARD_WIDTH, 2, 8)
        joker_right = super_sample(self.joker, CARD_HEIGHT, CARD_WIDTH, 2, -8)

        for i in range(0, game.num_p):
            if game.players[i] in game.hand_players:
                x = self.seat_positions[i][0] - self.circle_radius + offset
                y = self.seat_positions[i][1] - self.circle_radius / 2
                if game.players[i] == game.human_player:
                    human_card_left = super_sample(game.human_player.cards[0].image, CARD_HEIGHT, CARD_WIDTH, 2, 8)
                    human_card_right = super_sample(game.human_player.cards[1].image, CARD_HEIGHT, CARD_WIDTH, 2, -8)

                    self.display.blit(human_card_left, (x, y - y_offset))
                    self.display.blit(human_card_right, (x + self.card_width - card_squeeze_offset, y - y_offset))
                else:
                    self.display.blit(joker_left, (x, y - y_offset))
                    self.display.blit(joker_right, (x + self.card_width - card_squeeze_offset, y - y_offset))

    def render_shown_cards(self, game):
        card_squeeze_offset = CARD_WIDTH * 0.5
        offset = PLAYER_CIRCLE_RADIUS - CARD_WIDTH + card_squeeze_offset / 2
        y_offset = CARD_HEIGHT * 0.15

        for i in range(0, game.num_p):
            if game.players[i] in game.hand_players:
                left_card = super_sample(game.players[i].cards[0].image, CARD_HEIGHT, CARD_WIDTH, 2, 8)
                right_card = super_sample(game.players[i].cards[1].image, CARD_HEIGHT, CARD_WIDTH, 2, -8)

                x = self.seat_positions[i][0] - self.circle_radius + offset
                y = self.seat_positions[i][1] - self.circle_radius / 2 - y_offset
                self.display.blit(left_card, (x, y))
                self.display.blit(right_card, (x + self.card_width - card_squeeze_offset, y))
        """""""""
        for player in game.split_winners:
            left_card = super_sample(player.cards[0].image, CARD_HEIGHT, CARD_WIDTH, 2, 8)
            right_card = super_sample(player.cards[0].image, CARD_HEIGHT, CARD_WIDTH, 2, -8)

            x = self.seat_positions[player.seat_number][0] - self.circle_radius + offset
            y = self.seat_positions[player.seat_number][1] - self.circle_radius / 2 -y_offset
            self.display.blit(left_card, (x, y))
            self.display.blit(right_card,
                              (x + self.card_width - card_squeeze_offset, y))
        """""""""

    def render_players_info(self, game):
        for player in game.players:
            self.render_player_bet(player)
            self.render_player_chips(player)
            self.render_player_name(player)

    def render_player_name(self, player):
        box_width = DISPLAY_WIDTH * 0.05
        box_height = DISPLAY_HEIGHT * 0.018
        x = self.seat_positions[player.seat_number][0] - box_width / 2
        y = self.seat_positions[player.seat_number][1] - PLAYER_CIRCLE_RADIUS
        chips_text = f"{player.name}"
        self.draw_text_in_box(chips_text, "black", "white", x, y, box_width, box_height)

    def render_player_chips(self, player):
        box_width = DISPLAY_WIDTH * 0.08
        box_height = DISPLAY_HEIGHT * 0.025
        x = self.seat_positions[player.seat_number][0] - box_width / 2
        y = self.seat_positions[player.seat_number][1] + PLAYER_CIRCLE_RADIUS * (0.9)
        chips_text = f"{player.chips}$"
        self.draw_text_in_box(chips_text, "black", "white", x, y, box_width, box_height)

    def render_player_bet(self, player):
        x = self.bet_positions[player.seat_number][0]
        y = self.bet_positions[player.seat_number][1]

        # self.draw_text_in_box(f"{player.bet} $","black","white",x,y,100,50)

        bet_text = self.font.render(f"{player.bet} $", 1, "black")
        self.display.blit(bet_text, (x, y))

    def render_back_end_info(self, game):
        for player in game.players:
            rank_range_text = self.font.render(f"Rank/Range : {player.current_rank} / {player.current_range}", 1,
                                               "green")
            self.display.blit(rank_range_text, (
                self.seat_positions[player.seat_number][0] - 150,
                self.seat_positions[player.seat_number][1] + (2 * self.height / 10) - 20))

            limp_bluff_text = self.font.render(f"Limp/Bluff : {player.limp} / {player.bluff}", 1,
                                               "red")
            self.display.blit(limp_bluff_text, (
                self.seat_positions[player.seat_number][0] - 150,
                self.seat_positions[player.seat_number][1] + (2 * self.height / 10)))

            bet_limit_text = self.font.render(f"Bet Limit : {round(player.bet_limit, 2)}", 1,
                                              "blue")
            self.display.blit(bet_limit_text, (
                self.seat_positions[player.seat_number][0] - 150,
                self.seat_positions[player.seat_number][1] + (2 * self.height / 10) + 20))

    def render_winners(self, game):
        if game.winners_found:
            box_width = 0.28 * self.width
            box_height = 0.025 * self.height

            x = 0.5 * self.width - box_width / 2
            y = 0.64 * self.height
            if not game.split:
                winner = game.players[game.winner_loc]
                winner_text = f"{winner.name} wins with : {categorize_value(winner.showdown_value)}"
                self.draw_text_in_box(winner_text, "white", "black", x, y, box_width, box_height)
            else:
                winners_names = ','.join(player.name for player in game.split_winners)
                winner_text_1 = f"The pot is split. Winners are : "
                winner_text_2 = f"{winners_names}"

                self.draw_text_in_box(winner_text_1, "white", "black", x, y, box_width, box_height)
                self.draw_text_in_box(winner_text_2, "white", "black", x, y + box_height, box_width, box_height)

    def render_dealer(self, game):
        x = self.dealer_positions[game.dealer_loc][0]
        y = self.dealer_positions[game.dealer_loc][1]
        # pygame.draw.circle(self.display, "brown", (x,y), DEALER_BUTTON_RADIUS,2)
        # dealer_text = self.font.render(f"D", 1, "white")
        # self.display.blit(dealer_text, (x,y))

        width = DEALER_BUTTON_RADIUS * 3.8
        height = (DISPLAY_HEIGHT / DISPLAY_WIDTH) * width

        # x = self.seat_positions[player.seat_number][0] - width / 2
        # y = self.seat_positions[player.seat_number][1] - height / 2

        scaled_image = pygame.transform.smoothscale(self.dealer_image, (width, height))

        self.display.blit(scaled_image, (x, y))

        """""""""
        radius = DEALER_BUTTON_RADIUS
        circle_color = "brown"
        circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, circle_color, (radius, radius), radius)

        # Create text surface
        text_surface = self.font.render(f"D", True, "black")

        # Calculate text position to center it within the circle
        text_rect = text_surface.get_rect(center=(radius, radius))

        # Blit text onto circle
        circle_surface.blit(text_surface, text_rect)

        # Blit circle onto screen
        self.display.blit(circle_surface, (x - radius, y - radius))
        
        """""""""

    def render_time(self, game):
        time_text = self.font.render(f"Time: {int(time.time() - game.start_time)}", 1, "black")
        self.display.blit(time_text, (0, 0))
        # Test stuff
        # current_bet_text = self.font.render(f"Previous Bet: {game.previous_bet} , {game.previous_bet_amount}", 1,
        #                                    "black")
        # self.display.blit(current_bet_text, (0, 20))

    def render_bg(self):
        self.display.fill("gray")
        self.display.blit(self.background, (0 + DISPLAY_WIDTH * 0.10, 0 + DISPLAY_HEIGHT * 0.10))

    def render_chips_test(self, loc=(0, 0)):
        pass
        # for i in range(0, 2):
        #    self.display.blit(self.red_chip, (loc[0] + (i * 2), loc[1] - (i + 0.5)))
        # self.display.blit(self.stack_10_green
        #                  , (loc[0] + 35, loc[1] + 10))
        # self.display.blit(self.stack_10_red, (loc[0] + 55, loc[1] + 20))
        # self.display.blit(self.stack_5_green, (loc[0] - 45, loc[1] - 20))
        # self.display.blit(self.red_chip_3d, (loc[0]-35, loc[1]+20))

    def render_seats(self):
        i = 1
        box_width = self.circle_radius
        box_height = self.circle_radius / 3

        for location in self.seat_positions:
            pygame.draw.circle(self.display, "black", location, self.circle_radius,
                               0)  # 2 indicates the thickness of the outline

            pygame.draw.circle(self.display, "brown", location, self.circle_radius + 1,
                               4)  # 2 indicates the thickness of the outline

            pygame.draw.circle(self.display, "black", location, self.circle_radius - 4,
                               4)  # 2 indicates the thickness of the outline

            self.draw_text_in_box(f"Seat {i}", box_color="white", text_color="black", x=location[0] - box_width / 2,
                                  y=location[1] - box_height / 2,
                                  width=box_width,
                                  height=box_height)

            i += 1

    def render_player_avatars(self, game):
        for player in game.players:
            width = self.circle_radius * 3.8
            height = (DISPLAY_HEIGHT / DISPLAY_WIDTH) * width

            x = self.seat_positions[player.seat_number][0] - width / 2
            y = self.seat_positions[player.seat_number][1] - height / 2

            # scaled_image = player.avatar_image
            scaled_image = pygame.transform.scale(player.avatar_image, (width, height))
            # TODO # Need to create a new surface maybe?
            self.display.blit(scaled_image, (x, y))

    def render_pot(self, game):
        box_width = (6 / 48) * DISPLAY_WIDTH
        box_height = (1 / 53) * DISPLAY_HEIGHT
        self.draw_text_in_box(f" Total Pot : {game.pot} $ ", "white", "black", self.width / 2 - box_width / 2,
                              self.height * 0.305,
                              box_width, box_height)

    def draw_text_in_box(self, text, box_color, text_color, x, y, width, height):
        # Create box surface
        box_surface = pygame.Surface((width, height))
        box_surface.fill(box_color)

        # Create text surface
        text_surface = self.font.render(text, True, text_color)

        # Center text within the box
        text_rect = text_surface.get_rect(center=(width // 2, height // 2))

        # Blit text onto box
        box_surface.blit(text_surface, text_rect)

        # Blit box onto screen
        self.display.blit(box_surface, (x, y))

    def count_pot_chips(self, game):
        pot = game.pot
        chip_counts = [0] * 5
        chip_values = [1, 2, 5, 10]  # , 20]
        i = len(chip_values) - 1
        while pot > 0:
            chip_value = chip_values[i]
            quotient, remainder = divmod(pot, chip_value)
            chip_counts[i] += quotient
            pot = remainder
            i -= 1
        return chip_counts

    def render_pot_chips(self, chip_counts, loc=(DISPLAY_WIDTH / 2, DISPLAY_HEIGHT * 0.35)):
        center_x = loc[0]
        center_x = loc[0]

        left = random.random() < 0.5

        # TODO # Create a "box" where pot chips will appear.
        # For each chip that will be placed, "randomly" assign coordinates within that box

        offset_y = CHIP_HEIGHT / 3
        offset_x = +CHIP_WIDTH / 3
        count = 0
        for i in range(0, len(chip_counts)):
            # if left:
            #    offset_x = -CHIP_WIDTH / 3
            # else:
            #

            for j in range(0, int(chip_counts[i])):
                self.display.blit(self.chip_images[i], (loc[0] + offset_x * count, loc[1] + offset_y))
                count += 1

    ###
    def render_call_check_bet_raise_button(self, game):
        # Draw the button

        font = pygame.font.Font(None, self.button_font_size)

        if self.slider_value == 0:
            if game.players[3].bet != game.current_bet:
                self.button_one_text = "Call"
            else:
                self.button_one_text = "Check"

        elif self.slider_value < game.players[3].chips:
            if game.previous_bet:
                self.button_one_text = "Raise"

            else:
                self.button_one_text = "Bet"

        else:
            self.button_one_text = "All-in"

        text = font.render(self.button_one_text, True, "white")
        text_rect = text.get_rect(
            center=(CALL_BUTTON_X + CALL_BUTTON_WIDTH // 2, CALL_BUTTON_Y + CALL_BUTTON_HEIGHT // 2))
        pygame.draw.rect(self.display, "black", (CALL_BUTTON_X, CALL_BUTTON_Y, CALL_BUTTON_WIDTH, CALL_BUTTON_HEIGHT))

        self.display.blit(text, text_rect)

    def render_fold_button(self):
        # Draw the button
        font = pygame.font.Font(None, self.button_font_size)
        text_2 = font.render("Fold", True, "white")
        text_rect_2 = text_2.get_rect(
            center=(FOLD_BUTTON_X + FOLD_BUTTON_WIDTH // 2, FOLD_BUTTON_Y + CALL_BUTTON_HEIGHT // 2))
        pygame.draw.rect(self.display, "black", (FOLD_BUTTON_X, FOLD_BUTTON_Y, FOLD_BUTTON_WIDTH, FOLD_BUTTON_HEIGHT))
        self.display.blit(text_2, text_rect_2)

    def render_raise_sliding_bar(self, game):
        font = pygame.font.Font(None, 24)
        min_value = 0
        max_value = game.players[3].chips
        # Draw the bar
        pygame.draw.rect(self.display, "black", (BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT))

        # Draw the handle
        pygame.draw.rect(self.display, "brown", (self.handle_x, HANDLE_Y, HANDLE_WIDTH, HANDLE_HEIGHT))

        # Draw value text
        self.slider_value = int(
            (self.handle_x - BAR_X) / (BAR_WIDTH - HANDLE_WIDTH) * (max_value - min_value) + min_value)

        self.slider_value = min(game.human_player.chips, self.slider_value)

        if self.handle_x != BAR_X:
            if game.previous_bet:
                min_slider_value = max(game.big_blind_amount, game.previous_bet_amount)
            else:
                min_slider_value = game.big_blind_amount
        else:
            min_slider_value = 0
        self.slider_value = max(min_slider_value, self.slider_value)
        value_text = font.render(
            f"{self.slider_value}", True,
            "BLACK")

        # value_text = font.render(
        #    f"{int(BAR_X-HANDLE_X-HANDLE_WIDTH)}", True,
        #    "BLACK")

        self.display.blit(value_text, (BAR_X + BAR_WIDTH, BAR_Y + (BAR_HEIGHT - value_text.get_height()) // 2))

    def render_request_human_input(self, game):
        if game.action_required:
            box_width = 0.28 * self.width
            box_height = 0.025 * self.height
            x = 0.5 * self.width - box_width / 2
            y = 0.64 * self.height
            self.draw_text_in_box("Please choose an action", "white", "black", x, y, box_width, box_height)

    def update_slider_position(self, game):
        gui = self
        increment = 5
        if gui.slider_left:
            gui.handle_x = gui.handle_x - increment
        elif gui.slider_right and gui.slider_value < game.players[3].chips:
            gui.handle_x = gui.handle_x + increment
        #Stay within bounds
        gui.handle_x = max(gui.handle_x, BAR_X)
        gui.handle_x = min(gui.handle_x, BAR_X + BAR_WIDTH - HANDLE_WIDTH / 2)

    # TODO # Starting a new game through a render method isn't ideal...
    def render_new_game_timer(self, game):

        if game.winners_found:
            timer = 5 - int(time.time() - game.round_ended_time)

            if timer > 0:
                y = 0.72 * self.height
                time_text = self.font.render(f"New game in: {timer}", 1, "black")
                x = self.width / 2 - 0.026 * DISPLAY_WIDTH
                self.display.blit(time_text, (x, y))
            else:
                game.new_game(self)
