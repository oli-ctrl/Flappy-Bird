import pygame
import time
import random
import pathlib

## path to assets folder
path = pathlib.Path(__file__).parent.absolute()
path = str(F"{path}/assets/").replace("\\", "/")

# pygame setup
pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Arial', 30)
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()


## particle controller
class particles():
    def __init__(self):
        self.allparticles = []
        self.particlecount = 0

    ## draws all particles
    def draw(self):
        for i in self.allparticles:
            i.draw()
    ## removes a particle from the list if it is dead
    def remove(self, particle):
        if particle.die():
            self.allparticles.remove(particle)
    ## cleares all particles from the screen
    def removeall(self):
        self.allparticles = []
    ## adds a particle to the list to iterate over and draw
    def add(self, particle):
        self.allparticles.append(particle)
    ## updates all particles
    def update(self):
        for i in self.allparticles:
            i.update()
    
## particle class 
class particle():
    ## generates a particle with the given parameters
    def __init__(self, x, y, size = 5, color = "Red", vertvelocity = 5, horisontalvelocity = random.randint(-5,5), gravity = 0.5, lifetime = 60, bounce = 0, effectedbymovement = False, decayrate= 0.1):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.vertvelocity = vertvelocity
        self.horisontalvelocity = horisontalvelocity
        self.gravity = gravity
        self.lifetime = lifetime
        self.bounce = bounce
        self.lifetimer = 0
        self.bouncecooldown = 0
        self.effectedbymovement = effectedbymovement
        self.decayrate = decayrate
        self.wallbounce = False

    def update(self):
        ## update velocity, position and bounce cooldown
        self.vertvelocity += self.gravity
        self.y += self.vertvelocity
        self.x += self.horisontalvelocity
        self.bouncecooldown -= 1
        
        ## decay particle
        self.lifetimer += 1
        if self.lifetimer > self.lifetime:
            game.particlecontroller.remove(self)

        ## ground collisions
        if self.y > 680 - self.size and self.bouncecooldown <= 0 and self.vertvelocity > 0.1 and self.bounce != 0:
            self.vertvelocity = -self.vertvelocity*self.bounce
            self.bouncecooldown = 1
            self.horisontalvelocity /= 2
            self.y = 680 - self.size

        ## wall/pipe collisions
        if self.wallbounce == True and self.bouncecooldown <= 0:
            for i in game.pipecontroller.pipes:
                
                ## check collsion with top of pipe
                collider = pygame.Rect(self.x-self.size, self.y-self.size, self.size, self.size)
                if collider.colliderect(pygame.Rect(i.x, i.y, i.width, i.height/2)) or collider.colliderect(pygame.Rect(i.x, i.y - (i.height + i.gap), i.width, i.height/2)):
                    self.vertvelocity = -self.vertvelocity*self.bounce
                    self.bouncecooldown = 1
                    self.horisontalvelocity /= 2
                    break

                ## check collsion with left side of pipe
                if collider.colliderect(pygame.Rect(i.x-i.width/2, i.y, i.width/2, i.height)) or collider.colliderect(pygame.Rect(i.x-i.width/2, i.y - (i.height + i.gap), i.width/2, i.height)):
                    self.horisontalvelocity= -abs(self.horisontalvelocity*self.bounce)
                    self.bouncecooldown = 1
                    break

                ## check collsion with right side of pipe
                if collider.colliderect(pygame.Rect(i.x+i.width/2, i.y, i.width/2, i.height)) or collider.colliderect(pygame.Rect(i.x+i.width/2, i.y - (i.height + i.gap), i.width/2, i.height)):
                    self.horisontalvelocity = abs(self.horisontalvelocity*self.bounce)
                    self.bouncecooldown = 1
                    break
                ## check collsion with bottom of pipe
                if collider.colliderect(pygame.Rect(i.x, i.y + i.height/2, i.width, i.height/2)) or collider.colliderect(pygame.Rect(i.x, i.y - (i.height + i.gap) + i.height/2, i.width, i.height/2)): 
                    self.vertvelocity = -abs(self.vertvelocity*self.bounce)
                    self.bouncecooldown = 1
                    break
        
        ## moves particle with bird
        if self.effectedbymovement == True and game.bird.alive == True:
            self.x -= 3
        
    ## draws the particle
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

    ## returns true if particle is dead and should be removed, otherwise slowly shrinks the particle
    def die(self):
        self.size -= self.decayrate
        if self.size < 0.1:
            self.size = 0
            return True

