import pygame
import sys
import random
import time
import math
import os
import pygame.mixer

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(os.path.join("music", "1.mp3"))

width, height = 1200, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bonk Bros v1.7.0 Beta")

red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
background_color = (255, 255, 255)
health_bar_background = (255, 0, 0)
text_color = (0, 0, 0)

good = True
Good2 = False

powerup_images = {}
if good:
    powerup_images = {
            "health": pygame.image.load(os.path.join("drawn", "medkit.png")),
            "speed": pygame.image.load(os.path.join("drawn", "superspeed.png")),
            "damage": pygame.image.load(os.path.join("drawn", "moreDamage.png")),
            "fireRate": pygame.image.load(os.path.join("drawn", "fireRate.png")),
            "bullets": pygame.image.load(os.path.join("drawn", "extrabullets.png")),
            "lowGravity": pygame.image.load(os.path.join("drawn", "lowGravity.png")),
            "fastBullets": pygame.image.load(os.path.join("professional", "fastBullets.png")),
            "oneShot": pygame.image.load(os.path.join("drawn", "oneShot.png")),
            "freezePlayer": pygame.image.load(os.path.join("drawn", "freezePlayer.png")),
            "fastRegen" : pygame.image.load(os.path.join("professional", "fastRegen.png")),
            "sniper": pygame.image.load(os.path.join("professional", "sniper.png")),
            "flamethrower": pygame.image.load(os.path.join("professional", "flamethrower.png")),
    }
else:
    powerup_images = {
            "health": pygame.image.load(os.path.join("professional", "medkit.png")),
            "speed": pygame.image.load(os.path.join("professional", "superspeed.png")),
            "damage": pygame.image.load(os.path.join("professional", "moreDamage.png")),
            "fireRate": pygame.image.load(os.path.join("professional", "fireRate.png")),
            "bullets": pygame.image.load(os.path.join("professional", "extrabullets.png")),
            "lowGravity": pygame.image.load(os.path.join("professional", "lowGravity.png")),
            "fastBullets": pygame.image.load(os.path.join("professional", "fastBullets.png")),
            "oneShot": pygame.image.load(os.path.join("professional", "oneShot.png")),
            "freezePlayer": pygame.image.load(os.path.join("professional", "freezePlayer.png")),
            "fastRegen": pygame.image.load(os.path.join("professional", "fastRegen.png")),
            "sniper": pygame.image.load(os.path.join("professional", "sniper.png")),
            "flamethrower": pygame.image.load(os.path.join("professional", "flamethrower.png")),
    }
class Powerup:
    def __init__(self, x, y, powerup_type):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.powerup_type = powerup_type

powerups = []

def generate_powerup(platformsList, specific):
    platformVar = random.choice(platformsList)
    x = random.randint(platformVar.rect.x, platformVar.rect.x + platformVar.rect.width - 20)
    y = platformVar.rect.y - 40
    powerup_type = "health"
    if specific == "None":
        powerup_type = random.choice(["health", "speed", "damage", "fireRate", "bullets", "lowGravity", "fastBullets", "oneShot", "freezePlayer", "fastRegen", "sniper", "flamethrower"])
        # "health", "speed", "damage", "fireRate", "bullets", "lowGravity", "fastBullets", "oneShot", "freezePlayer", "fastRegen", "sniper", "flamethrower"
    else:
        powerup_type = specific

    powerups.append(Powerup(x, y, powerup_type))

red_projectile_color = (255, 0, 0)
blue_projectile_color = (0, 0, 255)

class Projectile:
    def __init__(self, x, y, color, velocity_x, velocity_y, damage):
        self.rect = pygame.Rect(x, y, 10, 5)
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.damage = damage
        self.creation_time = time.time()  # Record the creation time

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

player1_projectiles = []
player2_projectiles = []


sniperProjectileDamage = 40
sniperFireRate = 50
sniperBullets = 1
sniperBulletSpeed = 30
sniperOneShot = False
ftProjectileDamage = 1
ftFireRate = 10
ftBullets = 13
ftBulletSpeed = 5
ftOneShot = False

