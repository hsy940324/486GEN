# 모듈 로딩
import tflite_runtime.interpreter as tflite
import numpy as np
import time
import cv2 
import tensorflow as tf
import pygame
import random
import math
import mediapipe as mp
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_SIZE, WHITE, BLACK, RED, GREEN, COUNTDOWN, POINTTOWIN
import process

running = True
playerCors = []
userChoice = ""
computerChoice = ""
playerScore = [0]
computerScore = 0
classList = '_ Scissors Rock Paper'.split()
playerClassIdx = [0]

def makePlayerCors():
    result =  {
        0: {'min_x':0, 'min_y':0,'max_x':SCREEN_WIDTH,'max_y':SCREEN_HEIGHT}
    }
    return result

def getPlayerCount(screen, font):
    input_box = pygame.Rect(200, 200, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((30, 30, 30))
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    return int(text)

def startCountDown():
    global timeWaiting
    global endCountDownTime

    timeWaiting = True
    endCountDownTime = time.time() + COUNTDOWN
    
def calGameResult():
    global result
    global userChoice
    global computerChoice
    global computerScore
    global multiPlayerScore
    global currentWinner
    global playerClassIdx
    
    # Game Logic
    userChoice = classList[playerClassIdx[0]]
    computerChoice = random.choice(['Rock', 'Paper', 'Scissors'])
    if userChoice == computerChoice:
        currentWinner = ''
        result = 'Draw'
    elif (userChoice == 'Rock' and computerChoice == 'Scissors') or \
            (userChoice == 'Scissors' and computerChoice == 'Paper') or \
            (userChoice == 'Paper' and computerChoice == 'Rock'):
        currentWinner = 'Player'
        playerScore[0] += 1
        result = 'User wins'
    else:
        currentWinner = 'Computer'
        computerScore += 1
        result = 'Computer wins'

def decideWinner():
    global computerScore
    global multiPlayerScore

    resultWinner = ''
    if playerScore[0] == POINTTOWIN:
        resultWinner = 'Player'
    elif computerScore == POINTTOWIN:
        resultWinner = 'Computer'
    
    return resultWinner

def pygameHandler():
    global running

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not timeWaiting:
                    startCountDown()
                    break

def printResult(screen, font):
    global playMode
    global userChoice
    global computerChoice
    global multiPlayerScore
    global computerScore
    global currentWinner
    global reStartTime

    result_text = font.render(f'Player: {userChoice}', True, WHITE)
    screen.blit(result_text, (10, 10))
    result_text = font.render(f'Computer: {computerChoice}', True, WHITE)
    screen.blit(result_text, (10, 25))
    result_text = font.render(f'Player Score: {playerScore[0]}', True, WHITE)
    screen.blit(result_text, (10, 40))
    result_text = font.render(f'Computer Score: {computerScore}', True, WHITE)
    screen.blit(result_text, (10, 55))
    if currentWinner:
        result_text = font.render(f'{currentWinner} win!', True, BLACK)
        screen.blit(result_text, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    else:
        result_text = font.render('Draw!', True, BLACK)
        screen.blit(result_text, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

    if reStartTime == 0:
        reStartTime = time.time() + 2

def run():
    global playerClassIdx

    playerCors = makePlayerCors()
    process.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.Font(None, FONT_SIZE)
    pygame.display.set_caption("Rock Paper Scissors Game")
    clock = pygame.time.Clock()

    # 카메라 설정
    cap = cv2.VideoCapture(0) # 0번 카메라 열기
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,SCREEN_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,SCREEN_HEIGHT)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,1)

    startTime = 0
    result = ""
    timeWaiting = False
    endCountDownTime = 0
    multiPlayerScore = [0,0]
    endGameFlag = False
    reStartTime = 0
    currentWinner = ''
    isGameEnd = False


    while running:
        ret,frame=cap.read() # 과거에 캡처된 이미지 읽어서 버리기
        if not ret: break

        pygameHandler()

        screen.fill((255, 255, 255))

        ret,frame=cap.read() # 사진 찍기 -> (240,320,3)
        if not ret: break
        
        # FPS 계산
        curTime = time.time()
        fps = 1/(curTime - startTime)
        startTime = curTime

        playerClassIdx = process.processImage(frame,playerCors)

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            screen.blit(frame, (0, 0))

        if timeWaiting:
            nowTime = time.time()
            remain_time = round((endCountDownTime - nowTime)//1.5)
            result_text = font.render(str(remain_time), True, BLACK)
            screen.blit(result_text, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            if remain_time <= 0:
                timeWaiting = False
                calGameResult()

        if result:
            printResult(screen, font)
            nowTime = time.time()
            if reStartTime != 0 and nowTime >= reStartTime:
                result = ''
                reStartTime = 0
                finalWinner = decideWinner()
                if finalWinner:
                    isGameEnd = True
                else:
                    startCountDown()

        if isGameEnd:
            result_text = font.render(f'Winner : {finalWinner}', True, BLACK)
            screen.blit(result_text, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))


        pygame.display.flip()
        clock.tick(30)

    cap.release()
    pygame.quit()
    cv2.destroyAllWindows() # 모든 창 닫기