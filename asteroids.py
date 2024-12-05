import py_compile
#from pygame.locals import *
import pygame
import random
from os import path
from abc import ABCMeta, abstractmethod
import time


img_dir = path.dirname(__file__)

# zmienne globalne, "stałe"
WIDTH = 480
HEIGHT = 600
FPS = 60
POWERUP_TIME = 5000

# zmienne kolorów RGB
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))   # #############
pygame.display.set_caption("Asteroids")     # ############
clock = pygame.time.Clock()     # ############
font_name = pygame.font.match_font('arial')

# Load all game graphics
background = pygame.image.load(path.join(img_dir, "background.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "playerShip1_orange.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, "laserBlue16.png")).convert()
meteor_images = []
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_big2.png', 'meteorBrown_med1.png',
               'meteorBrown_med3.png', 'meteorBrown_small1.png', 'meteorBrown_small2.png',
               'meteorBrown_tiny1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())

explosion_animation = {}
explosion_animation['lg'] = []
explosion_animation['sm'] = []
explosion_animation['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_animation['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_animation['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_animation['player'].append(img)
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, "shield_gold.png")).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, "bolt_gold.png")).convert()


# Funkcja wyświetla ilość punktów zdobytych przez gracza w określonym przez parametry miejscu
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# Funkcja wyświetla pasek pasek tarczy na współrzędnych określonych w parametrach oraz
# wypełnia go na zielono częsci podanej w parametrze percent
def draw_shield_bar(surf, x, y, percent):
    if percent < 0:
        percent = 0
    BAR_LENGHT = 100
    BAR_HEIGHT = 10
    fill = (percent / 100) * BAR_LENGHT
    outline_rect = pygame.Rect(x, y, BAR_LENGHT, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

# Funkcja wyświetla mały obrazek statku w ilości odpowiadającej obecnej ilości szans gracza
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "Asteroids", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys to move, Space to fire", 22, WIDTH/2, HEIGHT / 2)
    draw_text(screen, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.RECEIVER = CommandReceiver()
        self.MOVE_RIGHT = MoveRightCommand(self.RECEIVER)
        self.MOVE_LEFT = MoveLeftCommand(self.RECEIVER)
        self.SHOOT = ShootCommand(self.RECEIVER)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        # Czas trwania mocy po zebraniu obiektu ulepszającego właściwości statku gracza
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()
        # odkrywanie
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        self.speedx = 0
        # Rejestrowanie komend przy użyciu invokera (InputHandler)
        command = InputHandler()

        # Wywołanie komend zarejestrowanych przez Invoker (InputHandler)
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            command.register("LEFT", self.MOVE_LEFT)
            command.execute("LEFT")
            self.speedx = self.RECEIVER.move_left()
        if keystate[pygame.K_RIGHT]:
            command.register("RIGHT", self.MOVE_RIGHT)
            command.execute("RIGHT")
            self.speedx = self.RECEIVER.move_right()
        if keystate[pygame.K_SPACE]:
            command.register("SHOOT", self.SHOOT)
            command.execute("SHOOT")
            if self.RECEIVER.move_right():
                self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                self.game.all_sprites.add(bullet)
                self.game.bullets.add(bullet)
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                self.game.all_sprites.add(bullet1)
                self.game.all_sprites.add(bullet2)
                self.game.bullets.add(bullet1)
                self.game.bullets.add(bullet2)

    def hide(self):
        # tymczasowo ukryj obiekt gracza
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


class Action(metaclass=ABCMeta):    # Command interface

    @staticmethod
    @abstractmethod
    def execute():
        pass


class MoveRightCommand(Action):     # ConcreteCommand

    def __init__(self, receiver):
        self.receiver = receiver

    def execute(self):
        self.receiver.move_right()


class MoveLeftCommand(Action):      # ConcreteCommand

    def __init__(self, receiver):
        self.receiver = receiver

    def execute(self):
        self.receiver.move_left()


class ShootCommand(Action):     # ConcreteCommand

    def __init__(self, receiver):
        self.receiver = receiver

    def execute(self):
        self.receiver.shoot()


class InputHandler: #Invoker

    """The Invoker Class"""

    def __init__(self):
        self._commands = {}
        self._history = []

    @property
    def history(self):
        return self._history

    def register(self, command_name, command):
        self._commands[command_name] = command

    def execute(self, command_name):
        if command_name in self._commands.keys():
            self._history.append((time.time(), command_name))
            self._commands[command_name].execute()
        else:
            print(f"Command [{command_name}] not recognised")


class CommandReceiver:  # Receiver

    def move_right(self):
        # print("moved right")
        return 8

    def move_left(self):
        # print("moved left")
        return -8

    def shoot(self):
        # print("bullet shot")
        return True


def new_asteroid(all_sprites, asteroids):

    chosen_move_strategy = random.randrange(0, 3)
    strategy_type = None

    if chosen_move_strategy == 0:
        strategy_type = XShiftStrategy()
    elif chosen_move_strategy == 1:
        strategy_type = StraightAtPlayerStrategy()
    elif chosen_move_strategy == 2:
        strategy_type = RotationStrategy()

    a = Asteroid(strategy_type)
    # a.set_strategy(strategy_type)
    # print(a.get_strategy())

    all_sprites.add(a)
    asteroids.add(a)

    return all_sprites, asteroids


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, strategy):

        self._strategy = strategy

        pygame.sprite.Sprite.__init__(self)
        self.image_original = random.choice(meteor_images)
        self.image_original.set_colorkey(BLACK)
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width) #
        self.rect.y = random.randrange(-150, -100) #
        self.speedy = random.randrange(1, 8) #
        self.speedx = random.randrange(-3, 3) #
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8) #
        self.last_update = pygame.time.get_ticks()

    def get_strategy(self):
        return self._strategy

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rotation = (self.rotation + self.rotation_speed) % 360
            new_image = pygame.transform.rotate(self.image_original, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()

        self.move_strategy()
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # Asteroida
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

    def move_strategy(self):
        self._strategy.move_strategy()


class Strategy(metaclass=ABCMeta):

    @abstractmethod
    def move_strategy(self):
        pass
        print("Error: Strategy not chosen")


class XShiftStrategy(Strategy):
    def move_strategy(self):
        pass
        print("XShiftStrategy")


class StraightAtPlayerStrategy(Strategy):
    def move_strategy(self):
        pass
        print("StraightAtPlayerStrategy")


class RotationStrategy(Strategy):
    def move_strategy(self):
        pass
        print("RotationStrategy")


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()


class PowerupObject(pygame.sprite.Sprite):
    def __init__(self, center, power_type):
        pygame.sprite.Sprite.__init__(self)
        self.type = power_type
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 0

    def get_speedy(self):
        return self.speedy

    def get_center(self):
        return self.rect.center

    def get_power_type(self):
        return self.type


class PowerupType(pygame.sprite.Sprite):
    def __init__(self, powerup):
        self.powerup = powerup

    def get_speedy(self):
        return self.powerup.get_speedy()

    def get_center(self):
        return self.powerup.get_center()

    def get_power_type(self):
        return self.powerup.get_power_type()


class Powerup(PowerupType):
    def __init__(self, powerup):
        pygame.sprite.Sprite.__init__(self)
        super(Powerup, self).__init__(powerup)
        self.type = self.get_power_type()
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = self.get_center()
        self.speedy = self.get_speedy()

    def update(self):
        self.rect.y += self.speedy
        self.rect.y += self.speedy
        # kill if it moves off the top of the screen
        if self.rect.top > HEIGHT:
            self.kill()

    def get_speedy(self):
        return super(Powerup, self).get_speedy()

    def get_center(self):
        return super(Powerup, self).get_center()

    def get_power_type(self):
        return super(Powerup, self).get_power_type()


class RestoreShield(PowerupType):

    def __init__(self, powerup):
        super(RestoreShield, self).__init__(powerup)

    def get_speedy(self):
        return super(RestoreShield, self).get_speedy() + 2

    def get_center(self):
        return super(RestoreShield, self).get_center()

    def get_power_type(self):
        return super(RestoreShield, self).get_power_type()


class UpgradeBullet(PowerupType):

    def __init__(self, powerup):
        super(UpgradeBullet, self).__init__(powerup)

    def get_speedy(self):
        return super(UpgradeBullet, self).get_speedy() + 4

    def get_center(self):
        return super(UpgradeBullet, self).get_center()

    def get_power_type(self):
        return super(UpgradeBullet, self).get_power_type()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self. image = explosion_animation[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_animation[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_animation[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Game:

    __instance = None

    def __init__(self, arg):
        if not Game.__instance:
            Game.__instance = Game.__Game(arg)

        else:
            Game.__instance.test = arg

    def __getattr__(self, name):
        return getattr(self.__instance, name)

    class __Game:

        def __init__(self, test):
            self.test = test
            self.running = True
            self.game_over = True
            self.all_sprites = None
            self.asteroids = None
            self.bullets = None
            self.powerups = None
            self.hits = None
            self.score = None
            self.pow = None
            self.action = InputHandler()

        def play(self):
            while self.running:

                if self.game_over:
                    show_go_screen()
                    self.game_over = False

                    self.all_sprites = pygame.sprite.Group()
                    self.asteroids = pygame.sprite.Group()
                    self.bullets = pygame.sprite.Group()
                    self.powerups = pygame.sprite.Group()

                    player = Player(Game(True))
                    self.all_sprites.add(player)
                    for i in range(8):
                        self.all_sprites, self.asteroids = new_asteroid(self.all_sprites, self.asteroids)

                    self.score = 0

                    # keep loop running at the right speed
                clock.tick(FPS)
                # Process input (events)
                for event in pygame.event.get():
                    # check for closing window
                    if event.type == pygame.QUIT:
                        self.running = False

                # Update
                self.all_sprites.update()

                # check to see if a bullet hit the asteroid
                self.hits = pygame.sprite.groupcollide(self.asteroids, self.bullets, True, True)
                for hit in self.hits:
                    self.score += 50 - hit.radius
                    expl = Explosion(hit.rect.center, 'lg')
                    self.all_sprites.add(expl)
                    power_type = random.choice(['shield', 'gun'])
                    if random.random() > 0.4:  # chance for powerup dropped by asteroid
                        if power_type == 'shield':
                            self.pow = Powerup((RestoreShield((PowerupObject(hit.rect.center, power_type)), )), )
                        elif power_type == 'gun':
                            self.pow = Powerup((UpgradeBullet((PowerupObject(hit.rect.center, power_type)), )), )
                        self.all_sprites.add(self.pow)
                        self.powerups.add(self.pow)
                    self.all_sprites, self.asteroids = new_asteroid(self.all_sprites, self.asteroids)

                # check to see if an asteroid hit the player
                self.hits = pygame.sprite.spritecollide(player, self.asteroids, True, pygame.sprite.collide_circle)

                for hit in self.hits:
                    player.shield -= hit.radius * 2
                    expl = Explosion(hit.rect.center, 'sm')
                    self.all_sprites.add(expl)
                    self.all_sprites, self.asteroids = new_asteroid(self.all_sprites, self.asteroids)

                    if player.shield <= 0:
                        death_explosion = Explosion(player.rect.center, 'player')
                        self.all_sprites.add(death_explosion)
                        player.hide()
                        player.lives -= 1
                        player.shield = 100

                # sprawdź czy gracz zebrał bonus
                self.hits = pygame.sprite.spritecollide(player, self.powerups, True)
                for hit in self.hits:
                    if hit.type == 'shield':
                        player.shield += random.randrange(10, 30)
                        if player.shield >= 100:
                            player.shield = 100
                    if hit.type == 'gun':
                        player.powerup()

                # if player died and explosion has finished playing
                if player.lives == 0 and not death_explosion.alive():
                    self.game_over = True
                # Draw / render
                screen.fill(BLACK)
                screen.blit(background, background_rect)
                self.all_sprites.draw(screen)
                draw_text(screen, str(self.score), 18, WIDTH / 2, 10)
                draw_shield_bar(screen, 5, 5, player.shield)
                draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
                # *after* drawing everything, flip the display
                pygame.display.flip()

            pygame.quit()


if __name__ == '__main__':

    game1 = Game(True)
    game2 = Game(False)

    print(game1._Game__instance)
    print(game2._Game__instance)

    if game1._Game__instance == game2._Game__instance:
        print("Referencja identyczna")
    game1.play()
    exit()
