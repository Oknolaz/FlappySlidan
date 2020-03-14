'''
Flappy Slidan 1.0.5



by Oknogames
'''
import pygame_sdl2
pygame_sdl2.import_as_pygame()


def SCREEN_blit(what, at):
    global RENDERER, spritecache
    Sprite(RENDERER.load_texture(what)).render(at)


def pygame_display_update():
    RENDERER.render_present()
    RENDERER.clear((0, 0, 0))


useswblitting = False

from itertools import cycle
import random
import sys

import pygame
from pygame.locals import *
from pygame.render import *

FPS = 38
SCREENWIDTH = 288 * 2
SCREENHEIGHT = 620 * 2
PIPEGAPSIZE = 120 * 2  # Отвечает за пространство между пипками (Больше значение - больше промежуток)
BASEY = SCREENHEIGHT * 0.79
# Картинки, звуки, хитбоксы
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# Список игровых персонажей, возможно добавление (3 строки для up, middle и down положения)
PLAYERS_LIST = (
    # wtf slidan
    (
        'assets/sprites/wtf.png',
        'assets/sprites/wtf.png',
        'assets/sprites/wtf.png',
    ),
    # green slidan
    (
        'assets/sprites/or.png',
        'assets/sprites/or.png',
        'assets/sprites/or.png',
    ),
    # sleedan lox
    (
        'assets/sprites/lyba.png',
        'assets/sprites/lyba.png',
        'assets/sprites/lyba.png',
    ),
    #pacan
    (
        'assets/sprites/poc.png',
        'assets/sprites/poc.png',
        'assets/sprites/poc.png',
    ),
    (
        'assets/sprites/kaka.png',
        'assets/sprites/kaka.png',
        'assets/sprites/kaka.png',
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background.png',
    'assets/sprites/background2.png',
    'assets/sprites/shash.png',
    'assets/sprites/background3.png'
    
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/sh.png',
    'assets/sprites/palec.png'
)

try:
    xrange
except NameError:
    xrange = range


def main():
    global SCREEN, FPSCLOCK, RENDERER
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    RENDERER = Renderer(None)
    pygame.display.set_caption('Flappy Slidan')

    if useswblitting:
        global SCREEN_blit, pygame_display_update
        SCREEN_blit = SCREEN.blit
        pygame_display_update = pygame.display.update

    #Спрайты цифр для отображения счёта
    IMAGES['numbers'] = (pygame.image.load('assets/sprites/0.png').convert_alpha(), pygame.image.load('assets/sprites/1.png').convert_alpha(), pygame.image.load('assets/sprites/2.png').convert_alpha(), pygame.image.load('assets/sprites/3.png').convert_alpha(), pygame.image.load('assets/sprites/4.png').convert_alpha(), pygame.image.load('assets/sprites/5.png').convert_alpha(), pygame.image.load('assets/sprites/6.png').convert_alpha(), pygame.image.load('assets/sprites/7.png').convert_alpha(), pygame.image.load('assets/sprites/8.png').convert_alpha(), pygame.image.load('assets/sprites/9.png').convert_alpha())

    # спрайт для конца игры
    IMAGES['gameover'] = pygame.image.load('assets/sprites/sex.png').convert_alpha()
    #Победа
    IMAGES['win'] = pygame.image.load('assets/sprites/win.png')
    # сообщение в начале игры
    IMAGES['message'] = pygame.image.load('assets/sprites/sex.png').convert_alpha()
    # Спрайт земли
    IMAGES['base'] = pygame.image.load('assets/sprites/mine.png').convert_alpha()

    # звуки (раскомментировать строку ниже, убрать .ogg в путях к файлам и добавить переменную soundExt в случае возникновения ошибок)
    '''
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'
'''
    SOUNDS['die'] = pygame.mixer.Sound('assets/audio/smert.ogg')
    SOUNDS['hit'] = pygame.mixer.Sound('assets/audio/neudacha.ogg')
    SOUNDS['point'] = pygame.mixer.Sound('assets/audio/pisyn.ogg')
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/pisyn.ogg')
    SOUNDS['wing'] = pygame.mixer.Sound('assets/audio/puk.ogg')
    #SOUNDS['unitaz'] = pygame.mixer.Sound('assets/audio/unitaz.ogg')


    while True:
        # рандомные фоны
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # рандом персонажа
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # рандом труб
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.rotate(pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), 180),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # хитбоксы для труб
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )

        # хитбоксы для игрока
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
        )

        movementInfo = showWelcomeAnimation()
        crashInfo = mainGame(movementInfo)
        showGameOverScreen(crashInfo)


def showWelcomeAnimation():
    """показывает начальный экран flappy slidan'а"""
    # индекс игрока
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    # я сам не понял о чём здесь написал
    loopIter = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)