## bird class 
class Bird():
    def __init__(self):
        self.size = 30
        self.velocity = -10
        self.gravity = 0.5
        self.direction = 0
        self.picture = pygame.image.load(str(path) + "bird.png")
        self.picture = pygame.transform.scale(self.picture, (self.size*2, self.size*2))
        self.deadpicture = pygame.image.load(str(path) + "Deadbird.png")
        self.deadpicture = pygame.transform.scale(self.deadpicture, (self.size*2.5, self.size*2.5))
        self.reset()

    ## resets the bird
    def reset(self):
        self.direction = 0
        self.x = 360
        self.y = 360
        self.score = 0
        self.alive = True

    ## draws the bird
    def draw(self):
        if self.alive == True or self.alive == "dying":
            orig_rect = self.picture.get_rect()
            rot_image = pygame.transform.rotate(self.picture, -self.direction)
        else:
            orig_rect = self.deadpicture.get_rect()
            rot_image = pygame.transform.rotate(self.deadpicture, -self.direction)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        if self.alive == True:
            screen.blit(rot_image, (self.x-self.size, self.y-self.size))
        else:
            screen.blit(rot_image, (self.x-self.size+10, self.y-self.size-18))
        if game.debug:
            pygame.draw.circle(screen, "yellow", (self.x, self.y), self.size)
    
    ## makes the bird fall down when called
    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.direction = self.velocity*8
        if self.direction > 80:
            self.direction = 80
        if self.direction < -90:
            self.direction = -90   
        if not self.alive: 
            self.direction = 80
        
    # makes the bird jump when called also some particle effects
    def jump(self):
        self.velocity = -10
        for i in range (20,50):
            i = random.randint(200,255)
            game.particlecontroller.add(particle(self.x, self.y, random.randint(10,20), (i,i,i), random.randint(-50,50)/10, random.randint(-50,50)/10, 0.5, 1, 0.5, True, 1))
            game.particlecontroller.allparticles[-1].wallbounce = True

    ## checks if the bird hits a pipe, or the ground
    def checkhit(self):
        if self.y > 700: 
            return True
        if self.y < -50:
            self.y += 25
        for i in game.pipecontroller.pipes:
            if pygame.Rect(self.x-self.size, self.y-self.size, self.size, self.size).colliderect(pygame.Rect(i.x, i.y, i.width/2, i.height)) or pygame.Rect(self.x-self.size, self.y-self.size, self.size, self.size).colliderect(pygame.Rect(i.x, i.y - (i.height + i.gap), i.width/2, i.height)):
                return True
        return False
    
    ## death animation
    def die(self):
        self.alive = "dying"
        count = -5
        self.velocity = 0
        game.drawscore(self.score, 640, 185, 2)
        for i in range (0,25):
            game.particlecontroller.add(particle(self.x, self.y, random.randint(3,7), "red", random.randint(-20,20)/10, random.randint(-20,20)/10, 0.5, 40, 0.5, True, 0.6))
        while self.y <= 680:
            game.particlecontroller.add(particle(self.x, self.y, random.randint(3,7), "red", random.randint(-10,10)/10, random.randint(-10,10)/10, 0.5, 20, 0.5, True, 0.6))
            self.direction = 100
            screen.fill((0,0,0))
            game.draw()
            game.updateall()
            
            self.x -= 5
            pygame.display.flip()
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.running = False
                    return True
        self.y = 680
        for i in range (0, 100):
            game.particlecontroller.add(particle(self.x, self.y, random.randint(3,7), "Brown", random.randint(-50, 50)/10, random.randint(-100,100)/10, 0.5, 120, 0.2))
            game.particlecontroller.add(particle(self.x, self.y, random.randint(4,6), "yellow", random.randint(-50, 50)/10, random.randint(-100,100)/10, 0.5, 100, 0.2))
        self.alive = False
        while True:
            self.direction = 80
            game.particlecontroller.add(particle(self.x, self.y, random.randint(3,7), "red", random.randint(-10,10)/10, random.randint(-10,10)/10, 0.5, 20, 0.5, True, 0.6))
            if count % 5 == 0:
                game.particlecontroller.add(particle(self.x, self.y, random.randint(3,7), "red", -10, random.randint(-10,10)/10, 0.5, random.randint(20,40), 0.5, True, 0.6))
            screen.fill((0,0,0))
            game.updateall()
            game.draw()
            pygame.display.flip()
            clock.tick(60)
            count += 1
            if count >= 100:
                game.fade.fadeout()
                return True
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.running = False
                    return True

