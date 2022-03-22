import itertools
from copy import deepcopy

def add_position(pos1, pos2):
    return pos1[0] + pos2[0], pos1[1] + pos2[1]


def build_zones():
    zones = set()
    for ix in range(9):
        zones.add(tuple((ix, col) for col in range(9)))
        zones.add(tuple((row, ix) for row in range(9)))
    for topleft in itertools.product((0, 3, 6), (0, 3, 6)):
        zone = []
        for tile in itertools.product(range(3), range(3)):
            zone.append(add_position(topleft, tile))
        zones.add(tuple(zone))
    assert len(zones) == 27
    return zones


class Grid:

    size = (9, 9)
    zones = build_zones()

    def __init__(self, empty_tiles=False):
        self.tiles = dict() if empty_tiles else {(i, j): False for (i, j) in itertools.product(range(self.size[0]), range(self.size[1]))}
        self.score = 0
        self.moves = 0
        self.possible_locations_cache = dict()

    def tiles_from(self, orig):
        orig = orig.replace(' ', '')
        for ix_char, character in enumerate(orig):
            self.tiles[(ix_char // 9, ix_char % 9)] = (character == '1')

    def copy(self):
        c = self.__class__(empty_tiles=True)
        c.tiles = {key: value for (key, value) in self.tiles.items()}
        c.score = self.score
        c.moves = self.moves
        c.possible_locations_cache = deepcopy(self.possible_locations_cache)
        return c

    def possible_locations(self, block):
        if block not in self.possible_locations_cache or self.possible_locations_cache[block]['dirty']:
            self.calc_possible_locations(block)
        return self.possible_locations_cache[block]['options']

    def calc_possible_locations(self, block):
        # if possible locations present and dirty: only use these - otherwise use all

        if block in self.possible_locations_cache:
            options = self.possible_locations_cache[block]['options']
        else:
            block_size = max(tile[0] for tile in BLOCKS[block]) + 1,  max(tile[1] for tile in BLOCKS[block]) + 1,
            max_row, max_col = (self.size[0] - block_size[0], self.size[1] - block_size[1])
            options = [topleft for topleft in itertools.product(range(max_row + 1), range(max_col + 1))]

        if block not in self.possible_locations_cache:
            self.possible_locations_cache[block] = dict()

        self.possible_locations_cache[block]['options'] = tuple(topleft for topleft in options if self.can_place_block(topleft=topleft, block=block))
        self.possible_locations_cache[block]['dirty'] = False

    def can_place_block(self, topleft=None, block=None):
        for tile in BLOCKS[block]:
            tile_position = add_position(topleft, tile)
            if self.tiles[tile_position]:
                return False
        return True

    def place(self, topleft=None, block=None):
        for block_tile in BLOCKS[block]:
            tile = add_position(topleft, block_tile)
            assert not self.tiles[tile]
            self.tiles[tile] = True
            self.score += 1
        self.moves += 1
        for cache in self.possible_locations_cache.values():
            cache['dirty'] = True

        self.clean_full_zones()

    def clean_full_zones(self):
        tiles_to_be_cleaned = set()
        for zone in self.zones:
            if all(self.tiles[tile] for tile in zone):
                tiles_to_be_cleaned.update(zone)
                self.score += 18
        for tile in tiles_to_be_cleaned:
            assert self.tiles[tile]
            self.tiles[tile] = False
        self.possible_locations_cache = dict()

    def __str__(self):
        lines = []
        for ix_row in range(self.size[0]):
            line = ''.join('X' if self.tiles[(ix_row, ix_col)] else '_' for ix_col in range(self.size[1]))
            lines.append(line)
        return '\n'.join(lines)

    def print_with_move(self, topleft=None, block=None):
        extra_tiles = {add_position(topleft, tile) for tile in BLOCKS[block]}
        for ix_row in range(9):
            line = ""
            for ix_col in range(9):
                pos = (ix_row, ix_col)
                if self.tiles[pos]:
                    line += " X"
                elif pos in extra_tiles:
                    line += " \033[93mY\033[39m"
                else:
                    line += " -"
            print(line)
        print()


BLOCKS = dict(Wide5=[(0, i) for i in range(5)],
              Wide4=[(0, i) for i in range(4)],
              Wide3=[(0, i) for i in range(3)],
              Wide2=[(0, i) for i in range(2)],
              Single=[(0, 0)],
              Tall5=[(i, 0) for i in range(5)],
              Tall4=[(i, 0) for i in range(4)],
              Tall3=[(i, 0) for i in range(3)],
              Tall2=[(i, 0) for i in range(2)],
              DiagDown2=[(i, i) for i in range(2)],
              DiagDown3=[(i, i) for i in range(3)],
              DiagDown4=[(i, i) for i in range(4)],
              DiagUp2=[(i, 1-i) for i in range(2)],
              DiagUp3=[(i, 2-i) for i in range(3)],
              DiagUp4=[(i, 3-i) for i in range(4)],
              Square=[(0, 0), (0, 1), (1, 0), (1, 1)],
              LUpRight=[(0, 0), (1, 0), (1, 1)],
              LDownRight=[(0, 0), (0, 1), (1, 0)],
              LUpLeft=[(0, 1), (1, 0), (1, 1)],
              LDownLeft=[(0, 0), (0, 1), (1, 1)],
              LLUpRight=[(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],
              LLDownRight=[(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)],
              LLUpLeft=[(0, 2), (1, 2), (2, 2), (2, 1), (2, 0)],
              LLDownLeft=[(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)],
              KnightUpRight=[(0, 0), (1, 0), (2, 0), (2, 1)],
              KnightUpLeft=[(0, 1), (1, 1), (2, 1), (2, 0)],
              KnightRightUp=[(1, 0), (1, 1), (1, 2), (0, 0)],
              KnightRightDown=[(0, 0), (0, 1), (0, 2), (1, 0)],
              KnightDownLeft=[(0, 0), (0, 1), (1, 1), (2, 1)],
              KnightDownRight=[(0, 0), (0, 1), (1, 0), (2, 0)],
              KnightLeftUp=[(1, 0), (1, 1), (1, 2), (0, 2)],
              KnightLeftDown=[(0, 0), (0, 1), (0, 2), (1, 2)],
              TUp=[(0, 1), (1, 0), (1, 1), (1, 2)],
              TDown=[(0, 0), (0, 1), (0, 2), (1, 1)],
              TRight=[(0, 0), (1, 0), (2, 0), (1, 1)],
              TLeft=[(0, 1), (1, 1), (2, 1), (1, 0)],
              TTUp=[(0, 1), (1, 1), (2, 0), (2, 1), (2, 2)],
              TTDown=[(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)],
              TTRight=[(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)],
              TTLeft=[(0, 2), (1, 2), (2, 2), (1, 0), (1, 1)],
              ZVert=[(0, 1), (1, 0), (1, 1), (2, 0)],
              ZHoriz=[(0, 0), (0, 1), (1, 1), (1, 2)],
              SHoriz=[(0, 1), (0, 2), (1, 1), (1, 0)],
              SVert=[(0, 0), (1, 0), (1, 1), (2, 1)],
              Cross=[(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],
              CannonDown=[(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)],
              CannonUp=[(0, 0), (0, 2), (1, 0), (1, 1), (1, 2)],
              CannonLeft=[(0, 0), (0, 1), (1, 1), (2, 0), (2, 1)],
              CannonRight=[(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)]
              )
