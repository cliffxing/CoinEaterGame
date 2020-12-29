
import random, sys, time, math, pygame
from pygame.locals import *
from pygame import mixer

mixer.init()
pygame.mixer.pre_init(44100,16,2,4096)
pygame.init()


#COLOR VARIABLES
BackgroundColor = (139,115,85)#Background color (brown)
colorwhite = (255, 255, 255)#color white variable used for text
colorred = (255, 0, 0)#color red variable used for text

#Variables
backgroundmovement = 90     # distance the coin moves from the centre before moving the background
coinspeed = 9         # coin's speed
coinbouncespeed = 6       # how fast the coin jumps 
coinbounceheight = 30    # how high the coin jumps 
initialcoinsize = 25       # initial coin size
winningcoinsize = 300        # winning coin size
invincibility = 2       # invincibility length after losing life
lives = 3        # number of lives player has
numrocks = 80        # number of background rocks
enemycoins = 30    # number of enemy coins 
minimumcoinspeed = 3 # minimum speed coin goes
maximumcoinspeed = 7 # maximum speed coin goes
direction = 2    #change of direction 
menurunning=True #variable needed for title page loop
rulesmenu=True #variable needed for instrucitons page loop

#initilization and dimensions
frames = 30 # frames per second to update the screen
width = 640 # width of the program's window, in pixels
height = 480 # height in pixels
halfwidth = int(width / 2)#width divided by 2
halfheight = int(height / 2)#height divided by 2
screen=pygame.display.set_mode((width, height))
left = 'left'
right = 'right'



def main():
    global frametimer, DISPLAYSURF, standardfont, GoldCoin, FlipCoin, ROCKIMAGES

    pygame.init()
    frametimer = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((width, height))
    standardfont = pygame.font.Font('freesansbold.ttf', 100)


    # loading images
    GoldCoin = pygame.image.load('images/GoldCoin1.png')
    FlipCoin= pygame.transform.flip(GoldCoin, True, False)
    ROCKIMAGES = []

    for i in range(1, 5):
        ROCKIMAGES.append(pygame.image.load('images/Rock%s.png' % i))

    while True:
        runGame()

        
def restart():
    screen.fill(0)
    main()
    runGame()

