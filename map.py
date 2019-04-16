import random
from playsound import playsound
from gtts import gTTS
import pygame
from pygame.locals import *

pygame.init()
windowSize = 100
window = pygame.display.set_mode((windowSize, windowSize))


class mazeObject:
    allObj = []
    chance = 0

    def __init__(self, symbol='', name='', monstersCanKill=True):
        self.symbol = symbol
        self.name = name
        self.monstersCanKill = monstersCanKill
        mazeObject.allObj.append(self)

    def attacked(self, b, y, x):
        b.board[y][x] = None

    def sound(self, direction):
        try:
            direction = ['Forward', 'Right', 'Forward', 'Left'][direction]
            # print(self.name + direction + '.mp3')
            playsound(self.name + direction + '.mp3')
        except:
            pass


class playerClass(mazeObject):
    def __init__(self):
        super().__init__('@', 'Player')
        self.inventory = []

    def sound(self, direction):
        playsound('Walk' + str(random.randint(1, 2)) + '.mp3')


class wallClass(mazeObject):
    chance = 3

    def __init__(self):
        super().__init__('.', 'Wall')

    def breakSound(self, direction):
        direction = ['Forward', 'Right', 'Forward', 'Left'][direction]
        playsound('WallBreak' + direction + '.mp3')


class rockClass(mazeObject):
    chance = 10

    def __init__(self):
        super().__init__('#', 'Rock')

    def attacked(self, b, y, x):
        pass


class monsterClass(mazeObject):
    chance = 20

    def __init__(self, symbol='M', name='Monster'):
        super().__init__(symbol, name)
        self.direction = random.randint(0, 3)

    def update(self, board, y, x, p, rot=1):
        change = [[-1, 0], [0, 1], [1, 0], [0, -1]][self.direction]
        obj = board.moveObj(y, x, (y + change[0]) % board.size, (x + change[1]) % board.size)
        if obj is not None and not obj.monstersCanKill:
            self.direction = (self.direction + rot) % 4
        if board.getCoords(p) is None:
            return None

    def attacked(self, b, y, x):
        super().attacked(b, y, x)
        playsound('MonsterKilledForward.mp3')


class goalClass(mazeObject):
    def __init__(self):
        super().__init__('O', 'Goal', monstersCanKill=False)
        self.locked = True


class keyClass(mazeObject):
    keyAdj = ['Jagged', 'Scented', 'Smooth', 'Slippery', 'Crystal']

    # for adj in keyAdj:i
    #     tts = gTTS(text=adj + ' key', lang='en')
    #     tts.save(adj + 'Key' + '.mp3')

    def __init__(self, b):
        super().__init__(';', 'Key', monstersCanKill=False)
        temp = len(keyClass.keyAdj) - b.difficulty
        if temp < 0:
            temp = 0
        self.adj = keyClass.keyAdj[random.randint(temp, len(keyClass.keyAdj) - 1)]
        if self.adj != 'Crystal':
            self.box = box(self.adj)
            y, x = [random.randint(0, b.size - 1) for _ in range(2)]
            while b.board[y][x] is not None:
                y, x = [random.randint(0, b.size - 1) for _ in range(2)]
            b.board[y][x] = self.box

    def attacked(self, b, y, x):
        b.board[y][x] = monsterClass()
        if self.adj == 'Crystal':
            b.board[b.goalCoords[0]][b.goalCoords[1]].locked = False
        else:
            self.box.locked = False

    def sound(self, direction):
        playsound(self.adj + 'Key.mp3')


class box(mazeObject):
    boxAdj = keyClass.keyAdj
    boxAdj.remove('Crystal')

    # for adj in boxAdj:
    #     tts = gTTS(text=adj + ' box', lang='en')
    #     tts.save(adj + 'Box' + '.mp3')

    def __init__(self, adj):
        super().__init__('B', 'Box', monstersCanKill=False)
        self.adj = adj
        self.locked = True

    def attacked(self, b, y, x):
        if not self.locked:
            b.board[y][x] = keyClass(b)

    def sound(self, direction):
        playsound(self.adj + 'Box.mp3')


