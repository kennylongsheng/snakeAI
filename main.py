import os
import random
import math
import time
import keyboard
import numpy as np
import training

import torch
import torch.optim as optim
import torch.optim.lr_scheduler as scheduler

class snake:
    dir2Code = {'left' : 0,
                'right' : 1,
                'up': 2,
                'down' : 3}
    snakeMove = {0: (0, -1),
                 1: (0, 1),
                 2: (-1, 0),
                 3: (1, 0)}
    cc = {0: 1,
          1: 0,
          2: 3,
          3: 2}
    def __init__(self, size):
        self.length = 3
        self.direction = 0
        self.position = (int(size/2), int(size/2))
        self.score = 0
        self.lock = False
        self.distance = 0

    def setDirection(self, x):
        tempC = self.dir2Code.get(x)
        tempCC = self.cc.get(tempC)
        if((tempC != None) and (self.direction != tempCC) and (self.direction != tempC)):
            self.direction = tempC
        return None

    def move(self, size):
        tempC = self.snakeMove.get(self.direction)
        tempX = (self.position[0] + tempC[0]) #% size[0]
        tempY = (self.position[1] + tempC[1]) #% size[1]
        self.position = (tempX, tempY)
        return None

    def scoreIncrease(self, x):
        self.score += x
        self.length += 1
        return None


class map:
    def __init__(self, size):
        self.map = np.zeros((size, size), dtype=np.int)
        self.size = size
        self.snakeBody = []
        self.berryPos = None
        self.boundPoint = [(0, 0), (0, size-1), (size-1, size-1), (size-1, 0)]
        self.clear()

    def clear(self):
        self.map = np.zeros((self.size, self.size), dtype=np.int)
        for yIdx in range(self.size):
            self.map[0][yIdx] = 3
            self.map[self.size-1][yIdx] = 3
        for xIdx in range(self.size):
            self.map[xIdx][0] = 3
            self.map[xIdx][self.size-1] = 3
        return None

    def setBerry(self):
        self.berryPos = dropBerry(self.map, self.boundPoint)
        return None

    def snakeBodyUpdate(self, snakeLength):
        if(len(self.snakeBody) > snakeLength):
            head = len(self.snakeBody) - snakeLength
            self.snakeBody = self.snakeBody[head:]
            return None


def initGame(size):
    mapInit = map(size)
    snakeInit = snake(size)
    mapInit.setBerry()
    return mapInit, snakeInit


def dropBerry(map, boundPoint):
    boundTLX, boundTLY = boundPoint[0]
    boundBRX, boundBRY = boundPoint[2]
    while(True):
        xPick = random.randint(boundTLX+1, boundBRX-1)
        yPick = random.randint(boundTLY+1, boundBRY-1)
        if (map[xPick][yPick] == 0):
            return (xPick, yPick)


def keyFunc(key):
    if(not snakeC.lock):
        snakeC.setDirection(key.name)
        snakeC.lock = True
    return None


def point2Line(p11, p12, p21, p22):
    x1, y1 = p11
    x2, y2 = p12
    x3, y3 = p21
    x4, y4 = p22
    #print(p11 ,p12, p21, p22)
    denominator = ((x1-x2)*(y3-y4))-((y1-y2)*(x3-x4))
    if (denominator == 0):
        return None
    else:
        t = (((x1-x3)*(y3-y4))-((y1-y3)*(x3-x4)))/denominator
        u = -1 * ((((x1-x2)*(y1-y3))-((y1-y2)*(x1-x3)))/denominator)
        if t>=0 and u>=0 and u<=1:
            return (x3+u*(x4-x3), y3+u*(y4-y3))
    return None


def pointInLine(p11, p12, p2):
    d1 = calDis(p11, p2)
    d2 = calDis(p12, p2)
    d3 = calDis(p11, p12)
    if(d1 + d2 == d3):
        return d1
    else:
        return 0

def calDis(p1, p2):
    xp1, yp1 = p1
    xp2, yp2 = p2
    return math.sqrt(((xp2-xp1)**2) + ((yp2-yp1)**2))