def runGame():
    # variables needed for beginning of game
    invincible = False  # invincibility
    invincibleduration = 0 # invincibility time
    gameover = False      # gameover variable
    victory = False           # winning variable

    
    

    # viewing variabels
    viewx = 0
    viewy = 0

    rockObjs = []    # list that holds rocks
    objects = [] # stores the rest of the objects in the game

    
    # list for the player
    playercoin = {'surface': pygame.transform.scale(GoldCoin, (initialcoinsize, initialcoinsize)),
                 'facing': left,
                 'size': initialcoinsize,
                 'x': halfwidth,
                 'y': halfheight,
                 'bounce':0,
                 'health': lives}

    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False

    # generates rocks across the background
    for i in range(10):
        rockObjs.append(makeNewRock(viewx, viewy))
        rockObjs[i]['x'] = random.randint(0, width)
        rockObjs[i]['y'] = random.randint(0, height)


    while True: #  game loop
        # checks for invincibility
        if invincible and time.time() - invincibleduration > invincibility:
            invincible = False

        # moves the enemy coins
        
        for sObj in objects:
            # moves the coin and adds jumping mechanic
            sObj['x'] += sObj['movex']
            sObj['y'] += sObj['movey']
            
            

            #random direction change for enemy coins
            if random.randint(0, 99) < direction:
                sObj['movex'] = getRandomSpeed()
                sObj['movey'] = getRandomSpeed()
                if sObj['movex'] > 0: # if statement for facing right
                    sObj['surface'] = pygame.transform.scale(FlipCoin, (sObj['width'], sObj['height']))
                    
                else: # if statement for facing left
                    sObj['surface'] = pygame.transform.scale(GoldCoin, (sObj['width'], sObj['height']))


        # go through all the objects and see if any need to be deleted.
        for i in range(len(rockObjs) - 1, -1, -1):
            if isOutsideActiveArea(viewx, viewy, rockObjs[i]):
                del rockObjs[i]
        for i in range(len(objects) - 1, -1, -1):
            if isOutsideActiveArea(viewx, viewy, objects[i]):
                del objects[i]

        # Adds more rocks and enemy coins when moving out of frame
        while len(rockObjs) < numrocks:
            rockObjs.append(makeNewRock(viewx, viewy))
        while len(objects) < enemycoins:
            objects.append(makeNewCoin(viewx, viewy))


        # moves background to adjust frame
        playerCenterx = playercoin['x'] + int(playercoin['size'] / 2)
        playerCentery = playercoin['y'] + int(playercoin['size'] / 2)
        if (viewx + halfwidth) - playerCenterx > backgroundmovement:
            viewx = playerCenterx + backgroundmovement - halfwidth
        elif playerCenterx - (viewx + halfwidth) > backgroundmovement:
            viewx = playerCenterx - backgroundmovement - halfwidth
        if (viewy + halfheight) - playerCentery > backgroundmovement:
            viewy = playerCentery + backgroundmovement - halfheight
        elif playerCentery - (viewy + halfheight) > backgroundmovement:
            viewy = playerCentery - backgroundmovement - halfheight

        # loads the background (brown)
        DISPLAYSURF.fill(BackgroundColor)


        # loads the rocks 
        for gObj in rockObjs:
            gRect = pygame.Rect( (gObj['x'] - viewx,
                                  gObj['y'] - viewy,
                                  gObj['width'],
                                  gObj['height']) )
            DISPLAYSURF.blit(ROCKIMAGES[gObj['RockImage']], gRect)


        # loads enemy coins 
        for sObj in objects:
            sObj['rect'] = pygame.Rect( (sObj['x'] - viewx,
                                         sObj['y'] - viewy - getBounceAmount(sObj['bounce'], sObj['coinbouncespeed'], sObj['coinbounceheight']),
                                         sObj['width'],
                                         sObj['height']) )
            DISPLAYSURF.blit(sObj['surface'], sObj['rect'])


        # loads player's coin
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameover and not (invincible and flashIsOn):
            playercoin['rect'] = pygame.Rect( (playercoin['x'] - viewx,
                                              playercoin['y'] - viewy - getBounceAmount(playercoin['bounce'], coinbouncespeed, coinbounceheight),
                                              playercoin['size'],
                                              playercoin['size']) )
            DISPLAYSURF.blit(playercoin['surface'], playercoin['rect'])


        # draws healthbar
        drawHealthMeter(playercoin['health'])



        #CONTROLS
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                    if playercoin['facing'] != left: # changes player image
                        playercoin['surface'] = pygame.transform.scale(GoldCoin, (playercoin['size'], playercoin['size']))
                    playercoin['facing'] = left
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True
                    if playercoin['facing'] != right: # changes player image
                        playercoin['surface'] = pygame.transform.scale(FlipCoin, (playercoin['size'], playercoin['size']))
                    playercoin['facing'] = right
                elif victory and event.key == K_r:
                    return


            elif event.type == KEYUP:
                # stops the player's movements
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False

                elif event.key == K_ESCAPE:
                    terminate()


        if not gameover:
            # adds bounce and movement for player
            if moveLeft:
                playercoin['x'] -= coinspeed
            if moveRight:
                playercoin['x'] += coinspeed
            if moveUp:
                playercoin['y'] -= coinspeed
            if moveDown:
                playercoin['y'] += coinspeed

            if (moveLeft or moveRight or moveUp or moveDown) or playercoin['bounce'] != 0:
                playercoin['bounce'] += 1
            
            if playercoin['bounce'] > coinbouncespeed:
                playercoin['bounce'] = 0 # resest jump amount

                
            # collision detection
            for i in range(len(objects)-1, -1, -1):
                sqObj = objects[i]
                if 'rect' in sqObj and playercoin['rect'].colliderect(sqObj['rect']): #if player touches coin
                    

                    if sqObj['width'] * sqObj['height'] <= playercoin['size']**2: #if player is larger and eats the coin
                        
                        
                        playercoin['size'] += int( (sqObj['width'] * sqObj['height'])**0.2 ) + 1
                        del objects[i]

                        Chomp=mixer.Sound("audio/Chomp.wav")
                        Chomp.play()

                        
                        if playercoin['facing'] == left:
                            playercoin['surface'] = pygame.transform.scale(GoldCoin, (playercoin['size'], playercoin['size']))
                        if playercoin['facing'] == right:
                            playercoin['surface'] = pygame.transform.scale(FlipCoin, (playercoin['size'], playercoin['size']))

                        if playercoin['size'] > winningcoinsize:
                            victory = True # player wins game if achieved size 

                    elif not invincible:
                        # player is smaller and takes damage
                        invincible = True
                        invincibleduration = time.time()
                        playercoin['health'] -= 1
                        if playercoin['health'] == 0:
                            gameover = True # player loses
                            
        else:
            text=font.render("GAMEOVER",True,(255,255,255)) #displays game over text
            textRect=text.get_rect()
            textRect.center=[325,100]
            screen.blit(text,textRect)

            text=font.render("Press G to Play Again",True,(255,255,255)) #play again text
            textRect=text.get_rect()
            textRect.center=[325,200]
            screen.blit(text,textRect)
            pygame.display.update()
            pygame.display.update()
            replay=True
            while replay: #while loop asking player to press g to play again
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); 
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_g:
                            restart() #restarts if player presses 'g'

            
                
                
            
            
        # player wins
        if victory:
            text=font.render("YOU WIN!",True,(255,255,255)) #displays win text
            textRect=text.get_rect()
            textRect.center=[325,100]
            screen.blit(text,textRect)
            pygame.display.update()

            text=font.render("Press G to Play Again",True,(255,255,255)) #asks player to play again
            textRect=text.get_rect()
            textRect.center=[325,200]
            screen.blit(text,textRect)
            pygame.display.update()
            pygame.display.update()
            replay=True
            while replay: #while loop asking player to press g to play again
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); 
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_g:
                            restart() #restarts if player presses 'g'
                            
        pygame.display.update()
        frametimer.tick(frames)




