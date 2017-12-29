
# coding: utf-8

import random
from functools import reduce

suits = ['♣', '♦', '♥', '♠']

ranks = [
    { 'name': 'ACE', 'value': 1 },
    { 'name': 'KING', 'value': 10 },
    { 'name': 'QUEEN', 'value': 10 },
    { 'name': 'JACK', 'value': 10 },
    { 'name': '10', 'value': 10 },
    { 'name': '9', 'value': 9 },
    { 'name': '8', 'value': 8 },
    { 'name': '7', 'value': 7 },
    { 'name': '6', 'value': 6 },
    { 'name': '5', 'value': 5 },
    { 'name': '4', 'value': 4 },
    { 'name': '3', 'value': 3 },
    { 'name': '2', 'value': 2 },
]

machine = {
    'start': {
        'ADD_PLAYER': 'add_player',
    },
    'add_player': {
        'ADD_PLAYER': 'add_player',
        'SHUFFLE': 'shuffle_cards',
    },
    'shuffle_cards': {
        'PLACE_BET': 'get_bet',
    },
    'get_bet': {
        'DEAL_FIRST_CARDS_PLAYER': 'deal_first_cards_to_player',
    },
    'deal_first_cards_to_player': {
        'DEAL_FIRST_CARDS_NEXT_PLAYER': 'deal_first_cards_to_player',
        'FINISH_FIRST_CARDS_PLAYER_DEAL': 'deal_first_cards_to_bank',
    },
    'deal_first_cards_to_bank': {
        'PLAYER_DECISION': 'player_decision',
    },
    'player_decision': {
        'PLAYER_HIT': 'player_decision',
        'PLAYER_STAND': 'player_decision',
        'PLAYER_BUST': 'player_decision',
        'FINISH_PLAYER_DECISION': 'deal_card_to_bank',
    },
    'deal_card_to_bank': {
        'BANK_HIT': 'deal_card_to_bank',
        'BANK_STAND': 'eval',
        'BANK_BUST': 'eval',
    },
    'eval': {
        'PLAY_AGAIN': 'add_player',
        'QUIT': 'quit',
    },
    'quit': {},
}

def get_number(label):
    while True:
        try:
            return int(input(label))
        except:
            print('invalid number, try again');

class Card(object):

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank


class Pack(object):
    def __init__(self):
        self.cards = []
        for s in range(len(suits)):
            for r in range(len(ranks)):
                self.cards.append({'suit': suits[s], 'rank': ranks[r]})

    def shuffle(self):
        self.pack_of_divider = self.cards[:]
        random.shuffle(self.pack_of_divider)

    def take_card(self, amount):
        cards = self.pack_of_divider[:amount]
        self.pack_of_divider = self.pack_of_divider[amount:]
        return cards

class Participant(object):
    def __init__(self):
        self.cards = []
        self.cards_sums = [0]
        self.name = 'participant'
        self.busted = False

    def add_cards(self, new_cards):
        self.cards += new_cards
        self.update_cards_sums(new_cards)

    def show_cards(self, hidden_second = False):
        print('\nCards of', self.name, ':')
        for idx, card in enumerate(self.cards):
            if (idx == 1 and hidden_second == True):
                print('Hidden card')
            else: print(card['suit'], card['rank']['name'])

    def update_cards_sums(self, new_cards):
        def update_reducer(acc, new_card):
            new_sums = list(map(lambda x: x + new_card['rank']['value'], acc[:]))
            if (new_card['rank']['name'] != 'ACE'):
                return new_sums
            new_sums_ace_11 = list(map(lambda x: x + 11, acc[:]))
            return new_sums + new_sums_ace_11

        self.cards_sums = reduce(update_reducer, new_cards, self.cards_sums[:]);

    def in_bust(self):
        return all(sum > 21 for sum in self.cards_sums)

    def bust(self):
        self.busted = True
        print('Unfortunately, ' + self.name + ' is busted')

    def highest(self):
        return max(self.cards_sums)

    def reset(self):
        self.cards = []
        self.cards_sums = [0]
        self.busted = False

class Player(Participant):
    def __init__(self):
        Participant.__init__(self)
        self.name = input('Player name: ')
        self.init_wallet()

    def init_wallet(self):
         self.wallet = get_number(self.name + ', please enter your wallet total (USD):')

    def place_bet(self):
        while True:
            bet = get_number(self.name +
                ', please take you bet (wallet: ' +
                str(self.wallet) +'):')
            if (self.wallet >= bet):
                self.wallet -= bet
                self.bet = bet
                break
            else:
                print('Not enough money in your wallet:', self.wallet)

    def decide(self):
        action = input('What is next action of ' + self.name + '? (h)it/(s)tand: ')
        return 'HIT' if (action == 'h') else 'STAND'

    def got(self, amount):
        self.wallet += self.bet + amount

class Players(object):
    def __init__(self):
        self.players = []

    def add(self):
        self.players.append(Player())

    def get(self, index = -1):
        if index == -1:
            return self.players
        return self.players[index]

    def len(self):
        return len(self.players)

    def play_again(self):
        for player in self.players:
            player.reset()

class Bank(Participant):
    def __init__(self):
        Participant.__init__(self)
        self.name = 'BANK'

    def decide(self):
        if any(sum >= 17 for sum in self.cards_sums):
            return 'STAND'
        return 'HIT'

