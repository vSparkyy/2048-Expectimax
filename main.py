import pygame
import sys
import os
import random
import time
import solver

pygame.init()

colours = {
    "cream": (238, 228, 218),
    "light_gray": (119, 110, 101),
    "light_brown": (205, 193, 180),
    "dark_brown": (187, 173, 160),
    "white": (250, 248, 239),
    "creamy_orange": (237, 224, 200),
    "white2": (249, 246, 242),
    "light_orange": (242, 177, 121),
    "orange": (245, 149, 99),
    "orangey_red": (246, 124, 95),
    "red": (246, 94, 59),
    "gold": (237, 207, 114),
    "bright_gold": (237, 204, 97),
    "bright_yellow": (237, 200, 80),
    "yellow": (237, 197, 63),
    "dark_yellow": (237, 194, 46),
    "dark_gray": (119, 110, 101),
}

screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("2048")
clock = pygame.time.Clock()

default_font = pygame.font.Font(
    os.path.join(os.path.dirname(__file__), "assets/montserrat_regular.ttf"), 36
)
text_font = pygame.font.Font(
    os.path.join(os.path.dirname(__file__), "assets/montserrat_regular.ttf"), 24
)
bold_font = pygame.font.Font(
    os.path.join(os.path.dirname(__file__), "assets/montserrat_bold.ttf"), 36
)

def save_score():
    with open(os.path.join(os.path.dirname(__file__), "assets/highscore.txt"), "r") as f:
        highscore = int(f.read())
    if game.score > highscore:
        with open(os.path.join(os.path.dirname(__file__), "assets/highscore.txt"), "w") as f:
            f.write(str(game.score))

class Tile:
    def __init__(self, position, size, number, line_space=15):
        self.position = position
        self.line_space = line_space
        self.number = number
        self.size = size
        self.colour_chart = {
            0: colours["light_brown"],
            2: colours["cream"],
            4: colours["creamy_orange"],
            8: colours["light_orange"],
            16: colours["orange"],
            32: colours["orangey_red"],
            64: colours["red"],
            128: colours["gold"],
            256: colours["bright_gold"],
            512: colours["bright_yellow"],
            1024: colours["yellow"],
            2048: colours["dark_yellow"],
        }

    def draw(self):
        tile_color = (
            self.colour_chart[self.number]
            if self.number in self.colour_chart
            else colours["dark_gray"]
        )

        pygame.draw.rect(
            screen,
            tile_color,
            (self.position[0], self.position[1], self.size, self.size),
            border_radius=5,
        )

        if self.number != 0:
            text = bold_font.render(
                str(self.number),
                True,
                colours["light_gray"] if self.number in [2, 4] else colours["white2"],
            )
            text_rect = text.get_rect(
                center=(
                    self.position[0] + self.size // 2,
                    self.position[1] + self.size // 2,
                )
            )
            screen.blit(text, text_rect)

