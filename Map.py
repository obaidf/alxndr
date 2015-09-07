class Map:
    def __init__(self, map_layout):
        self.territories = {}
        self.continents = {}
        self.border_territories = set()

        self.transform_inputs(map_layout)
        self.compute_mappings()
        self.compute_continent_borders()

    # Transform territory and continent lists to dictionaries
    def transform_inputs(self, map_layout):
        for territory in map_layout['territories']:
            id = territory['territory']
            self.territories[id] = territory
        for continent in map_layout['continents']:
            id = continent['continent']
            self.continents[id] = continent

    # Compute territory -> continent mappings
    def compute_mappings(self):
        for continent_id, continent in self.continents.iteritems():
            for territory_id in continent['territories']:
                try:
                    self.territories[territory_id]['continent'] = continent_id
                except KeyError:
                    print 'Territory does not exist'

    # Compute border territories of all continents
    def compute_continent_borders(self):
        for continent_id, continent in self.continents.iteritems():
            border_territories = self.compute_continent_border(continent)
            self.continents[continent_id]['border_territories'] = border_territories
            self.border_territories.union(set(border_territories))

    # Compute border territories of a continent
    def compute_continent_border(self, continent):
        border_territories = []

        for territory_id, territory in self.territories.iteritems():
            if len(set(territory['adjacent_territories']).intersection(continent['territories'])) != 0:
                border_territories.append(territory_id)

        return border_territories

    # Pick position with most adjacent enemy territories
    # my_territories should be a list of territory IDs
    def territory_with_most_enemies(self, my_territories):
        candidate = None
        highest_count = 0

        for territory_id in my_territories:
            territory = self.territories[territory_id]
            num_adjacent_enemies = 0
            for neighbor_id in territory['adjacent_territories']:
                if neighbor_id not in my_territories:
                    num_adjacent_enemies += 1
            if candidate == None or num_adjacent_enemies > highest_count:
                candidate = territory_id
                highest_count = num_adjacent_enemies

        return candidate

