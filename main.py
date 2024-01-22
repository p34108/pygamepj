import pygame
import os
import sys
from player import *
from blocks import *
from monsters import *

WIN_WIDTH = 1080
WIN_HEIGHT = 720
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
BACKGROUND_COLOR = "#000000"

FILE_DIR = os.path.dirname(__file__)


class Camera2(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WIN_WIDTH / 2, -t + WIN_HEIGHT / 2

    l = min(0, l)
    l = max(-(camera.width - WIN_WIDTH), l)
    t = max(-(camera.height - WIN_HEIGHT), t)
    t = min(0, t)

    return Rect(l, t, w, h)


def loadLevel():
    global playerX, playerY

    levelFile = open('%s/levels/1.txt' % FILE_DIR)
    line = " "
    commands = []
    while line[0] != "/":
        line = levelFile.readline()
        if line[0] == "[":
            while line[0] != "]":
                line = levelFile.readline()
                if line[0] != "]":
                    endLine = line.find("|")
                    level.append(line[0: endLine])

        if line[0] != "":
            commands = line.split()
            if len(commands) > 1:
                if commands[0] == "player":
                    playerX = int(commands[1])
                    playerY = int(commands[2])
                if commands[0] == "portal":
                    tp = BlockTeleport(int(commands[1]), int(commands[2]), int(commands[3]), int(commands[4]))
                    entities.add(tp)
                    platforms.append(tp)
                    animatedEntities.add(tp)
                if commands[0] == "monster":
                    mn = Monster(int(commands[1]), int(commands[2]), int(commands[3]), int(commands[4]),
                                 int(commands[5]), int(commands[6]))
                    entities.add(mn)
                    platforms.append(mn)
                    monsters.add(mn)


def main():
    loadLevel()
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("Super Mario Boy")
    bg = Surface((WIN_WIDTH, WIN_HEIGHT))

    bg.fill(Color(BACKGROUND_COLOR))

    left = right = False
    up = False
    running = False

    hero = Player2(playerX, playerY)
    entities.add(hero)

    timer = pygame.time.Clock()
    x = y = 0
    for row in level:
        for col in row:
            if col == "-":
                pf = Platform(x, y)
                entities.add(pf)
                platforms.append(pf)
            if col == "*":
                bd = BlockDie(x, y)
                entities.add(bd)
                platforms.append(bd)
            if col == "P":
                pr = Princess(x, y)
                entities.add(pr)
                platforms.append(pr)
                animatedEntities.add(pr)

            x += PLATFORM_WIDTH
        y += PLATFORM_HEIGHT
        x = 0

    total_level_width = len(level[0]) * PLATFORM_WIDTH
    total_level_height = len(level) * PLATFORM_HEIGHT

    camera2 = Camera2(camera_configure, total_level_width, total_level_height)

    while not hero.winner:
        timer.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT:
                return
            if e.type == KEYDOWN and e.key == K_UP:
                up = True
            if e.type == KEYDOWN and e.key == K_LEFT:
                left = True
            if e.type == KEYDOWN and e.key == K_RIGHT:
                right = True
            if e.type == KEYDOWN and e.key == K_LSHIFT:
                running = True

            if e.type == KEYUP and e.key == K_UP:
                up = False
            if e.type == KEYUP and e.key == K_RIGHT:
                right = False
            if e.type == KEYUP and e.key == K_LEFT:
                left = False
            if e.type == KEYUP and e.key == K_LSHIFT:
                running = False

        screen.blit(bg, (0, 0))

        animatedEntities.update()
        monsters.update(platforms)
        camera2.update(hero)
        hero.update(left, right, up, running, platforms)
        for e in entities:
            screen.blit(e.image, camera2.apply(e))
        pygame.display.update()

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    return level_map


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, w, h):
        super().__init__(tiles_group, all_sprites)
        self.image = pygame.transform.scale(tile_images[tile_type], (int(w), int(h)))
        self.rect = self.image.get_rect()
        self.rect.x = int(pos_x)
        self.rect.y = int(pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet):
        super().__init__(player_group, all_sprites)
        self.frames = list()
        for i in sheet:
            self.frames.append(pygame.transform.scale(i, (46, 60)))
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 630 - self.rect.h
        self.fps = 0

    def update(self, x, y):
        player.rect.y += 1
        if pygame.sprite.spritecollideany(player, tiles_group) and x != 0:
            self.fps += 1
            if self.fps == 6:
                self.fps = 0
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
        player.rect.y -= 1
        ans_x = x * 5
        ans_y = y * 5
        if pygame.sprite.spritecollideany(self, tiles_group):
            self.rect.x -= x * 5
            self.rect.y -= y * 5
            ans_x = 0
            ans_y = 0
            for i in range(5):
                if x != 0:
                    self.rect.x += x
                    ans_x += x
                if y != 0:
                    self.rect.y += y
                    ans_y += y
                if pygame.sprite.spritecollideany(self, tiles_group):
                    self.rect.x -= x
                    ans_x -= x
                    self.rect.y -= y
                    ans_y -= y
                    break
        return ans_x, ans_y