class Grid:
    def __init__(self, size, position):
        self.size = size
        self.position = position
        self.line_space = 15
        self.score = 0
        self.tile_size = (self.size - 5 * self.line_space) // 4
        self.starting_state()

    def starting_state(self):
        self.tiles = []
        self.score = 0

        for i in range(16):
            r, c = i // 4, i % 4
            x = (
                self.position[0]
                + self.line_space
                + c * (self.tile_size + self.line_space)
            )
            y = (
                self.position[1]
                + self.line_space
                + r * (self.tile_size + self.line_space)
            )
            self.tiles.append(Tile((x, y), self.tile_size, 0))

        self.original_positions = [tile.position for tile in self.tiles]
        self.generate_tiles(count=2)

    def draw_grid(self, draw_tiles=True):
        screen.fill(colours["white"])
        self.draw_stats()

        pygame.draw.rect(
            screen,
            colours["dark_brown"],
            (self.position[0], self.position[1], self.size, self.size),
            border_radius=5,
        )

        if draw_tiles:
            self.draw_tiles()

    def draw_tiles(self):
        for tile in self.tiles:
            tile.draw()

    def draw_stats(self):
        with open(os.path.join(os.path.dirname(__file__), "assets/highscore.txt"), "r") as f:
            text = f.read()
            if text:
                highscore = int(text)
            else:
                highscore = 0

        def create(title, text, pos, dimensions): 
            area = pygame.Rect(pos[0], pos[1], dimensions[0], dimensions[1])
            pygame.draw.rect(screen, colours["light_brown"], area, border_radius=5)
            title_surf = bold_font.render(title, True, colours["light_gray"])
            title_rect = title_surf.get_rect(midtop=(area.centerx, area.top + 5))
            screen.blit(title_surf, title_rect)

            picked_size = 36
            for size in reversed(range(14, 37)):
                fnt = pygame.font.Font(os.path.join(os.path.dirname(__file__), "assets/montserrat_bold.ttf"), size)
                test_surf = fnt.render(text, True, colours["white"])
                if test_surf.get_width() <= area.width - 20 and test_surf.get_height() <= area.height / 2:
                    picked_size = size
                    break

            _font = pygame.font.Font(os.path.join(os.path.dirname(__file__), "assets/montserrat_bold.ttf"), picked_size)
            _surf = _font.render(text, True, colours["white"])
            _rect = _surf.get_rect(center=(area.centerx, area.centery + 10))
            screen.blit(_surf, _rect)

        create("SCORE", str(self.score), (150, 75), (225, 100))
        create("BEST", str(highscore), (410, 75), (225, 100))

    def draw_empty_tiles(self):
        for x, y in self.original_positions:
            pygame.draw.rect(
                screen,
                colours["light_brown"],
                (x, y, self.tile_size, self.tile_size),
                border_radius=5,
            )

    def get_empty_tiles(self):
        return [tile for tile in self.tiles if tile.number == 0]

    def arr_to_matrix(self):
        matrix = []
        for i in range(0, len(self.tiles), 4):
            matrix.append(self.tiles[i : i + 4])
        return matrix

    def matrix_to_arr(self, matrix):
        return [tile for row in matrix for tile in row]

    def generate_tiles(self, count=1, animate=True):
        generated = []

        for _ in range(count):
            random_number = random.choices([2, 4], weights=[0.9, 0.1])[0]
            empty_tiles = [tile for tile in self.tiles if tile.number == 0]

            if empty_tiles:
                empty_tile = random.choice(empty_tiles)
                empty_tile.number = random_number
                generated.append(empty_tile)

        if generated and animate:
            self.pop_in_batch(generated)

    def pop_in_batch(self, tiles, step=6):
        tile_size = self.tile_size
        originals = [(t.position[0], t.position[1]) for t in tiles]

        for size in range(0, tile_size + 1, step):
            self.draw_grid(draw_tiles=False)
            self.draw_empty_tiles()

            for tile in self.tiles:
                if tile not in tiles:
                    tile.draw()

            for i, tile in enumerate(tiles):
                ox, oy = originals[i]
                tile.size = size
                tile.position = (
                    ox + (tile_size - size) // 2,
                    oy + (tile_size - size) // 2,
                )
                tile.draw()

            pygame.display.flip()
            clock.tick(300)

        for i, tile in enumerate(tiles):
            tile.size = tile_size
            tile.position = originals[i]

    def pop_out_batch(self, tiles, step=5, max_size=25):
        tile_size = self.tile_size
        originals = [(t.position[0], t.position[1]) for t in tiles]

        for size in range(tile_size, tile_size + max_size, step):
            self.draw_grid(draw_tiles=False)
            self.draw_empty_tiles()

            for tile in self.tiles:
                if tile not in tiles:
                    tile.draw()

            for i, tile in enumerate(tiles):
                ox, oy = originals[i]
                tile.size = size
                tile.position = (
                    ox - (size - tile_size) // 2,
                    oy - (size - tile_size) // 2,
                )
                tile.draw()

            pygame.display.flip()
            clock.tick(200)

        for size in range(tile_size + max_size, tile_size, -step):
            self.draw_grid(draw_tiles=False)
            self.draw_empty_tiles()

            for tile in self.tiles:
                if tile not in tiles:
                    tile.draw()

            for i, tile in enumerate(tiles):
                ox, oy = originals[i]
                tile.size = size
                tile.position = (
                    ox - (size - tile_size) // 2,
                    oy - (size - tile_size) // 2,
                )
                tile.draw()

            pygame.display.flip()
            clock.tick(200)

        for i, tile in enumerate(tiles):
            tile.size = tile_size
            tile.position = originals[i]

    def move(self, direction, animate=True, ai=False):
        board = self.arr_to_matrix()
        score = 0

        offsets = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1),
        }

        offset = offsets[direction]
        merged_flags = [[False] * 4 for _ in range(4)]
        moves_report = []
        moved = False

        y_range = range(4) if offset[0] <= 0 else range(3, -1, -1)
        x_range = range(4) if offset[1] <= 0 else range(3, -1, -1)

        for y in y_range:
            for x in x_range:
                if board[y][x].number == 0:
                    continue

                old_num = board[y][x].number
                ny, nx = y + offset[0], x + offset[1]

                while 0 <= ny < 4 and 0 <= nx < 4 and board[ny][nx].number == 0:
                    ny += offset[0]
                    nx += offset[1]

                if not (0 <= ny < 4 and 0 <= nx < 4):
                    ny -= offset[0]
                    nx -= offset[1]

                if ny == y and nx == x:
                    continue

                if (
                    board[ny][nx].number == old_num
                    and not merged_flags[ny][nx]
                    and board[ny][nx].number != 0
                ):
                    merged_flags[ny][nx] = True
                    moved = True
                    moves_report.append(
                        (
                            Tile(board[y][x].position, board[y][x].size, old_num),
                            ny,
                            nx,
                            True,
                        )
                    )
                    board[ny][nx].number = old_num * 2
                    score += board[ny][nx].number
                    board[y][x].number = 0

                else:
                    if board[ny][nx].number != 0 and board[ny][nx].number != old_num:
                        ny -= offset[0]
                        nx -= offset[1]

                        if ny == y and nx == x:
                            continue

                    moved = True
                    moves_report.append(
                        (
                            Tile(board[y][x].position, board[y][x].size, old_num),
                            ny,
                            nx,
                            False,
                        )
                    )
                    board[ny][nx].number = old_num
                    board[y][x].number = 0

        if ai:
            return score, moved

        if not moved:
            return

        if animate:
            self.animate_moves(moves_report)
            self.tiles = self.matrix_to_arr(board)

        merged_positions = {}
        for move_item in moves_report:
            if move_item[3]:
                final_tile = board[move_item[1]][move_item[2]]
                merged_positions[(move_item[1], move_item[2])] = final_tile

        if merged_positions and animate:
            self.pop_out_batch(list(merged_positions.values()))

        self.generate_tiles()
        self.score += score
        save_score()

    def animate_moves(self, moves_report, duration=0.12):
        if not moves_report:
            return

        final_board = self.arr_to_matrix()
        moving_set = set()

        for m in moves_report:
            moving_set.add((m[1], m[2]))

        def cell_to_xy(r, c):
            return (
                self.position[0]
                + self.line_space
                + c * (self.tile_size + self.line_space),
                self.position[1]
                + self.line_space
                + r * (self.tile_size + self.line_space),
            )

        start_time = time.time()

        while True:
            now = time.time()
            t = (now - start_time) / duration

            if t >= 1.0:
                t = 1.0

            self.draw_grid(draw_tiles=False)
            self.draw_empty_tiles()

            for r in range(4):
                for c in range(4):
                    if final_board[r][c].number != 0 and (r, c) not in moving_set:
                        final_board[r][c].draw()

            for tile_copy, fr, fc, is_merge in moves_report:
                start_x, start_y = tile_copy.position
                end_x, end_y = cell_to_xy(fr, fc)
                cur_x = start_x + (end_x - start_x) * t
                cur_y = start_y + (end_y - start_y) * t
                temp_tile = Tile((cur_x, cur_y), self.tile_size, tile_copy.number)
                temp_tile.draw()

            pygame.display.flip()
            clock.tick(60)

            if t >= 1.0:
                break

    
    def check_loss(self):
        matrix = self.arr_to_matrix()
        for row in matrix:
            for tile in row:
                if tile.number == 0:
                    return False
        for r in range(4):
            for c in range(4):
                val = matrix[r][c].number
                if r < 3 and matrix[r+1][c].number == val:
                    return False
                if c < 3 and matrix[r][c+1].number == val:
                    return False
        return True
    
    def check_win(self):
        for tile in self.tiles:
            if tile.number == 2048:
                return True
        return False