## pipe controller class
class Pipes():
    def __init__(self):
        self.pipes = []
    def draw(self):
        for i in self.pipes:
            i.draw()
    def add(self, pipe):
        self.pipes.append(pipe)
    def reset(self):
        self.pipes = []
    def update(self):
        for i in self.pipes:
            i.update()
    def check(self):
        for i in self.pipes:
            i.check()

## pipe class
class Pipe ():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 500
        self.gap = 200
        self.givenpoint = False
        self.bottompipe = pygame.image.load(str(path) + "Pipe.png")
        self.bottompipe = pygame.transform.scale(self.bottompipe, (self.width*1.5, self.height))
        self.toppipe = pygame.image.load(str(path) + "Pipe.png")
        self.toppipe = pygame.transform.scale(self.toppipe, (self.width*1.5, self.height))
        self.toppipe = pygame.transform.flip(self.toppipe, False, True)

    ## draw the pipe
    def draw(self):
        screen.blit(self.bottompipe, (self.x-15, self.y))
        screen.blit(self.toppipe, (self.x-15, self.y - (self.height + self.gap)))
        if game.debug:
            pygame.draw.rect(screen, "green", (self.x , self.y, self.width, self.height))
            pygame.draw.rect(screen, "green", (self.x , self.y - (self.height + self.gap), self.width, self.height))

    ## move the pipe
    def update(self):
        self.x -= 3
    
    ## check if the pipe is off the screen or the bird has passed
    def check(self):
        if self.x <= game.bird.x and not self.givenpoint and game.bird.alive and game.gamestate == "Playing":
            game.bird.score += 1
            self.givenpoint = True
        if self.x < -100:
            game.pipecontroller.pipes.remove(self)

## main menu controller class
class mainmenu():
    def __init__(self):
        self.allbuttons = []
        self.alltexts = []
        self.other = []
    def draw(self):
        for i in self.other:
            i.render()
        for i in self.allbuttons:
            i.draw()
            i.check()
        for i in self.alltexts:
            i.render()

    def construct(self):
        self.allbuttons.append(playButton())
        self.other.append(Image(390, 15, 500, 700,"MenuBackground.png"))
        
## image class for easy rendering of static images
class Image():
    def __init__(self, x, y, height, width, image):
        self.x = x
        self.y = y
        self.image = pygame.image.load(str(path) + image)
        self.image = pygame.transform.scale(self.image, (height, width))
        self.imagewidth = self.image.get_width()
        self.imageheight = self
    def render(self):
        screen.blit(self.image, (self.x, self.y))

## play button class
class playButton():
    def __init__(self):
        self.x = 565
        self.y = 500
        self.imagewidth = 75
        self.imageheight = 50
        self.width = 150
        self.height = 100
        self.Image = pygame.image.load(str(path) + "PlayButton.png")
        self.Image = pygame.transform.scale(self.Image,(self.imagewidth*2, self.imageheight*2))
        self.HoverImage = pygame.image.load(str(path) + "PlayButton_Hover.png")
        self.HoverImage = pygame.transform.scale(self.HoverImage,(self.imagewidth*2, self.imageheight*2))
        self.clicked = False
        self.hover = False
    def draw(self):
        if self.hover:
            screen.blit(self.HoverImage, (self.x, self.y))
        else:
            screen.blit(self.Image, (self.x, self.y))
        if game.debug:
            pygame.draw.rect(screen, "red", (self.x, self.y, self.width, self.height))
    def check(self):
        if pygame.mouse.get_pos()[0] > self.x and pygame.mouse.get_pos()[0] < self.x + self.width and pygame.mouse.get_pos()[1] > self.y and pygame.mouse.get_pos()[1] < self.y + self.height:
            self.hover = True
            if pygame.mouse.get_pressed()[0]:
                self.onclick()
        else:
            self.hover = False
    def onclick(self):
        self.clicked = True