class Player:
    def __init__(self, color, x, y):
        self.rect = pygame.Rect(x, y, 30, 60)
        self.color = color
        self.velocity_x = 0
        self.velocity_y = 0
        self.jump_height = -15
        self.gravity = 1
        self.on_ground = False
        self.health = 100.0
        self.knockback_distance = 10
        self.last_hit_time = 0
        self.kills = 0
        self.last_direction = 1
        self.ranged_attack_cooldown = 0
        self.projectiles = []
        self.speedModifier = 1
        self.projectileDamage = 10
        self.fireRate = 25
        self.bullets = 3
        self.text_cooldown = 0
        self.bulletSpeed = 10
        self.previousBullets = self.bullets
        self.oneShot = False
        self.freezeDuration = 0
        self.healthSpeed = 0.05
        self.current_weapon = "Ranged Attack"
        self.powerupWeapon = "None" # None, Sniper, Flamethrower

    def check_collision_with_projectile(self, projectile):
        return self.rect.colliderect(projectile.rect)

    def move(self, left_key, right_key, jump_key):
        key = pygame.key.get_pressed()
        if key[left_key]:
            self.velocity_x = -5 * self.speedModifier
            self.last_direction = -1
        elif key[right_key]:
            self.velocity_x = 5 * self.speedModifier
            self.last_direction = 1
        else:
            self.velocity_x = 0

        if key[jump_key]:
            self.jump()

    def jump(self):
        if self.on_ground:
            self.velocity_y = self.jump_height
            self.on_ground = False

    def respawn(self, other_player_x, occupied_positions):
        new_x = 300
        if other_player_x - self.rect.width > 0:
            new_x = random.randint(0, other_player_x - self.rect.width) if self.color == red else random.randint(
                other_player_x + 50, width - self.rect.width)
        new_y = height - self.rect.height
        while (new_x, new_y) in occupied_positions:
            if other_player_x - self.rect.width > 0:
                new_x = random.randint(0, other_player_x - self.rect.width) if self.color == red else random.randint(
                    other_player_x + 50, width - self.rect.width)
        self.rect.x = new_x
        self.rect.y = new_y
        self.health = 100.0
        self.last_hit_time = time.time()
        self.fireRate = 25
        self.speedModifier = 1
        self.projectileDamage = 10
        self.bullets = 3
        self.gravity = 1
        self.oneShot = False
        self.bulletSpeed = 10
        self.healthSpeed = 0.05

    def take_damage(self, damage, respawn_function, arg, arg2):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            respawn_function(arg.rect.x, arg2)
            arg.kills += 1

    def regen_health(self):
        if time.time() - self.last_hit_time > 1 and self.health < 100:
            self.health = round(min(100.00, self.health + self.healthSpeed), 2)

    def ranged_attack(self):
        a, b, c, d, e = 0, 0, 0, 0, False

        if self.current_weapon == "Ranged Attack":
            a = self.projectileDamage
            b = self.fireRate
            c = self.bullets
            d = self.bulletSpeed
            e = self.oneShot
        elif self.current_weapon == "Secondary":
            if self.powerupWeapon == "Sniper":
                a = sniperProjectileDamage
                b = sniperFireRate
                c = sniperBullets
                d = sniperBulletSpeed
                e = sniperOneShot
            if self.powerupWeapon == "Flamethrower":
                a = ftProjectileDamage
                b = ftFireRate
                c = ftBullets
                d = ftBulletSpeed
                e = ftOneShot

        if self.freezeDuration > 0:
            return

        if self.ranged_attack_cooldown <= 0:

            angle_step = 0.1
            half_step = angle_step / 2
            start_angle = -half_step * (c - 1)
            angles = [start_angle + i * angle_step for i in range(c)]

            if e:
                initial_velocity_x = d * self.last_direction * math.cos(0)
                initial_velocity_y = d * math.sin(0)
                self.previousBullets = c
                self.bullets = 1
                self.oneShot = False
                self.projectiles.append(Projectile(self.rect.x, self.rect.centery, self.color,
                                                   initial_velocity_x, initial_velocity_y, 1000000))
                self.bullets = self.previousBullets
                return

            for angle in angles:
                initial_velocity_x = d * self.last_direction * math.cos(angle)
                initial_velocity_y = d * math.sin(angle)
                bullety = self.rect.centery
                if self.powerupWeapon == "Flamethrower" and self.current_weapon == "Secondary":
                    bullety = random.randint(self.rect.y, self.rect.y + 60)
                    initial_velocity_y = 0
                self.projectiles.append(Projectile(self.rect.x, bullety, self.color,
                                                   initial_velocity_x, initial_velocity_y, a))

            self.ranged_attack_cooldown = b

    def toggle_weapon(self):
        if self.current_weapon == "Ranged Attack":
            self.current_weapon = "Secondary"
        else:
            self.current_weapon = "Ranged Attack"

    def update(self, platformsToUpdate):
        if self.freezeDuration > 0:
            self.freezeDuration -= 1
            return

        if not self.on_ground:
            self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        self.rect.x += self.velocity_x

        self.on_ground = False
        for PLATFORM in platformsToUpdate:
            if self.rect.colliderect(PLATFORM.rect):
                self.rect.y = PLATFORM.rect.y - self.rect.height + 1
                self.on_ground = True
                self.velocity_y = 0
                break

        if self.rect.x < -self.rect.width:
            self.rect.x = width - 1
        elif self.rect.x > width:
            self.rect.x = -self.rect.width + 1

        if self.ranged_attack_cooldown > 0:
            self.ranged_attack_cooldown -= 1

        if self.rect.y > height:
            if width - self.rect.width > 0:
                self.respawn(random.randint(0, width - self.rect.x), occupied_respawn_positions)
            else:
                self.respawn(300, occupied_respawn_positions)
            other_player = player2 if self.color == red else player1
            other_player.kills += 1