#    winx = int((SCREENWIDTH - IMAGES['win'].get_width()) / 2)
 #   winy = int(SCREENHEIGHT * 0.12)

    basex = 0
    # движение земли по экрану
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # Shm игрока для вверх-вниз на начальном экране
    playerShmVals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP) or event.type == MOUSEBUTTONDOWN:
                # делает звук первого хлопка и возвращает к игре
                SOUNDS['wing'].play()
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

        
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # рисует спрайты
        SCREEN_blit(IMAGES['background'], (0, 0))
        SCREEN_blit(IMAGES['player'][playerIndex], (playerx, playery + playerShmVals['val']))
        SCREEN_blit(IMAGES['message'], (messagex, messagey))
        SCREEN_blit(IMAGES['base'], (basex, BASEY))

        pygame_display_update()
        FPSCLOCK.tick(FPS)


def mainGame(movementInfo):
    score = playerIndex = loopIter = 0
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']

    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # даёт две пипки
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # список верхних труб
    upperPipes = [
        {
            'x': SCREENWIDTH + 200 * 2,
            'y': newPipe1[0]['y']
        },
        {
            'x': SCREENWIDTH + 200 * 2 + (SCREENWIDTH / 2),
            'y': newPipe2[0]['y']
        },
    ]

    # список нижних труб
    lowerPipes = [
        {
            'x': SCREENWIDTH + 200 * 2,
            'y': newPipe1[1]['y']
        },
        {
            'x': SCREENWIDTH + 200 * 2 + (SCREENWIDTH / 2),
            'y': newPipe2[1]['y']
        },
    ]

    pipeVelX = -4

    # player velocity, max velocity, downward accleration, accleration on flap
    playerVelY = -9  # player's velocity along Y, default same as playerFlapped
    playerMaxVelY = 10  # max vel along Y, max descend speed
    playerMinVelY = -8  # min vel along Y, max ascend speed
    playerAccY = 1  # players downward accleration
    playerRot = 45  # player's rotation
    playerVelRot = 3  # angular speed
    playerRotThr = 20  # rotation threshold
    playerFlapAcc = -9  # players speed on flapping
    playerFlapped = False  # True когда игрок флопит

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP) or event.type == MOUSEBUTTONDOWN:
                if playery > -2 * IMAGES['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
                    SOUNDS['wing'].play()

        # Здесь проверка на краши
        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex}, upperPipes, lowerPipes)
        if crashTest[0]:
            return {'y': playery, 'groundCrash': crashTest[1], 'basex': basex, 'upperPipes': upperPipes, 'lowerPipes': lowerPipes, 'score': score, 'playerVelY': playerVelY, 'playerRot': playerRot}

        # проверка очков
        playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                SOUNDS['point'].play()

        # playerIndex basex изменение
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # rotate игрока
        if playerRot > -90:
            playerRot -= playerVelRot

        # движение игрока
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

            
            playerRot = 45

        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # двигает трубы влево
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # добавляет новые трубы, когда другие уходят за экран
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # убирает первые трубы, если они за экраном
        if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # рисует спрайты
        SCREEN_blit(IMAGES['background'], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN_blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN_blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN_blit(IMAGES['base'], (basex, BASEY))
        # показывет очки
        showScore(score)
       # if score ==	1000:
        #	SCREEN_blit(IMAGES['win'], (winx, winy))
        
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot

        playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
        SCREEN_blit(playerSurface, (playerx, playery))

        pygame_display_update()
        FPSCLOCK.tick(FPS)


def showGameOverScreen(crashInfo):
    """крашит игрока вниз и показывает гейм овер"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # проигрывает звуки удара и смерти
    SOUNDS['hit'].play()
    if not crashInfo['groundCrash']:
        SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP) or event.type == MOUSEBUTTONDOWN:
                if playery + playerHeight >= BASEY - 1:
                    return

        # player y shift
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # player velocity change
        if playerVelY < 15:
            playerVelY += playerAccY

        # rotate only when it's a pipe crash
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        # рисует спрайты
        SCREEN_blit(IMAGES['background'], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN_blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN_blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN_blit(IMAGES['base'], (basex, BASEY))
        showScore(score)

        playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
        SCREEN_blit(playerSurface, (playerx, playery))

        FPSCLOCK.tick(FPS)
        pygame_display_update()


def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
        playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {
            'x': pipeX,
            'y': gapY - pipeHeight
        },  # upper pipe
        {
            'x': pipeX,
            'y': gapY + PIPEGAPSIZE
        },  # lower pipe
    ]


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0  # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN_blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'], player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if slidan collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]


def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1 + x][y1 + y] and hitmask2[x2 + x][y2 + y]:
                return True
    return False


def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


if __name__ == '__main__':
    main()
while True:
	SOUNDS['unitaz'].play()