## cloud controller class  
class clouds():
    def __init__(self):
        self.allclouds = []
    def add(self, cloud):
        self.allclouds.append(cloud)
    def draw(self):
        for i in self.allclouds:
            i.draw()
    def move(self, amount = 3):
        for i in self.allclouds:
            i.move(amount)
    def check(self):
        for i in self.allclouds:
            i.check()

## cloud class
class cloud():
    def __init__(self, x = 1400):
        self.x = x
        self.y = random.randint(0, 300)
        self.size = random.randint(20, 50)
        self.depth = random.randint(1, 5)
        color = 200+ self.depth*5 + random.randint(-10, 10)
        self.color = pygame.Color(color, color, color)
        self.secondcloudpos = []
        self.speed = random.randint(10, 20)
        for i in range(random.randint(5,10)):
            randlim= round(self.size*self.depth/4)
            self.secondcloudpos.append((random.randint(-randlim, randlim), random.randint(-randlim, randlim)))
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size*self.depth/4)
        for i in self.secondcloudpos:
            pygame.draw.circle(screen, self.color, (self.x + i[0], self.y + i[1]), self.size*self.depth/4)

    def move(self, amount = 3):
        self.x -= amount*self.depth/self.speed

    def check(self):
        if self.x < -100:
            game.cloudcontroller.allclouds.remove(self)
        
## class for fading the screen in and out
class fades():  
    def __init__(self):
        self.fade = pygame.Surface((1400, 800))
        self.fade.fill((0,0,0))
        self.fade.set_alpha(0)
    def fadeout(self):
        for alpha in range(1, 255, 1):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.running = False
                    return
            self.fade.set_alpha(alpha)
            screen.blit(self.fade, (0,0))
            pygame.display.flip()
            pygame.time.delay(5)
    def fadein(self):
        for alpha in range(255, 1, -4):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.running = False
                    return
            if alpha <250:
                screen.fill("Blue")
            else:
                screen.fill((0,0,0))
            game.draw()
            self.fade.set_alpha(alpha)
            screen.blit(self.fade, (0,0))
            pygame.display.flip()
            pygame.time.delay(5)
        self.fade.set_alpha(0)

## background class
class background():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.image = pygame.image.load(str(path) + "Background.png")
        self.image = pygame.transform.scale(self.image, (1400, 800))

    def draw(self):
        screen.blit(self.image, (self.x, self.y))
        screen.blit(self.image, (self.x - 1400, self.y))
        screen.blit(self.image, (self.x + 1400, self.y))
    
    def update(self, amount = 0.5):
        self.x -= amount
        if self.x < -1400:
            self.x = 0

## ground class
class ground():
    def __init__(self):
        self.size = 3
        self.x = 768
        self.image = pygame.image.load(str(path) + "Ground.png")
        self.image = pygame.transform.scale(self.image, (128*self.size, 14*self.size))
        self.y = 680

    def draw(self):
        screen.blit(self.image, (self.x, self.y))
        screen.blit(self.image, (self.x - 256*self.size, self.y))
        screen.blit(self.image, (self.x - 128*self.size, self.y))
        screen.blit(self.image, (self.x + 128*self.size, self.y))
        screen.blit(self.image, (self.x + 256*self.size, self.y))
        screen.blit(self.image, (self.x + 384*self.size, self.y))

        if game.debug:
            pygame.draw.rect(screen, "dark green", (0, 680, 1400, 100))
    
    def update(self, amount = 3):
        self.x -= amount
        if self.x < -128:
            self.x = 768