def distanceUpdate(map, snake):
    sHead = snake.position
    bPoint = map.boundPoint
    sBody = np.flip(map.snakeBody[:-1], axis=0)
    #np.set_printoptions(precision=3)
    disArr = np.zeros((3,8))
    # print("Check45->{}".format(tempPoint))

    # 0deg
    tempPoint = point2Line(sHead, (sHead[0], sHead[1] + 1), bPoint[1], bPoint[2])
    disArr[0][0] = calDis(sHead, tempPoint)
    disArr[1][0] = pointInLine(sHead, tempPoint, map.berryPos)
    for idx in sBody:
        tempDis = pointInLine(sHead, tempPoint, idx)
        if (tempDis != 0):
            disArr[2][0] = tempDis
            break

    # 45deg
    tempPoint = point2Line(sHead, (sHead[0] - 1, sHead[1] + 1), bPoint[1], bPoint[2])
    if tempPoint == None:
        tempPoint = point2Line(sHead, (sHead[0] - 1, sHead[1] + 1), bPoint[0], bPoint[1])
    disArr[0][1] = calDis(sHead, tempPoint)
    disArr[1][1] = pointInLine(sHead, tempPoint, map.berryPos)
    for idx in sBody:
        tempDis = pointInLine(sHead, tempPoint, idx)
        if (tempDis != 0):
            disArr[2][1] = tempDis
            break

    # 90deg
    tempPoint = point2Line(sHead, (sHead[0] - 1, sHead[1]), bPoint[0], bPoint[1])
    disArr[0][2] = calDis(sHead, tempPoint)
    disArr[1][2] = pointInLine(sHead, tempPoint, map.berryPos)
    for idx in sBody:
        tempDis = pointInLine(sHead, tempPoint, idx)
        if (tempDis != 0):
            disArr[2][2] = tempDis
            break

    # 135deg
    tempPoint = point2Line(sHead, (sHead[0] - 1, sHead[1] - 1), bPoint[0], bPoint[1])
    if tempPoint == None:
        tempPoint = point2Line(sHead, (sHead[0] - 1, sHead[1] - 1), bPoint[0], bPoint[3])
    disArr[0][3] = calDis(sHead, tempPoint)
    disArr[1][3] = pointInLine(sHead, tempPoint, map.berryPos)
    for idx in sBody:
        tempDis = pointInLine(sHead, tempPoint, idx)
        if (tempDis != 0):
            disArr[2][3] = tempDis
            break

    # 180deg
    tempPoint = point2Line(sHead, (sHead[0], sHead[1] - 1), bPoint[0], bPoint[3])
    disArr[0][4] = calDis(sHead, tempPoint)
    disArr[1][4] = pointInLine(sHead, tempPoint, map.berryPos)
    for idx in sBody:
        tempDis = pointInLine(sHead, tempPoint, idx)
        if (tempDis != 0):
            disArr[2][4] = tempDis
            break

    # 225deg
    tempPoint = point2Line(sHead, (sHead[0] + 1, sHead[1] - 1), bPoint[0], bPoint[3])
    if tempPoint == None:
        tempPoint = point2Line(sHead, (sHead[0] + 1, sHead[1] - 1), bPoint[2], bPoint[3])
    disArr[0][5] = calDis(sHead, tempPoint)
    disArr[1][5] = pointInLine(sHead, tempPoint, map.berryPos)
    for idx in sBody:
        tempDis = pointInLine(sHead, tempPoint, idx)
        if (tempDis != 0):
            disArr[2][5] = tempDis
            break

    # 270deg
    tempPoint = point2Line(sHead, (sHead[0] + 1, sHead[1]), bPoint[2], bPoint[3])
    disArr[0][6] = calDis(sHead, tempPoint)
    disArr[1][6] = pointInLine(sHead, tempPoint, map.berryPos)
    for idx in sBody:
        tempDis = pointInLine(sHead, tempPoint, idx)
        if (tempDis != 0):
            disArr[2][6] = tempDis
            break

    # 315deg
    tempPoint = point2Line(sHead, (sHead[0] + 1, sHead[1] + 1), bPoint[2], bPoint[3])
    if tempPoint == None:
        tempPoint = point2Line(sHead, (sHead[0] + 1, sHead[1] + 1), bPoint[1], bPoint[2])
    disArr[0][7] = calDis(sHead, tempPoint)
    disArr[1][7] = pointInLine(sHead, tempPoint, map.berryPos)
    for idx in sBody:
        tempDis = pointInLine(sHead, tempPoint, idx)
        if (tempDis != 0):
            disArr[2][7] = tempDis
            break

    snake.distance = disArr
    return None


def checkCollision(map, snake):
    snakeX, snakeY = snake.position
    boundTLX, boundTLY = map.boundPoint[0]
    boundBRX, boundBRY = map.boundPoint[2]
    if (snake.position in map.snakeBody[:-1]) or (snakeX <= boundTLX) or (snakeX >= boundBRX) or (snakeY <= boundTLY) or (snakeY >= boundBRY):
        return True
    else:
        return False


def mapUpdate(map, snake):
    if (snake.position == map.berryPos):
        snake.scoreIncrease(1)
        map.setBerry()
    snake.move(map.map.shape)
    if checkCollision(map, snake):
        print("*****BOOM*****")
        return False
    map.clear()
    distanceUpdate(map, snake)
    map.map[map.berryPos] = 1
    map.snakeBody.append(snake.position)
    map.snakeBodyUpdate(snakeLength=snake.length)
    for idxBody in map.snakeBody:
        map.map[idxBody] = 2
    return True


def drawMap(map, fps, snake):
    os.system("cls")
    print(f"{fps} frames/second. Score: {snake.score}.")
    print(map.map)
    return None


def main(mapC, snakeC, Alive):
        fps = 3 + ((snakeC.score)**1.1)
        snakeC.lock = False
        keyboard.on_press(callback=keyFunc)
        Alive = mapUpdate(mapC, snakeC)
        drawMap(mapC, int(fps), snakeC)
        time.sleep(1 / fps)
        return Alive


if __name__ == "__main__":
    Alive = False
    boardSize = 20

    while(True):
        if(Alive):
            Alive = main(mapC, snakeC, Alive)
        else:
            mapC, snakeC = initGame(boardSize)
            Alive = True