class Game(object):

    def __init__(self, state):
        self.current_state = state
        self.pack = Pack()
        self.players = Players()
        self.bank = Bank()
        self.transition({ 'type': 'ADD_PLAYER' })

    def get_next_state(self, action):
        return Game.machine[self.current_state][action['type']]

    def transition(self, action):
        ns = self.get_next_state(action)
        if (ns):
            self.current_state = ns
            self.command(action)

    def command(self, action):
        if (action['type'] == 'ADD_PLAYER'):
            self.add_players()

        elif (action['type'] == 'SHUFFLE'):
            self.pack.shuffle()
            self.transition({ 'type': 'PLACE_BET' })

        elif (action['type'] == 'PLACE_BET'):
            self.place_bets()
            self.transition({
                'type': 'DEAL_FIRST_CARDS_PLAYER',
                'player_index': 0,
                'card_amount': 2,
            })

        elif (action['type'] == 'DEAL_FIRST_CARDS_PLAYER' or
             action['type'] == 'DEAL_FIRST_CARDS_NEXT_PLAYER'):
            if not self.all_player_finished(action):
                player = self.get_current_player(action)
                self.deal(player, action)
                player.show_cards()
                self.transition({
                    'type': 'DEAL_FIRST_CARDS_NEXT_PLAYER',
                    'player_index': action['player_index'] + 1,
                    'card_amount': 2,
                })
            else:
               self.transition({
                   'type': 'FINISH_FIRST_CARDS_PLAYER_DEAL',
                   'card_amount': 2,
               })

        elif (action['type'] == 'FINISH_FIRST_CARDS_PLAYER_DEAL'):
            self.deal(self.bank, action)
            self.bank.show_cards(hidden_second = True);
            self.transition({
                'type': 'PLAYER_DECISION',
                'player_index': 0,
                'card_amount': 1,
            })

        elif (action['type'] == 'PLAYER_DECISION' or
             action['type'] == 'PLAYER_HIT' or
             action['type'] == 'PLAYER_STAND' or
             action['type'] == 'PLAYER_BUST'):
            if not self.all_player_finished(action):
                player = self.get_current_player(action)
                if action['type'] == 'PLAYER_HIT':
                    self.deal(player, action)
                    player.show_cards()
                if player.in_bust():
                    player.bust()
                    self.next_player(action)
                else:
                    self.make_player_decide(player, action)
            else:
                self.transition({ 'type': 'FINISH_PLAYER_DECISION' })

        elif (action['type'] == 'FINISH_PLAYER_DECISION' or
             action['type'] == 'BANK_HIT'):
            if action['type'] == 'BANK_HIT':
                self.deal(self.bank, action)
                self.bank.show_cards()
            if self.bank.in_bust():
                self.bank.bust()
                self.transition({ 'type': 'BANK_BUST' })
                self.evaluate()
                self.decide_play_again()
            else:
                self.make_bank_decide()

        elif (action['type'] == 'BANK_STAND'):
            self.bank.show_cards()
            self.evaluate()
            self.decide_play_again()

    def add_players(self):
        self.players.add()
        add_another_player = input('Add another player? (y/n) ') == 'y'
        if (add_another_player):
             self.transition({ 'type': 'ADD_PLAYER' })
        else:
            self.transition({ 'type': 'SHUFFLE' })

    def place_bets(self):
        for player in (self.players.get()):
            player.place_bet()

    def next_player(self, action):
        self.transition({
            'type': 'PLAYER_BUST',
            'player_index': action['player_index'] + 1,
            'card_amount': 2,
        })

    def get_current_player(self, action):
        return self.players.get(action['player_index'])

    def deal(self, participant, action):
        participant.add_cards(self.pack.take_card(action['card_amount']))

    def all_player_finished(self, action):
        return action['player_index'] == self.players.len()

    def make_player_decide(self, player, action):
        decision = player.decide()
        if (decision == 'HIT'):
            self.transition({
                'type': 'PLAYER_HIT',
                'player_index': action['player_index'],
                'card_amount': 1,
            })
        elif (decision == 'STAND'):
            self.transition({
                'type': 'PLAYER_STAND',
                'player_index': action['player_index'] + 1,
                'card_amount': 1,
            })

    def make_bank_decide(self):
        decision = self.bank.decide();
        if (decision == 'HIT'):
            self.transition({
                'type': 'BANK_HIT',
                'card_amount': 1,
            })
        elif (decision == 'STAND'):
            self.transition({ 'type': 'BANK_STAND' })

    def evaluate(self):
        for player in self.players.players:
            if player.busted:
                print(player.name, 'is busted, remained money is', player.wallet)
            elif self.bank.busted:
                print(player.name, 'got', int(player.bet * 0.5))
                player.got(int(player.bet * 0.5))
            else:
                player_highest = player.highest()
                bank_highest= self.bank.highest()
                if player_highest > bank_highest:
                    if player_highest == 21 and len(player.cards) == 2:
                        print(
                            player.name,
                            'has BLACK_JACK, got',
                            int(player.bet / 3 * 2)
                        )
                        player.got(int(player.bet / 3 * 2))
                    else:
                        print(player.name, 'got', int(player.bet * 0.5))
                        player.got(int(player.bet * 0.5))
                elif bank_highest > player_highest:
                    print(player.name, 'lost', player.bet)
                else:
                    print(player.name, 'is in PUSH, bet is returned')
                    player.got(0)

    def decide_play_again(self):
        d = input('PLAY AGAIN? (y/n)')
        if d == 'y':
            self.transition({ 'type': 'PLAY_AGAIN' })
            self.players.play_again()
            self.bank.reset()
            self.transition({ 'type': 'SHUFFLE' })
        else:
            print('Good Bye!')
            self.transition({ 'type': 'QUIT' })

Game('start')