class Camera:
    def __init__(self):
        self.dx = 0

    def apply(self, obj):
        obj.rect.x += self.dx

    def update(self, target):
        self.dx = -(target.rect.x - 400)
        if self.dx > 0:
            target.image = pygame.transform.flip(target.frames[target.cur_frame], True, False)
        elif self.dx < 0:
            target.image = target.frames[target.cur_frame]


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(coins_group, all_sprites)
        self.image = coin_image
        self.rect = self.image.get_rect()
        self.rect.x = int(pos_x)
        self.rect.y = int(pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        super().__init__(enemy_group, all_sprites)
        self.image = pygame.transform.scale(tile_images[3], (48, 48))
        self.rect = self.image.get_rect()
        self.rect.x = int(pos_x)
        self.rect.y = 720 - 90 - self.rect.h
        self.mask = pygame.mask.from_surface(self.image)
        self.v = 50

    def update(self):
        if pygame.sprite.spritecollideany(self, tiles_group):
            self.v *= -1
        for sprite in decor_group:
            if pygame.sprite.collide_mask(self, sprite):
                self.v *= -1
        self.rect.x += self.v / FPS


class Decor(pygame.sprite.Sprite):
    def __init__(self, pos_x, tile_type):
        super().__init__(decor_group, all_sprites)
        if int(tile_type) == 0:
            self.image = pygame.transform.scale(tile_images[4], (128, 128))
        else:
            self.image = pygame.transform.scale(tile_images[5], (170, 170))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = int(pos_x)
        self.rect.y = 720 - 90 - self.rect.h


class Castle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(coins_group, all_sprites)
        self.image = pygame.transform.scale(tile_images[6], (300, 300))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = 9320
        self.rect.y = 720 - 90 - self.rect.h


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    screen.fill((0, 222, 0))
    text1 = "level 1"
    text2 = "level 2"
    font = pygame.font.Font(None, 100)
    string_rendered2 = font.render(text2, 1, pygame.Color('white'))
    string_rendered1 = font.render(text1, 1, pygame.Color('white'))
    intro_rect1 = string_rendered1.get_rect()
    intro_rect1.x = (1080 - intro_rect1.w * 3) // 4
    intro_rect1.y = 100
    intro_rect2 = string_rendered2.get_rect()
    intro_rect2.x = (1080 - intro_rect2.w * 3) // 4
    intro_rect2.y = 300
    screen.fill((0, 0, 0), (intro_rect1.x - 20, intro_rect1.y - 20, intro_rect1.w + 40, intro_rect1.h + 40))
    screen.fill((0, 0, 0), (intro_rect2.x - 20, intro_rect2.y - 20, intro_rect2.w + 40, intro_rect2.h + 40))
    screen.blit(string_rendered1, intro_rect1)
    screen.blit(string_rendered2, intro_rect2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = event.pos
                if (intro_rect1.x - 20 <= x <= intro_rect1.x + 20 + intro_rect1.w and
                        intro_rect1.y - 20 <= y <= intro_rect1.y + intro_rect1.h + 20):
                    return
                if (intro_rect2.x - 20 <= x <= intro_rect2.x + 20 + intro_rect2.w and
                        intro_rect2.y - 20 <= y <= intro_rect2.y + intro_rect2.h + 20):
                    main()
        pygame.display.flip()
        clock.tick(FPS)


def end(line):
    font = pygame.font.Font(None, 200)
    string_rendered = font.render(line, 1, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    w = intro_rect.w
    h = intro_rect.h
    x = 540 - w // 2
    y = 360 - h // 2
    all_sprites.draw(screen)
    player_group.draw(screen)
    screen.fill((0, 0, 0), (x - 20, y - 20, w + 40, h + 40))
    screen.blit(string_rendered, (x, y, w, h))

    font = pygame.font.Font(None, 50)
    string_rendered = font.render(str(coins_cnt), 1, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    screen.fill((0, 0, 0), (0, 0, 1080, 50))
    screen.blit(string_rendered, (1000, 10, 50, 50))
    screen.blit(coin_image, (925, 1, 48, 48))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def generate_level(level):
    cnt = 0
    Castle()
    for i in range(len(level)):
        if level[i] == "---":
            cnt = cnt + 1
        else:
            if cnt == 3:
                list_cor = [int(x) for x in level[i].split()]
                for j in range(list_cor[2] // 48):
                    if list_cor[4] == 1:
                        pos_y = 48 * (j + 1) + 6
                        minus = 0
                        while pos_y > list_cor[3]:
                            pos_y = 48 * (j - minus) + 6
                            minus += 1
                        Tile(cnt % 3, list_cor[0] + 48 * j, 720 - 90 - pos_y, 48, pos_y)
                        Coin(list_cor[0] + 48 * j, 720 - 90 - pos_y - 48)
                    else:
                        pos_y = 48 * (j + 1) + 6
                        minus = 0
                        while pos_y > list_cor[3]:
                            pos_y = 48 * (j - minus) + 6
                            minus += 1
                        Tile(cnt % 3, list_cor[0] + list_cor[2] - 48 * (j + 1), 720 - 90 - pos_y, 48, pos_y)
                        Coin(list_cor[0] + list_cor[2] - 48 * (j + 1), 720 - 90 - pos_y - 48)
            elif cnt == 2:
                list_cor = [int(x) for x in level[i].split()]
                Tile(cnt % 3, list_cor[0], list_cor[1], list_cor[2], list_cor[3])
                for j in range(list_cor[2] // 48 - 2):
                    Coin(list_cor[0] + 48 * (j + 1), list_cor[1] - 48)
            elif cnt == 1:
                list_cor = [int(x) for x in level[i].split()]
                Tile(cnt % 3, list_cor[0], list_cor[1], list_cor[2], list_cor[3])
                Coin(list_cor[0] + 24, list_cor[1] - 48)
            elif cnt == 4:
                list_cor = [int(x) for x in level[i].split()]
                Enemy(list_cor[0])
            elif cnt == 5:
                list_cor = level[i].split()
                Decor(list_cor[0], list_cor[1])
            else:
                list_cor = level[i].split()
                Tile(cnt % 3, list_cor[0], list_cor[1], list_cor[2], list_cor[3])


if __name__ == '__main__':
    FPS = 60

    level = []
    entities = pygame.sprite.Group()
    animatedEntities = pygame.sprite.Group()
    monsters = pygame.sprite.Group()
    platforms = []
    pygame.init()
    size = WIDTH, HEIGHT = 1080, 720
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    start_screen()
    tile_images = [
        load_image('ground.png'),
        load_image('high_platform.png'),
        load_image('fly_platform.png'),
        load_image('enemy.png'),
        load_image('bush.png'),
        load_image('tree.png'),
        load_image('castle.png')
    ]
    coin_image = pygame.transform.scale(load_image('coin.png'), (48, 48))
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    coins_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    decor_group = pygame.sprite.Group()
    player = Player([load_image("M1.png"), load_image("M2.png"), load_image("M3.png")])
    fon = pygame.transform.scale(load_image('Background.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    generate_level(load_level('level.txt'))
    all_sprites.draw(screen)
    coins_cnt = 0
    font = pygame.font.Font(None, 50)

    string_rendered = font.render(str(coins_cnt), 1, pygame.Color('white'))
    intro_rect = string_rendered.get_rect()
    screen.fill((0, 0, 0), (0, 0, 1080, 50))
    screen.blit(string_rendered, (1000, 10, 50, 50))
    screen.blit(coin_image, (925, 1, 48, 48))

    camera = Camera()
    running = True
    up = False
    fly_hight = 0
    down = False
    right = False
    left = False
    line = "GAME OVER"
    while running:
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == 1073741905:
                    down = True
                if event.key == 1073741906:
                    player.rect.y += 1
                    if pygame.sprite.spritecollideany(player, tiles_group):
                        up = True
                    player.rect.y -= 1
                if event.key == 1073741903:
                    right = True
                if event.key == 1073741904:
                    left = True
            if event.type == pygame.KEYUP:
                if event.key == 1073741905:
                    down = False
                if event.key == 1073741906:
                    up = False
                    fly_hight = 0
                if event.key == 1073741903:
                    right = False
                if event.key == 1073741904:
                    left = False
        x = 0
        y = 0
        if up:
            player.rect.y -= 5
            y = -1
        if down:
            player.rect.y += 5
            y = 1
        if right:
            player.rect.x += 1
            if pygame.sprite.spritecollideany(player, tiles_group):
                left = False
                x = 0
            else:
                player.rect.x += 5
                x = 1
            player.rect.x -= 1
        if left:
            player.rect.x -= 1
            if pygame.sprite.spritecollideany(player, tiles_group):
                x = 0
            else:
                player.rect.x -= 5
                x = -1
            player.rect.x += 1
        ans_x, ans_y = player.update(x, y)
        if up:
            fly_hight -= ans_y
            player.rect.y -= 1
            if fly_hight > 336 or pygame.sprite.spritecollideany(player, tiles_group):
                up = False
                fly_hight = 0
            player.rect.y += 1
        player.rect.y += 1
        if not pygame.sprite.spritecollideany(player, tiles_group) and not up:
            for i in range(5):
                player.rect.y += 1
                if pygame.sprite.spritecollideany(player, tiles_group):
                    break
        player.rect.y -= 1
        if player.rect.y > 720:
            running = False
        for sprite in enemy_group:
            if pygame.sprite.collide_mask(player, sprite):
                running = False
        for sprite in coins_group:
            if pygame.sprite.collide_mask(player, sprite):
                if sprite.rect.w == 300:
                    line = "WINNER"
                    running = False
                else:
                    sprite.kill()
                    coins_cnt += 1
        enemy_group.update()
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.draw(screen)
        player_group.draw(screen)

        string_rendered = font.render(str(coins_cnt), 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        screen.fill((0, 0, 0), (0, 0, 1080, 50))
        screen.blit(string_rendered, (1000, 10, 50, 50))
        screen.blit(coin_image, (925, 1, 48, 48))

        pygame.display.flip()
        clock.tick(FPS)
    end(line)
    pygame.quit()

# if __name__ == "__main__":
#     main()
