import copy

SNAKE_W       = 1.0
MONOTONIC_W   = 1.0
FREECELLS_W   = 2.0

snake_matrix = [
    [2, 2**2, 2**3, 2**4],
    [2**8, 2**7, 2**6, 2**5],
    [2**9, 2**10, 2**11, 2**12],
    [2**16, 2**15, 2**14, 2**13]
]

def snake_heuristic(grid):
    score = 0
    for r in range(4):
        for c in range(4):
            score += grid[r][c].number * snake_matrix[r][c]
    return score

def monotonic_heuristic(grid):
    total = 0

    for r in range(4):
        row_vals = [grid[r][c].number for c in range(4)]
        total += monotonic_line_value(row_vals)

    for c in range(4):
        col_vals = [grid[r][c].number for r in range(4)]
        total += monotonic_line_value(col_vals)

    return total

def monotonic_line_value(line):
    inc_score = 0
    dec_score = 0
    for i in range(3):
        if line[i] <= line[i+1]:
            inc_score += line[i+1] - line[i]
        else:
            dec_score += line[i] - line[i+1]
    return max(inc_score, dec_score)

def free_cells_heuristic(grid):
    free_count = 0
    for r in range(4):
        for c in range(4):
            if grid[r][c].number == 0:
                free_count += 1
    return free_count

def combined_heuristic(grid):
    return (
        (SNAKE_W     * snake_heuristic(grid)) +
        (MONOTONIC_W * monotonic_heuristic(grid)) +
        (FREECELLS_W * free_cells_heuristic(grid))
    )

def expectimax(board, depth, is_chance):
    if board.check_loss():
        return float("-inf")
    if depth <= 0:
        return combined_heuristic(board.arr_to_matrix())

    if not is_chance:
        best_val = float("-inf")
        for direction in ["up", "down", "left", "right"]:
            temp_board = copy.deepcopy(board)
            local_score, moved = temp_board.move(direction, ai=True)
            if not moved:
                continue

            val = local_score + expectimax(temp_board, depth - 1, is_chance=True)
            if val > best_val:
                best_val = val
        return best_val

    else:
        empty_tiles = board.get_empty_tiles()
        if not empty_tiles:
            return combined_heuristic(board.arr_to_matrix())

        sum_val = 0
        for tile in empty_tiles:
            idx = board.tiles.index(tile)
            board.tiles[idx].number = 2
            val2 = expectimax(board, depth - 1, is_chance=False)
            sum_val += 0.9 * val2

            board.tiles[idx].number = 4
            val4 = expectimax(board, depth - 1, is_chance=False)
            sum_val += 0.1 * val4

            board.tiles[idx].number = 0

        return sum_val / len(empty_tiles)


def best_move(board, max_depth=4):
    best_dir = "left"
    best_val = float("-inf")

    for direction in ["up", "down", "left", "right"]:
        temp_board = copy.deepcopy(board)
        local_score, moved = temp_board.move(direction, ai=True)
        if not moved:
            continue

        val = local_score + expectimax(temp_board, max_depth - 1, is_chance=True)
        if val > best_val:
            best_val = val
            best_dir = direction

    return best_dir