class levelClass:
    spaceChar = ' '
    emptyChar = ' '

    def __init__(self, difficulty, p):
        self.difficulty = difficulty
        self.size = difficulty // 3 + int(not bool(difficulty // 3 % 2)) + 3
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.playerStart = 0
        b = self.board
        for y in range(self.size):
            for x in range(self.size):
                for obj in mazeObject.__subclasses__():
                    if obj.chance != 0 and not bool(random.randint(0, obj.chance)) and b[y][x] is None:
                        b[y][x] = obj()

        b[self.playerStart][self.playerStart] = p
        y1, x1, y2, x2 = [random.randint(0, self.size - 1) for _ in range(4)]
        while (y1 == self.playerStart and x1 == self.playerStart) or (y2 == self.playerStart and x2 == self.playerStart) or [y1, x1] == [y2, x2]:
            y1, x1, y2, x2 = [random.randint(0, self.size - 1) for _ in range(4)]
        self.goalCoords = (y1, x1)
        b[y1][x1] = goalClass()
        b[y2][x2] = keyClass(self)
        y, x = [random.randint(0, self.size - 1) for _ in range(2)]
        while self.board[y][x] is not None:
            y, x = [random.randint(0, self.size - 1) for _ in range(2)]
        b[y][x] = keyClass(self)

    def prettyPrint(self):
        for row in self.board:
            for obj in row:
                if obj is None:
                    print(levelClass.emptyChar, end=levelClass.spaceChar)
                else:
                    print(obj.symbol, end=levelClass.spaceChar)
            print()

    def moveObj(self, targety, targetx, desty, destx):
        desty %= self.size
        destx %= self.size
        temp = self.board[desty][destx]
        if type(temp) != goalClass:
            if temp is not None:
                temp.attacked(self, desty, destx)
            else:
                self.board[desty][destx] = self.board[targety][targetx]
                self.board[targety][targetx] = None
        return temp

    def movePlayer(self, direction, p):
        change = [[-1, 0], [0, 1], [1, 0], [0, -1]][direction]
        y, x = self.getCoords(p)
        out = self.moveObj(y, x, y + change[0], x + change[1])
        return out

    def inspectAdjacents(self, p, say=True):
        print()
        return [self.inspect(i, p, say) for i in range(4)]

    def inspect(self, direction, p, say=True):
        change = [[-1, 0], [0, 1], [1, 0], [0, -1]][direction]
        try:
            y, x, = self.getCoords(p)
        except TypeError:
            return
        target = self.board[(y + change[0]) % self.size][(x + change[1]) % self.size]
        if say:
            if target is not None:
                target.sound(direction)
            else:
                playsound('Walk1.mp3')
        return target

    def getCoords(self, obj):
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x] == obj:
                    return y, x
        return None
    
    def getCoordsByType(self, typ):
        for y in range(self.size):
            for x in range(self.size):
                if type(self.board[y][x]) == typ:
                    return y, x
        return None

    def updateLevel(self, p):
        for y in range(self.size):
            for x in range(self.size):
                if type(self.board[y][x]) == monsterClass:
                    if self.board[y][x].update(self, y, x, p) is None:
                        return None


def addText(y, x, txt):
    pygame.font.init()
    shade = 150
    myfont = pygame.font.SysFont('Comic Sans MS', 30)
    textsurface = myfont.render(txt, False, (shade, shade, shade))
    window.blit(textsurface, (x, y))


def showSurroundings(surroundings):
    window.fill((0, 0, 0))
    addText(33, 33, '@')
    for i in range(len(surroundings)):
        y, x = [(0, 33), (33, 66), (66, 33), (33, 0)][i]
        if surroundings[i] is not None:
            addText(y, x, surroundings[i].symbol)
    pygame.display.update()


player = playerClass()
testLevel = levelClass(5, player)
showSurroundings(testLevel.inspectAdjacents(player, False))

action = ''
while action != 'g':
    action = ''
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            try:
                action = {K_w: 'w', K_d: 'd', K_s: 's', K_a: 'a',
                          K_i: 'i', K_l: 'l', K_k: 'k', K_j: 'j',
                          K_g: 'g'}[event.key]
            except KeyError:
                pass
    if action in ['w', 'd', 's', 'a']:
        direction = ['w', 'd', 's', 'a'].index(action)
        t = testLevel.movePlayer(direction, player)
        if type(t) == goalClass and not t.locked:
            gTTS(text=f"Welcome. to level {testLevel.difficulty}", lang='en').save('newLevelSpeech.mp3')
            playsound('newLevelSpeech.mp3')
            testLevel = levelClass(testLevel.difficulty + 1, player)
            testLevel.inspectAdjacents(player)
        else:
            playsound('GoalLockedForward.mp3')
            testLevel.updateLevel(player)
            testLevel.inspectAdjacents(player)
        showSurroundings(testLevel.inspectAdjacents(player, False))
        # testLevel.prettyPrint()
    elif action in ['i', 'l', 'k', 'j']:
        direction = ['i', 'l', 'k', 'j'].index(action)
        testLevel.inspect(direction, player)
    if testLevel.getCoords(player) is None:
        break
print('You died')
playsound('PlayerDead.mp3')