kos_font = pygame.font.Font(None, 24)

def render_health_and_ko(drawOnPlayer, health_bar_color):
    pygame.draw.rect(screen, health_bar_background,
                     (drawOnPlayer.rect.x, drawOnPlayer.rect.y - 10, drawOnPlayer.rect.width, 5))
    pygame.draw.rect(screen, health_bar_color, (
        drawOnPlayer.rect.x, drawOnPlayer.rect.y - 10,
        drawOnPlayer.rect.width * min((drawOnPlayer.health / 100), 1.00), 5))

    font = pygame.font.Font(None, 24)
    health_text = font.render(f"{int(drawOnPlayer.health)}%", True, text_color)
    screen.blit(health_text,
                (drawOnPlayer.rect.x + drawOnPlayer.rect.width // 2 - health_text.get_width() // 2,
                 drawOnPlayer.rect.y - 30))

    kos_text = kos_font.render(f"KOs: {drawOnPlayer.kills}", True, text_color)
    screen.blit(kos_text,
                (drawOnPlayer.rect.x + drawOnPlayer.rect.width // 2 - kos_text.get_width() // 2,
                 drawOnPlayer.rect.y - 50))

debug_font = pygame.font.Font(None, 24)

def render_debug_menu(drawOnPlayer, player_id, debug_text_y):
    debug_text = debug_font.render(
        f"Player {player_id} - Position: ({drawOnPlayer.rect.x}, {drawOnPlayer.rect.y})  "
        f"Velocity: ({drawOnPlayer.velocity_x}, {drawOnPlayer.velocity_y})  On Ground: {drawOnPlayer.on_ground}  "
        f"Health: {round(drawOnPlayer.health)}  Kills: {drawOnPlayer.kills}  "
        f"Performance Stats: FPS: {int(clock.get_fps())}  "
        f"Player Projectiles: {len(drawOnPlayer.projectiles)}",
        True, text_color)
    screen.blit(debug_text, (10, debug_text_y))

