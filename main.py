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

    def clear(self):
        self.map = np.zeros((self.size, self.size), dtype=np.int)
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


def pointInLine():
    return None


def calDis(p1, p2):
    xp1, yp1 = p1
    xp2, yp2 = p2
    return math.sqrt(((xp2-xp1)**2) + ((yp2-yp1)**2))


def distanceUpdate(map, snake):
    sHead = snake.position
    bPoint = map.boundPoint
    disArr = np.zeros(8)
    # print("Check45->{}".format(tempPoint))
    tempPoint = point2Line(sHead, (sHead[0], sHead[1] + 1), bPoint[1], bPoint[2])  # 0deg
    disArr[0] = calDis(sHead, tempPoint)
    tempPoint = point2Line(sHead, (sHead[0] - 1, sHead[1] + 1), bPoint[1], bPoint[2])  # 45deg
    if tempPoint == None:
        tempPoint = point2Line(sHead, (sHead[0] - 1, sHead[1] + 1), bPoint[0], bPoint[1])  # 45deg
    #print("Check45->{}".format(tempPoint))
    disArr[1] = calDis(sHead, tempPoint)
    tempPoint = point2Line(sHead, (sHead[0] - 1, sHead[1]), bPoint[0], bPoint[1])  # 90deg
    disArr[2] = calDis(sHead, tempPoint)
    tempPoint = point2Line(sHead, (sHead[0] - 1, sHead[1] - 1), bPoint[0], bPoint[1])  # 135deg
    if tempPoint == None:
        tempPoint = point2Line(sHead, (sHead[0] - 1, sHead[1] - 1), bPoint[0], bPoint[3])  # 135deg
    #print("Check135->{}".format(tempPoint))
    disArr[3] = calDis(sHead, tempPoint)
    tempPoint = point2Line(sHead, (sHead[0], sHead[1] - 1), bPoint[0], bPoint[3])  # 180deg
    disArr[4] = calDis(sHead, tempPoint)
    tempPoint = point2Line(sHead, (sHead[0] + 1, sHead[1] - 1), bPoint[0], bPoint[3])  # 225deg
    if tempPoint == None:
        tempPoint = point2Line(sHead, (sHead[0] + 1, sHead[1] - 1), bPoint[2], bPoint[3])  # 225deg
    #print("Check225->{}".format(tempPoint))
    disArr[5] = calDis(sHead, tempPoint)
    tempPoint = point2Line(sHead, (sHead[0] + 1, sHead[1]), bPoint[2], bPoint[3])  # 270deg
    disArr[6] = calDis(sHead, tempPoint)
    tempPoint = point2Line(sHead, (sHead[0] + 1, sHead[1] + 1), bPoint[2], bPoint[3])  # 315deg
    if tempPoint == None:
        tempPoint = point2Line(sHead, (sHead[0] + 1, sHead[1] + 1), bPoint[1], bPoint[2])  # 315deg
    #print("Check315->{}".format(tempPoint))
    disArr[7] = calDis(sHead, tempPoint)
    snake.distance = disArr
    return None


def lineLineIntersect():
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
        map.map[idxBody] = -1
    return True


def drawMap(map, fps, snake):
    os.system("cls")
    print(f"{fps} frames/second. Score: {snake.score}.")
    print(map.map)
    print(snake.distance)
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
    boardSize = 10

    while(True):
        if(Alive):
            Alive = main(mapC, snakeC, Alive)
        else:
            mapC, snakeC = initGame(boardSize)
            Alive = True
