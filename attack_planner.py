def getAttack(bot, player):
	mapLayOut = bot.get_map_layout()
	playerStatus = bot.get_player_status()
	allAttackAdvantages = computeAttackAdvantages(bot, player)

	if len(allAttackAdvantages) == 0:
		return None

	attack = bestAttack(allAttackAdvantages)
	return attack

def computeAttackAdvantages(brisk, player):
	mapLayOut = brisk.get_map_layout()
	playerStatus = brisk.get_player_status()
	game_state = brisk.get_game_state()

	allAttackAdvantages = []
	allTerritories = mapLayOut['territories']
	ourTerritories = playerStatus['territories']

	player.update_state()
	my_territories = player.get_my_territories_dict()

	our_territory_ids = [t['territory'] for t in ourTerritories]
	for territory in allTerritories:
		if territory['territory'] in our_territory_ids:
			for neighbor in territory['adjacent_territories']:
				if neighbor not in our_territory_ids and my_territories[territory['territory']]['num_armies'] > 2:
					allAttackAdvantages.append(attackAdvantage(territory['territory'], neighbor, game_state))
	return allAttackAdvantages


def attackAdvantage(our_id, enemy_id, game_state):
	all_territories = game_state['territories']
	attacker_troops = 0
	defender_troops = 0
	for t in all_territories:
		if (our_id == t['territory']):
			attacker_troops = t['num_armies']
		if (enemy_id == t['territory']):
			defender_troops = t['num_armies']
	return {"attacking_territory": our_id, "enemy_territory": enemy_id, "attack_advantage" : attacker_troops - defender_troops}

def bestAttack(allAttackAdvantages):
	attacker_id = allAttackAdvantages[0]['attacking_territory']
	enemy_id = allAttackAdvantages[0]['enemy_territory']
	attack_advantage = allAttackAdvantages[0]['attack_advantage']

	for a in allAttackAdvantages:
		if attack_advantage < a['attack_advantage']:
			attack_advantage = a['attack_advantage']
			attacker_id = a['attacking_territory']
			enemy_id = a['enemy_territory']
	return {"our_territory": attacker_id, "enemy_territory": enemy_id, "attack_advantage" : attack_advantage}