## shrub controller class
class shrubs():
    def __init__(self):
        self.allshrubs = []
        self.shrubimages = []
        ## load shrub images
        for i in range(0, 5):
            self.shrubimages.append(pygame.image.load(str(path) + "Shrub" + str(i+1) + ".png"))

    def add(self, shrub):
        self.allshrubs.append(shrub)

    def draw(self):
        self.allshrubs.sort(key = lambda shrub: shrub.depth)
        for i in self.allshrubs:
            i.draw()

    def move(self, amount = 3):
        for i in self.allshrubs:
            i.move(amount)

    def check(self):
        for i in self.allshrubs:
            i.check()

## shrub class
class shrub():
    def __init__(self):
        self.x = 1400
        self.size = random.randint(30, 50)
        self.depth = random.randint(3, 5)
        self.y = 715 - self.size*self.depth/3 
        color = 200+ self.depth*5 + random.randint(-10, 10)
        self.color = pygame.Color(color, color, color)
        self.image = []
    def draw(self):
        if self.image == []:
            self.image = pygame.transform.scale(random.choice(game.shrubcontroller.shrubimages), (self.size*self.depth/3, self.size*self.depth/3))
        if game.debug:
            pygame.draw.rect(screen, (0,0,0), (self.x-25, self.y-25, self.size*self.depth/3, self.size*self.depth/3))
        screen.blit(self.image, (self.x-25, self.y-25))
        
    
    def move(self, amount = 2):
        self.x -= amount+(self.depth/2)
    
    def check (self):
        if self.x < -100:
            game.shrubcontroller.allshrubs.remove(self)

class drawnumber():
    def __init__(self):
        self.numbers = []
        for i in range(0, 10):
            self.numbers.append(pygame.image.load(str(path) + "Number" + str(i) + ".png"))

    def draw(self, number, x, y, size = 1):
        number = str(number)
        x -= len(number)*14*size
        for i in range(0, len(number)):
            screen.blit(pygame.transform.scale(self.numbers[int(number[i])], (int(28*size), int(36*size))), ((x + i*28*size), y))

## biiig game class that controls almost everything
class Game():
    def __init__(self):
        self.playing = False
        self.gamestate = "Menu"
        self.debug = False
        ## class inits  
        self.background = background()
        self.ground = ground()
        self.cloudcontroller = clouds()
        self.particlecontroller = particles()
        self.pipecontroller = Pipes()
        self.bird = Bird()
        self.fade = fades()
        self.menu = mainmenu()
        self.shrubcontroller = shrubs()
        self.drawnumber = drawnumber()
        self.highscore = 0

        self.pipeTime = time.time()
        self.cloudTime = time.time()
        self.shrubTime = time.time()
        self.shrubNextTime = random.randint(1, 300)/100
        self.menu.construct()
        self.running = True
        self.firstlaunch = True
        self.pipecontroller.add(Pipe(1400, random.randint(300,600)))
        self.pipecontroller.add(Pipe(1000, random.randint(300,600)))

    def draw(self):
        ## always draw 
        self.background.draw()
        self.cloudcontroller.draw()
        self.pipecontroller.draw()
        self.particlecontroller.draw()
        ## draw depending on gamestate
        if self.gamestate == "Playing":
            self.bird.draw()
            self.drawscore(self.bird.score)

        if self.gamestate == "Menu":
            if not self.bird.alive:
                self.bird.draw()
        
        ## stuff that is always drawn on top
        if self.debug:
            self.drawfps()
        self.ground.draw()
        self.shrubcontroller.draw()
        ## stuff that is drawn even more on top 
        if self.gamestate == "Menu":
            self.menu.draw()
            self.drawscore(self.bird.score, 640, 185, 2)
            self.drawscore(self.highscore, 640, 410, 2)

    def updateall(self):
        self.cloudcontroller.move()
        self.particlecontroller.update()
        if self.gamestate == "Playing" and self.bird.alive:
            self.pipecontroller.update()
            self.background.update()
            self.ground.update()
            self.bird.update()
            self.shrubcontroller.move()
        if self.gamestate == "Menu":
            if self.firstlaunch == True:
                self.pipecontroller.update()
                self.background.update()
                self.ground.update()
                self.shrubcontroller.move()

    def check(self):
        self.cloudcontroller.check()
        self.pipecontroller.check()
        self.shrubcontroller.check()
        if self.gamestate == "Playing" and self.bird.alive:
            if self.bird.checkhit():
                self.bird.die()
                self.gamestate = "Menu"
                self.fade.fadein()
        ## add a pipe every 2 seconds and cloud every 1.5 seconds
        if time.time() - self.pipeTime >= 2:
            self.pipeTime = time.time()
            self.pipecontroller.add(Pipe(1400, random.randint(300,600)))
        if time.time() - self.cloudTime >= 1.5:
            self.cloudcontroller.add(cloud())
            self.cloudTime = time.time()
        if self.bird.alive:
            if time.time() - self.shrubTime >= self.shrubNextTime:
                self.shrubcontroller.add(shrub())
                self.shrubTime = time.time()
                self.shrubNextTime = random.randint(1, 100)/100
        if self.bird.score > self.highscore:
            self.highscore = self.bird.score
    ## toggle debug mode
    def toggledebug(self):
        if self.debug:
            self.debug = False
        else:
            self.debug = True
    ## reset the game
    def reset(self):
            self.bird.reset()
            self.pipecontroller.reset()
            self.pipecontroller.add(Pipe(1400, random.randint(300,600)))
            self.pipecontroller.add(Pipe(1000, random.randint(300,600)))
            self.fade.fadein()
            self.bird.jump()
            self.pipeTime = time.time()
    ## draw the score
    def drawscore(self, score, x = 640, y = 120, size = 2):
        if self.debug:
            self.drawnumber.draw("0123456789", x, y, size)
        else:
            self.drawnumber.draw(score, x, y, size)
    def drawfps(self):
        font = pygame.font.SysFont("Arial", 50)
        text = font.render(f"FPS: {round(clock.get_fps())}", True, "black")
        screen.blit(text, (0, 50))