game = Grid(500, (150, 200))
active = False
won = False
continued = False

while True:
    game.draw_grid()

    if game.check_win() and not continued: 
        win_text = bold_font.render("                             You WON!\nPress R to restart or Q to continue playing", True, colours["white"])
        pygame.draw.rect(screen, colours["dark_yellow"], (5, 345, 790, 110), border_radius=10)
        pygame.draw.rect(screen, colours["light_brown"], (10, 350, 780, 100), border_radius=10)
        screen.blit(win_text, (15, 350))
        won = True
    
    if game.check_loss():
        lost_text = bold_font.render("You LOST! Press R to restart", True, colours["white"])
        pygame.draw.rect(screen, colours["red"], (140, 370, 535, 110), border_radius=10)
        pygame.draw.rect(screen, colours["light_brown"], (145, 375, 525, 100), border_radius=10)
        screen.blit(lost_text, (150, 400))
        save_score()

    if active and not game.check_loss() and not won:
        best_move = solver.best_move(game)
        game.move(best_move)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game.starting_state()
                won = False
                active = False

            if event.key == pygame.K_q and won:
                active = False
                continued = True

            if event.key == pygame.K_s:
                active = not active

            if ((not won) or continued) and not active:
                if event.key == pygame.K_UP:
                    game.move("up")

                elif event.key == pygame.K_DOWN:
                    game.move("down")

                elif event.key == pygame.K_LEFT:
                    game.move("left")

                elif event.key == pygame.K_RIGHT:
                    game.move("right")

    pygame.display.flip()
    clock.tick(120)
