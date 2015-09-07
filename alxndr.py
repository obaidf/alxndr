from Brisk import Brisk
from Map import Map

import sys

TOKEN_ID = "5b23d966068c4a95b67fcc24985480a8965b52c9"

ARMIES_TO_LEAVE = 1

def main():
	if len(sys.argv) > 1:
		bot = Alxndr(int(sys.argv[1]))
	else:
		bot = Alxndr()

class Alxndr(object):
	def __init__(self, game_id=False, bot_id=1):
		self.brisk = Brisk(game_id, bot_id)
		self.map = Map(self.brisk.get_map_layout())

		self.play()

	def update_state(self):
		self.game_state = self.brisk.get_game_state()
		self.player_status = self.brisk.get_player_status()

	def play(self):
		print 'Game ID: ' + str(self.brisk.game_id)
		while True:
			self.update_state()
			if self.game_state['winner']:
				print 'WINNER: ' + str(self.game_state['winner'])
				return
			if self.player_status['current_turn']:
				self.take_turn()

	def get_my_territory_ids(self):
		return [t['territory'] for t in self.player_status['territories']]

	def get_my_territories_dict(self):
		my_territories = {}

		for territory in self.player_status['territories']:
			territory_id = territory['territory']
			my_territories[territory_id] = territory

		return my_territories

	def take_turn(self):
		self.update_state()
		place_troops_at = self.get_territories_to_reinforce()
		num_reserves = self.player_status['num_reserves']

		troops_placed = 0
		troops_reserve = num_reserves
		if num_reserves > 0:
			if len(place_troops_at) > 3:
				place_troops_at = place_troops_at[:3]

			troops_to_place = num_reserves // len(place_troops_at)
			remainder_troops = num_reserves % len(place_troops_at)

			first_territory = True
			for territory in place_troops_at:
				self.brisk.place_armies(territory, troops_to_place if not first_territory else troops_to_place + remainder_troops)
				first_territory = False

				troops_placed += troops_to_place if not first_territory else troops_to_place + remainder_troops

			self.update_state()
		print 'put ' + str(troops_placed) + ' troops of ' + str(troops_reserve)

		self.attack()
		self.transfer()

	def get_territories_to_reinforce(self):
		import attack_planner

		territories = []

		candidate_attacks = attack_planner.computeAttackAdvantages(self.brisk, self)
		candidate_attacks = sorted(candidate_attacks, key=lambda a: a['attack_advantage'], reverse=True)

		for attack in candidate_attacks:
			if attack['attacking_territory'] in self.map.border_territories:
				territories.append(attack['attacking_territory'])

		# If no candidate attacks on continent borders, fall back to selecting territory based on most enemy neighbors
		if len(territories) == 0:
			territories.append(self.map.territory_with_most_enemies(self.get_my_territory_ids()))

		return territories

	def attack(self):
		import attack_planner
		front = attack_planner.getAttack(self.brisk, self)

		while front:
			print 'Starting attack!'

			if front['attack_advantage'] < 1:
				return

			my_territories = self.get_my_territories_dict()

			my_territory_id = front['our_territory']
			enemy_territory_id = front['enemy_territory']

			my_armies_left = my_territories[my_territory_id]['num_armies']

			attack_results = self.brisk.attack(my_territory_id, enemy_territory_id, min(3, my_armies_left-1))
			self.update_state()

			if attack_results['defender_territory_captured']:
				print 'We won territory ' + str(enemy_territory_id) + '!'
				num_to_transfer = attack_results['attacker_territory_armies_left'] - ARMIES_TO_LEAVE
				if num_to_transfer > 0:
					self.brisk.transfer_armies(my_territory_id, enemy_territory_id, num_to_transfer)

			front = attack_planner.getAttack(self.brisk, self)

	def territory_with_max_armies(self):
		candidate = None
		max_armies = 0

		for territory_id, territory in self.get_my_territories_dict().iteritems():
			if candidate == None or territory['num_armies'] > max_armies:
				candidate = territory
				max_armies = territory['num_armies']

		return candidate

	def transfer(self):
		from_territory = self.territory_with_max_armies()

		adjacent_territories = self.map.territories[from_territory['territory']]['adjacent_territories']
		adjacent_territories = set(adjacent_territories).intersection(set(self.get_my_territory_ids()))
		adjacent_territories = list(adjacent_territories)

		num_to_transfer = from_territory['num_armies'] - ARMIES_TO_LEAVE

		if len(adjacent_territories) == 0 or num_to_transfer <= 0:
			self.brisk.end_turn()
		else:
			to_territory_id = self.map.territory_with_most_enemies(adjacent_territories)
			self.brisk.transfer_armies(from_territory['territory'], to_territory_id, num_to_transfer)

		print("ending turn!")

if __name__ == "__main__":
	main()