class Platform:
    def __init__(self, x, y, platformWidth, platformHeight):
        self.rect = pygame.Rect(x, y, platformWidth, platformHeight)

class MovingPlatform(Platform):
    def __init__(self, x, y, platformWidth, platformHeight, speed, xboundary1, xboundary2):
        super().__init__(x, y, platformWidth, platformHeight)
        self.speed = speed
        self.direction = 1
        self.xboundary1 = xboundary1
        self.xboundary2 = xboundary2

    def move(self):
        self.rect.x += self.speed * 2 * self.direction

        if self.rect.right > self.xboundary1 or self.rect.left < self.xboundary2:
            self.direction *= -1

def generate_random_platforms():
    platform1 = [
        Platform(0, 600 - 20, 1200, 20),
        Platform(200, 600 - 150, 200, 10),
        Platform(1200 - 400, 600 - 150, 200, 10),
    ]

    platform2 = [
        Platform(0, height - 20, width, 20),
        Platform(0, height - 100, 200, 10),
        Platform(250, height - 200, 200, 10),
        Platform(500, height - 100, 200, 10),
        Platform(750, height - 200, 200, 10),
        Platform(1000, height - 100, 200, 10),

        Platform(0, height - 300, 200, 10),
        Platform(250, height - 400, 200, 10),
        Platform(500, height - 300, 200, 10),
        Platform(750, height - 400, 200, 10),
        Platform(1000, height - 300, 200, 10),
    ]

    platform3 = [
        Platform(0, height - 20, width, 20),
        Platform(100, height - 100, 200, 10),
        Platform(width - 300, height - 100, 200, 10),
        Platform(150, height - 200, 150, 10),
        Platform(width - 300, height - 200, 150, 10),
        Platform(200, height - 300, 100, 10),
        Platform(width - 300, height - 300, 100, 10),
        Platform(350, height - 375, 500, 10),
        Platform(500, height - 300, 50, 10),  # Added a small vertical platform
        Platform(800, height - 200, 100, 10),  # Added a horizontal platform
        Platform(700, height - 350, 150, 10),  # Added another horizontal platform
    ]

    platform4 = [
        Platform(50, height - 20, 100, 20),
        Platform(200, height - 40, 50, 20), # Small 1
        Platform(290, height - 100, 70, 150), # Large 1
        Platform(412, height - 40, 100, 20), # Small 2
        Platform(565, height - 150, 70, 150), # Large 2
        Platform(662, height - 40, 100, 20), # Small 3
        Platform(795, height - 120, 70, 120), # Large 3
        Platform(900, height - 40, 100, 20), # Small 4
        Platform(1040, height - 80, 70, 80), # Large 4
        MovingPlatform(width / 2 - 150, height - 250, 150, 10, 2,width / 2, 0),
        MovingPlatform(width / 2, height - 250, 150, 10, 2, width, width / 2),
        Platform(100, height - 350, 150, 10),
        Platform(950, height - 350, 150, 10),
        Platform(100, height - 450, 450, 10),
        Platform(650, height - 450, 450, 10),
    ]

    platform5 = [
        Platform(0, height - 20, width, 20),
        MovingPlatform(0, height - 150, 500, 10, 3, width, 0),
        MovingPlatform(50, height - 250, 400, 10, 3, width - 50, 50),
        MovingPlatform(100, height - 350, 300, 10, 3, width - 100, 100),
        MovingPlatform(150, height - 450, 200, 10, 3, width - 150, 150),
        MovingPlatform(200, height - 550, 100, 10, 3, width - 200, 200),
        Platform(250, height - 250, 150, 10),
        Platform(525, height - 350, 150, 10),
        Platform(800, height - 250, 150, 10),
        Platform(0, height - 150, 150, 10),
        Platform(width - 150, height - 150, 150, 10),
    ]

    platformsTable = [platform2]

    if not good:
        platformsTable = [platform1, platform2, platform3, platform4, platform5]

    choice = random.choice(platformsTable)
    return choice

