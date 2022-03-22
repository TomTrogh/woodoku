import random
import basics
import math
from basics import BLOCKS

def run_game(f_player, grid=None, blocks_to_place=None, select_blocks=False, print_grid=True):
    grid = grid or basics.Grid()
    blocks_to_place = blocks_to_place[:] if blocks_to_place else []

    while True:
        if not blocks_to_place:
            if select_blocks:
                while len(blocks_to_place) < 3:
                    block = input('Block drawn? ')
                    if block in basics.BLOCKS:
                        blocks_to_place.append(block)
                    else:
                        print(f"Block not found: {block}")
                        print(f"Possible values: {', '.join(sorted(basics.BLOCKS))}")
            else:
                blocks_to_place = random_blocks(3)
        if all(not grid.possible_locations(block) for block in blocks_to_place):
            return grid
        moves = f_player(grid, blocks_to_place)
        if not moves:
            print(grid)
            print(blocks_to_place)
            raise ValueError
        for topleft, block in moves:
            if print_grid:
                print(f"Moves: {grid.moves}, Score: {grid.score}")
                print()
                grid.print_with_move(topleft=topleft, block=block)

            grid.place(topleft, block)
            blocks_to_place.remove(block)


def random_blocks(count):
    assert count < len(basics.BLOCKS)
    blocks = []
    while len(blocks) < count:
        block = random.choice(list(basics.BLOCKS))
        if block not in blocks:
            blocks.append(block)
    return blocks


def random_player(grid, blocks_to_place):

    for ix_try in range(3):
        block = random.choice(blocks_to_place)
        block_size = max(tile[0] for tile in BLOCKS[block]) + 1, max(tile[1] for tile in BLOCKS[block]) + 1
        max_row, max_col = grid.size[0] - block_size[0], grid.size[1] - block_size[1]
        topleft = random.randint(0, max_row - 1), random.randint(0, max_col - 1)
        if grid.can_place_block(topleft, block):
            return [(topleft, block)]

    for block in random.sample(blocks_to_place, len(blocks_to_place)):
        possible_locations = tuple(grid.possible_locations(block))
        if possible_locations:
            return [(random.choice(possible_locations), block)]
    raise ValueError('Cannot find valid move...')


def better_player(grid, blocks_to_place):
    possible_moves = []
    for block in blocks_to_place:
        possible_moves.extend([(topleft, block) for topleft in grid.possible_locations(block)])
    best_grid = None
    best_move = None
    for topleft, block in possible_moves:
        next_grid = grid.copy()
        next_grid.place(topleft=topleft, block=block)
        if (not best_grid) or next_grid.score > best_grid.score:
            best_grid = next_grid
            best_move = (topleft, block)
    return [best_move]


def turn_player(grid, blocks_to_place):

    options = [(grid, blocks_to_place, '')]
    best_score = 0
    best_moves = ''

    while options:
        option_grid, blocks, move_history = options.pop(-1)
        for ix_block, block in enumerate(blocks):
            blocks_left = [b for ix_b, b in enumerate(blocks) if ix_b != ix_block]
            possible_locations = option_grid.possible_locations(block)
            if not possible_locations:
                continue
            for topleft in random.sample(option_grid.possible_locations(block), min(100, len(possible_locations))):
                c = option_grid.copy()
                c.place(topleft=topleft, block=block)
                if blocks_left:
                    options.append((c, blocks_left[:], move_history + f"{ix_block}{topleft[0]}{topleft[1]}"))
                if c.score > best_score:
                    best_moves = move_history + f"{ix_block}{topleft[0]}{topleft[1]}"
                    best_score = c.score
    moves = []
    blocks = blocks_to_place[:]
    for move_code in [best_moves[i:i+3] for i in range(0, len(best_moves), 3)]:
        block = blocks[int(move_code[0])]
        topleft = [int(move_code[1]), int(move_code[2])]
        moves.append((topleft, block))
        blocks.remove(block)
    print(moves)
    return moves


def mc_player(grid, blocks_to_place, runcount=300, explore=10):
    options = dict()

    for block in blocks_to_place:
        for topleft in grid.possible_locations(block):
            data = dict(grid=grid.copy(), blocks_to_place=blocks_to_place[:], score=0, plays=0)
            data['grid'].place(topleft, block)
            data['blocks_to_place'].remove(block)
            options[(topleft, block)] = data

    runcount = max(len(options)*10, runcount)
    for ix_run in range(runcount):
        best_option = max(options, key=lambda o: (options[o]['score'] / options[o]['plays'] + explore * math.sqrt(math.log(ix_run) / options[o]['plays'])) if options[o]['plays'] else 9999)
        data = options[best_option]
        res = run_game(random_player, grid=data['grid'].copy(), blocks_to_place=data['blocks_to_place'][:], print_grid=False)
        data['plays'] += 1
        data['score'] += res.moves

    r = sorted(((option, d, d['score'] / d['plays']) for option, d in options.items()), key=lambda l: l[2], reverse=True)

    # print(r[0][0], r[0][1]['score'], r[0][1]['plays'], r[0][2])
    return [(r[0][0][0], r[0][0][1])]


import datetime

def run_games(runs=100, player=None):
    sum_score = 0
    max_score = 0

    t = datetime.datetime.now()
    for ix_run in range(runs):
        grid = run_game(player, print_grid=False)
        sum_score += grid.moves
        if grid.moves > max_score:
            max_score = grid.moves
    print('End', datetime.datetime.now() - t)

    return dict(avg_score=sum_score/runs, max_score=max_score)


if __name__ == '__main__':
    pass
#    g = run_game(mc_player)
#    print(f"Moves: {g.moves}, Score: {g.score}")







