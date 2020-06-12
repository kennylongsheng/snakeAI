import os
import random
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

    def clear(self):
        self.map = np.zeros((self.size, self.size), dtype=np.int)
        return None

    def setBerry(self,map):
        self.berryPos = dropBerry(map)
        return None

    def snakeBodyUpdate(self, snakeLength):
        if(len(self.snakeBody) > snakeLength):
            head = len(self.snakeBody) - snakeLength
            self.snakeBody = self.snakeBody[head:]
            return None


def initGame(size):
    mapInit = map(size)
    snakeInit = snake(size)
    mapInit.setBerry(mapInit.map)
    return mapInit, snakeInit


def dropBerry(map):
    size = map.shape
    while(True):
        xPick = random.randint(0, size[0] - 1)
        yPick = random.randint(0, size[1] - 1)
        if (map[xPick][yPick] == 0):
            return (xPick, yPick)


def keyFunc(key):
    if(not snakeC.lock):
        snakeC.setDirection(key.name)
        snakeC.lock = True
    return None


def distanceUpdate(map, snake):
    snake.distance = np.zeros(4)  # [180 to wall, 0 to wall, 90 to wall, 270 to wall]
    snake.distance[0] = snake.position[1] - 0
    snake.distance[1] = map.size - 1 - snake.position[1]
    snake.distance[2] = snake.position[0] - 0
    snake.distance[3] = map.size - 1 - snake.position[0]
    return None



def mapUpdate(map, snake):
    if (snake.position == map.berryPos):
        snake.scoreIncrease(1)
        map.setBerry(map.map)
    snake.move(map.map.shape)
    if (snake.position in map.snakeBody[:-1]) or (snake.position[0] < 0) or (snake.position[0] >= map.size) or (snake.position[1] < 0) or (snake.position[1] >= map.size):
        return False
    distanceUpdate(map, snake)
    map.clear()
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