platforms = generate_random_platforms()

player1 = Player(red, 50, height - 200)
player2 = Player(blue, width - 150, height - 200)

occupied_respawn_positions = set()

show_debug_menu = False

musicPlaying = False

clock = pygame.time.Clock()
powerup_timer = 0

while True:
    for platform in platforms:
        if isinstance(platform, MovingPlatform):
            platform.move()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F2:
                show_debug_menu = not show_debug_menu
            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_q:
                player1.ranged_attack()
            elif event.key == pygame.K_RSHIFT or event.key == pygame.K_PAGEUP:
                player2.ranged_attack()
            elif event.key == pygame.K_m:
                if musicPlaying:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.play(-1)
                musicPlaying = not musicPlaying
            elif event.key == pygame.K_e:
                player1.toggle_weapon()
            elif event.key == pygame.K_PAGEDOWN:
                player2.toggle_weapon()
            elif event.key == pygame.K_PERIOD or event.key == pygame.K_1:
                generate_powerup(platforms, "None")
            elif event.key == pygame.K_c:
                Good2 = not Good2
            elif event.key == pygame.K_RCTRL and Good2:
                player2.bullets += 2
                player2.previousBullets = player1.bullets
                player2.oneShot = True
            elif event.key == pygame.K_RALT and Good2:
                player2.bullets += 10
                player2.projectileDamage += 25
                player2.health += 100
                player2.bulletSpeed = 20
                player2.fireRate = 1
                player2.kills += 2
            elif event.key == pygame.K_2 and Good2:
                player1.bullets += 2
                player1.previousBullets = player1.bullets
                player1.oneShot = True
            elif event.key == pygame.K_3 and Good2:
                player1.bullets += 10
                player1.projectileDamage += 25
                player1.health += 100
                player1.bulletSpeed = 20
                player1.fireRate = 1
                player1.kills += 2

    player1.move(pygame.K_a, pygame.K_d, pygame.K_w)

    player2.move(pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)

    player1.update(platforms)
    player2.update(platforms)

    if powerup_timer == 0:
        generate_powerup(platforms, "None")
        powerup_timer = 300 # 60 FPS * 5 Seconds

    if powerup_timer > 0:
        powerup_timer -= 1

    for player in [player1, player2]:
        for projectile in player.projectiles:
            projectile.update()
            # Check if the projectile has been alive for more than 10 seconds
            if time.time() - projectile.creation_time > 5:
                player.projectiles.remove(projectile)

            # Check for collision with platforms
            if any(pf.rect.colliderect(projectile.rect) for pf in platforms):
                player.projectiles.remove(projectile)

            # Check for collision with players
            for other_player in [player1, player2]:
                if other_player != player and other_player.check_collision_with_projectile(projectile):
                    other_player.take_damage(projectile.damage, other_player.respawn, player,
                                             occupied_respawn_positions)
                    player.projectiles.remove(projectile)


        for powerup in powerups:
            if player.rect.colliderect(powerup.rect):

                powerups.remove(powerup)

                if powerup.powerup_type == "health":
                    if player.health < 75 and player.health >= 50:
                        player.health = 100
                    elif player.health >= 75:
                        player.health += 25
                    else:
                        player.health += 50
                elif powerup.powerup_type == "speed":
                    player.speedModifier += 0.1
                elif powerup.powerup_type == "damage":
                    player.projectileDamage += 5
                elif powerup.powerup_type == "fireRate":
                    player.fireRate -= 5
                elif powerup.powerup_type == "bullets":
                    player.bullets += 2
                elif powerup.powerup_type == "lowGravity":
                    player.gravity *= 0.9
                elif powerup.powerup_type == "fastBullets":
                    player.bulletSpeed += 2
                elif powerup.powerup_type == "oneShot":
                    player.oneShot = True
                elif powerup.powerup_type == "freezePlayer":
                    other_player = player2 if player == player1 else player1
                    other_player.freezeDuration = 120
                elif powerup.powerup_type == "fastRegen":
                    player.healthSpeed += 0.01
                elif powerup.powerup_type == "sniper":
                    player.powerupWeapon = "Sniper"
                elif powerup.powerup_type == "flamethrower":
                    player.powerupWeapon = "Flamethrower"

    if player1.rect.colliderect(player2.rect):

        if player1.rect.centerx < player2.rect.centerx:
            overlap = player1.rect.right - player2.rect.left
            player1.rect.x -= overlap // 2
            player2.rect.x += overlap // 2
        else:
            overlap = player2.rect.right - player1.rect.left
            player1.rect.x += overlap // 2
            player2.rect.x -= overlap // 2

        keys = pygame.key.get_pressed()

        if keys[pygame.K_s]:
            if player1.freezeDuration == 0:
                player2.health = max(0.00, player2.health - 3)

        if keys[pygame.K_DOWN]:
            if player2.freezeDuration == 0:
                player1.health = max(0.00, player1.health - 3)

        if player2.health <= 0:
            player1.kills += 1
            player2.respawn(player2.rect.x, occupied_respawn_positions)

        if player1.health <= 0:
            player2.kills += 1
            player1.respawn(player1.rect.x, occupied_respawn_positions)

    for player in [player1, player2]:
        for projectile in player.projectiles:
            projectile.update()

    player1.projectiles = [projectile for projectile in player1.projectiles if
                           not any(pf.rect.colliderect(projectile.rect) for pf in platforms)]

    collided_projectiles = [projectile for projectile in player1.projectiles if
                            player2.rect.colliderect(projectile.rect)]
    for projectile in collided_projectiles:
        player2.take_damage(projectile.damage, player2.respawn, player1, occupied_respawn_positions)

    player1.projectiles = [projectile for projectile in player1.projectiles if projectile not in collided_projectiles]

    player2.projectiles = [projectile for projectile in player2.projectiles if
                           not any(pf.rect.colliderect(projectile.rect) for pf in platforms)]

    collided_projectiles = [projectile for projectile in player2.projectiles if
                            player1.rect.colliderect(projectile.rect)]
    for projectile in collided_projectiles:
        player1.take_damage(projectile.damage, player1.respawn, player2, occupied_respawn_positions)

    player2.projectiles = [projectile for projectile in player2.projectiles if projectile not in collided_projectiles]

    player1.projectiles = [projectile for projectile in player1.projectiles if 0 < projectile.rect.x < width]
    player2.projectiles = [projectile for projectile in player2.projectiles if 0 < projectile.rect.x < width]

    player1.regen_health()
    player2.regen_health()

    screen.fill(background_color)

    for platform in platforms:
        pygame.draw.rect(screen, green, platform.rect)

    pygame.draw.rect(screen, player1.color, player1.rect)
    pygame.draw.rect(screen, player2.color, player2.rect)

    render_health_and_ko(player1, green)
    render_health_and_ko(player2, green)

    if show_debug_menu:
        debug_font = pygame.font.Font(None, 24)

        render_debug_menu(player1, 1, 10)

        render_debug_menu(player2, 2, 40)

    weapon_text_player1 = kos_font.render(player1.current_weapon, True, text_color)
    screen.blit(weapon_text_player1, (10, height - 20))

    weapon_text_player2 = kos_font.render(player2.current_weapon, True, text_color)
    screen.blit(weapon_text_player2, (width - kos_font.size(player2.current_weapon)[0] - 10, height - 20))

    for player in [player1, player2]:
        for projectile in player.projectiles:
            pygame.draw.rect(screen, projectile.color, projectile.rect)

    for powerup in powerups:
        screen.blit(powerup_images[powerup.powerup_type], (powerup.rect.x, powerup.rect.y))

    pygame.display.flip()

    clock.tick(60)