game = Game()
## get the highscore from the file
f = open(str(path + "highscore.txt"), "r")
game.highscore = int(f.read())
f.close()
## time stuff for adding clouds
firstframe = True
game.cloudcontroller.add(cloud(100))
game.cloudcontroller.add(cloud(300))
game.cloudcontroller.add(cloud(500))
game.cloudcontroller.add(cloud(700))
game.cloudcontroller.add(cloud(900))
game.cloudcontroller.add(cloud(1100))
bloodcount = 0 
debugtimer = 0
while game.running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.running = False
    # fill the screen with a to wipe away anything from last frame
    screen.fill((0,0,0))
    # RENDER YOUR GAME HERE
    ## check if objects are of screen. if they are, remove them
    game.check()
    game.updateall()
    game.draw()
    ## debug stuff
    debugtimer -= 1
    if pygame.key.get_pressed()[pygame.K_d] and debugtimer <= 0:
        debugtimer = 10
        game.toggledebug()
    ## menu stuff
    if game.gamestate == "Menu":
        ## spawn red particles if bird dead
        if not game.bird.alive:
            bloodcount += 1
            if bloodcount >= 5:
                game.particlecontroller.add(particle(game.bird.x, game.bird.y, random.randint(3,7), "red", -10, random.randint(-10,10)/10, 0.5, random.randint(20,40), 0.5, True, 0.6))
                bloodcount = 0
        ## return to game 
        if pygame.key.get_pressed()[pygame.K_SPACE] or game.menu.allbuttons[0].clicked:
            game.fade.fadeout()
            game.menu.allbuttons[0].clicked = False
            game.gamestate = "Playing"
            firstframe = True
            pygame.display.flip()
            game.particlecontroller.removeall()
            game.firstlaunch = False
            
    ## playing stuff
    elif game.gamestate == "Playing":
        if firstframe == True:
            firstframe = False
            pressed = False
            game.reset()
        ## get inputs
        if pygame.key.get_pressed()[pygame.K_SPACE] and not pressed:
            game.bird.jump()
            pressed = True
        else:
            if not pygame.key.get_pressed()[pygame.K_SPACE]:
                pressed = False



    # after drawing, flip the display
    pygame.display.flip()
    clock.tick(60)  # limits FPS to 60

## save the highscore
f = open(str(path + "highscore.txt"), "w")
print ("saving highscore")
f.write(str(game.highscore))
f.close()

## quit pygame
pygame.quit()