def drawHealthMeter(currentHealth):
    for i in range(currentHealth): # draw red health bars
        pygame.draw.rect(DISPLAYSURF, colorred,   (15, 5 + (10 * lives) - i * 10, 20, 10))
    for i in range(lives): # draw the white outlines
        pygame.draw.rect(DISPLAYSURF, colorwhite, (15, 5 + (10 * lives) - i * 10, 20, 10), 1)


def terminate(): #terminates program
    pygame.quit()
    sys.exit()


def getBounceAmount(currentBounce, coinbouncespeed, coinbounceheight):#adds bounce to the game
    return int(math.sin( (math.pi / float(coinbouncespeed)) * currentBounce ) * coinbounceheight) #returns number of pixels to bounce



def getRandomSpeed(): #randomizes enemy coin speed
    speed = random.randint(minimumcoinspeed, maximumcoinspeed)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPos(viewx, viewy, objWidth, objHeight): #randomizes camera view
    # creates a rectangle of the camera view
    cameraRect = pygame.Rect(viewx, viewy, width, height)
    while True:
        x = random.randint(viewx - width, viewx + (2 * width))
        y = random.randint(viewy - height, viewy + (2 * height))
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y


def makeNewCoin(viewx, viewy): #generates enemy coins
    sq = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    sq['width']  = (generalSize + random.randint(0, 10)) * multiplier
    sq['height'] = (generalSize + random.randint(0, 10)) * multiplier
    sq['x'], sq['y'] = getRandomOffCameraPos(viewx, viewy, sq['width'], sq['height'])
    sq['movex'] = getRandomSpeed()
    sq['movey'] = getRandomSpeed()
    if sq['movex'] < 0: 
        sq['surface'] = pygame.transform.scale(GoldCoin, (sq['width'], sq['height']))
    else: 
        sq['surface'] = pygame.transform.scale(FlipCoin, (sq['width'], sq['height']))
    sq['bounce'] = 0
    sq['coinbouncespeed'] = random.randint(10, 18)
    sq['coinbounceheight'] = random.randint(10, 50)
    return sq


def makeNewRock(viewx, viewy): #generates background rocks
    gr = {}
    gr['RockImage'] = random.randint(0, len(ROCKIMAGES) - 1)
    gr['width']  = ROCKIMAGES[0].get_width()
    gr['height'] = ROCKIMAGES[0].get_height()
    gr['x'], gr['y'] = getRandomOffCameraPos(viewx, viewy, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect( (gr['x'], gr['y'], gr['width'], gr['height']) )
    return gr


def isOutsideActiveArea(viewx, viewy, obj): #function returns False if viewx and viewy are outside window
    boundsLeftEdge = viewx - width
    boundsTopEdge = viewy - height
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, width * 3, height * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)

#font and loads images for titlescreen and text
font=pygame.font.SysFont(None,35)
titlepage=pygame.image.load('images/titlepage.jpg')
rulesmenu=pygame.image.load('images/rulesmenu.jpg')


    
run=True
while run: #while loop for title screen
    for event in pygame.event.get():
        pygame.mixer.music.load("audio/piratemusic.mp3") #loads audio
        pygame.mixer.music.play(-1, 0.0) #plays audio
        pygame.mixer.music.set_volume(0.25) #sets audio volume
        screen.blit(titlepage,(110,0))
        text=font.render("Press Space Twice to Play",True,(255,255,255)) #text 
        textRect=text.get_rect()
        textRect.center=[325,25]
        screen.blit(text,textRect)
        pygame.display.update()
        
        text=font.render("Press 'R' For Game Rules",True,(255,255,255)) #text
        textRect=text.get_rect()
        textRect.center=[325,465]
        screen.blit(text,textRect)
        pygame.display.update()
        
        if event.type == pygame.QUIT:
            pygame.quit(); 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: #if player presses r, rules menu loads
                run=False
                screen.fill(0)
                screen.blit(rulesmenu, (110,-75))
                menurunning=True
                text=font.render("Press Any Key to Continue",True,(255,255,255)) #text
                textRect=text.get_rect()
                textRect.center=[325,465]
                screen.blit(text,textRect)
                pygame.display.update()
                pygame.display.update()
                
        
            if event.key == pygame.K_SPACE: #if player presses space, the loop exits and the game begins
                run=False
                
             
                

                
while menurunning:
    for event in pygame.event.get():
            
            if event.type==pygame.KEYDOWN:
                menurunning= False
    
  
          
    

if __name__ == '__main__':
    main()



