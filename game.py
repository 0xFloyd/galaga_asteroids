import pygame 
import random
from os import path

img_dir = path.join(path.dirname(__file__), "images")
snd_dir = path.join(path.dirname(__file__), "sound")
WIDTH = 800
HEIGHT = 600
FPS = 60 

# colors 

WHITE = (255, 255 ,255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

#initialize pygame and sound 
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaga Asteroids")
clock = pygame.time.Clock()


font_name = pygame.font.match_font('arial')


def draw_text(surface, text, font_size, x, y ):
    font = pygame.font.Font(font_name, font_size)
    text_surface = font.render(text, True, WHITE) #True is for anti-aliasing 
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)   # first the surface to render on, then what you're rendering 

def newMob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def draw_shield_bar(surface, x, y, pct):
    if pct < 0:
        pct = 0
    
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct/100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)   # 2 is the thickness 

# player class
class Player(pygame.sprite.Sprite):
    def __init__(self):

        # init sprite. must always do 
        pygame.sprite.Sprite.__init__(self)

        #scale image, make background transparent, and set position
        self.image = pygame.transform.scale(player_img, (50, 38))   # 50, 38 is just scaled from the original thats 99, by 75 or something
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        # draw circle for radius test 
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)

        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10 
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250  #milliseconds 
        self.last_shot = pygame.time.get_ticks()


    # update player position 
    def update(self):
        self.speedx = 0

        # this command gets every key thats pressed down 
        keystate = pygame.key.get_pressed()

        # handle left and right arrows being pressed 
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5  
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx 

        # prevent movement from going off screen 
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    # shoot bullet 
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            laser_sound.play()
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
      
# Mob class
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        # due to how rotations work, information is lost every rotation. so we need to make an original image, and then a copy for each time 
        self.image_original = random.choice(meteor_images)
        self.image_original.set_colorkey(BLACK)
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()

        # draw circle for radius test 
        self.radius = int(self.rect.width * .9 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)

        # init sprite in random spot at top of screen
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    # rotate asteroid 
    def rotate(self):
        now = pygame.time.get_ticks()
        
        # if more than 50 milliseconds  
        if now - self.last_update > 50:
            self.last_update = now
           
            # due to issues with rotation, have to make rectangle around image adjust in size and continue to use old center  
            self.rotation = (self.rotation + self.rotation_speed) % 360  # cant be greater than 360 degrees 
            new_image = pygame.transform.rotate(self.image_original, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center


    # update Mob position 
    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        # once sprite reaches bottom or side, send back to random spot in screen
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

# bullet class 
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = laser_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
    
    def update(self):
        self.rect.y += self.speedy
        
        # delete if rect moves off screen 
        if self.rect.bottom < 0:
            self.kill()

# Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_animation[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 10
    
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




# Load game graphics 
background = pygame.image.load(path.join(img_dir, "space.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "player.png"))
laser_img = pygame.image.load(path.join(img_dir, "laser.png"))

# load all meteors 
meteor_images = []
meteor_list = ["meteor1.png", "meteor2.png", "meteor3.png", "meteor4.png", "meteor5.png"]
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())

# load explosions into dictionary 
explosion_animation = {}
explosion_animation['lg'] = []
explosion_animation['sm'] = []
for i in range(9):
    filename = 'exp{}.png'.format(i+1)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_animation['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_animation['sm'].append(img_sm)



# load sound files 
laser_sound = pygame.mixer.Sound(path.join(snd_dir, 'laser_sound.wav'))
explosion_sound = pygame.mixer.Sound(path.join(snd_dir, 'explosion.WAV'))
pygame.mixer.music.load(path.join(snd_dir, 'soundtrack.ogg'))
pygame.mixer.music.set_volume(0.4)

# create sprite groups and player sprite 
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# spawn X number of mobs and add to both sprite groups
for i in range(8):
    newMob()



score = 0

pygame.mixer.music.play(loops=-1)
# game loop
running = True 
while running: 
    # keep loop running at the right speed 
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get(): 
        # check for closing window 
        if event.type == pygame.QUIT:
            running = False

      


    # Update 
    all_sprites.update()

    # check to see if bullet hit a mob. if either is hit, both are deleted (hence TRUE TRUE )
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    # for each destroy, spawn new mob
    for hit in hits: 
        explosion_sound.play()
        score += 50 - hit.radius
        explosion = Explosion(hit.rect.center, 'lg')
        all_sprites.add(explosion)
        newMob()

    # check if mob hit player. True = should sprite be deleted on hit
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        explosion = Explosion(hit.rect.center, 'sm')
        all_sprites.add(explosion)
        newMob()
        if player.shield < 0:
            running = False


    # Draw / render sprites to screen
    screen.fill(BLACK)

    # add background. blit is a computer graphics term for copying pixels onto screen 
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield) # x coordninate, y coordinate, percentage
    # after drawing everything, flip display to hide it 
    pygame.display.flip()

pygame.quit()