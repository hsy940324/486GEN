# 모듈 로딩
import numpy as np
import time
import cv2
import pygame
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_SIZE, WHITE, BLACK, RED, GREEN, COUNTDOWN, POINTTOWIN
import process

running = True
isGameStarting = False
playerCors = []
userChoice = ""
computerChoice = ""
playerScore = [0]
computerScore = 0
classList = '_ Scissors Rock Paper'.split()
playerClassIdx = [0]
timeWaiting = False
endCountDownTime = 0
result = ""
currentWinner = ''
reStartTime = 0
isGameEnd = False

def initData():
    global userChoice
    global computerChoice
    global playerScore
    global computerScore
    global playerClassIdx
    global timeWaiting
    global endCountDownTime
    global result
    global currentWinner
    global reStartTime
    global isGameEnd

    userChoice = ""
    computerChoice = ""
    playerScore = [0]
    computerScore = 0
    playerClassIdx = [0]
    timeWaiting = False
    endCountDownTime = 0
    result = ""
    currentWinner = ""
    reStartTime = 0
    isGameEnd = False

def makePlayerCors():
    result =  {
        0: {'min_x':0, 'min_y':0,'max_x':SCREEN_WIDTH,'max_y':SCREEN_HEIGHT}
    }
    return result

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
    global currentWinner
    global playerClassIdx
    global playerScore
    global classList
    
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
    global playerScore

    resultWinner = ''
    if playerScore[0] == POINTTOWIN:
        resultWinner = 'Player'
    elif computerScore == POINTTOWIN:
        resultWinner = 'Computer'
    
    return resultWinner

def pygameHandler():
    global running
    global isGameStarting

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not timeWaiting:
                    isGameStarting = True
                    initData()
                    startCountDown()
                    break

def printResult(screen, font):
    global userChoice
    global computerChoice
    global computerScore
    global currentWinner
    global reStartTime

    result_text = font.render(f'사용자: {userChoice}', True, WHITE)
    screen.blit(result_text, (10, 40))
    result_text = font.render(f'콤퓨타: {computerChoice}', True, WHITE)
    screen.blit(result_text, (SCREEN_WIDTH//2+10, 40))
    if currentWinner:
        result_text = font.render(f'{currentWinner} 승리!', True, BLACK)
        screen.blit(result_text, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    else:
        result_text = font.render('비김!', True, BLACK)
        screen.blit(result_text, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

    if reStartTime == 0:
        reStartTime = time.time() + 2

def printScore(screen, font):
    global playerScore
    global computerScore

    result_text = font.render(f'사용자 점수: {playerScore[0]}', True, WHITE)
    screen.blit(result_text, (10, 10))
    result_text = font.render(f'콤퓨타 점수: {computerScore}', True, WHITE)
    screen.blit(result_text, (SCREEN_WIDTH//2+10, 10))

def run():
    global playerClassIdx
    global timeWaiting
    global endCountDownTime
    global result
    global reStartTime
    global isGameEnd
    global isGameStarting

    playerCors = makePlayerCors()
    process.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font_path = './game_font.ttf'
    font = pygame.font.Font(font_path, FONT_SIZE)
    pygame.display.set_caption("가위 바위 보")
    clock = pygame.time.Clock()

    # 카메라 설정
    cap = cv2.VideoCapture(0) # 0번 카메라 열기
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,SCREEN_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,SCREEN_HEIGHT)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,1)

    startTime = 0
    
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

        process.processImage(frame,playerCors,playerClassIdx)

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
                    isGameStarting = False
                    isGameEnd = True
                else:
                    startCountDown()

        if isGameEnd:
            result_text = font.render(f'승리자 : {finalWinner}', True, BLACK)
            screen.blit(result_text, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

        if not isGameStarting:
            result_text = font.render('놀이 시작을 위해 스페이스 바를 누르시오.', True, BLACK)
            screen.blit(result_text, (10, SCREEN_HEIGHT - 50))
            
        printScore(screen,font)
        
        pygame.display.flip()
        clock.tick(30)

    cap.release()
    pygame.quit()
    cv2.destroyAllWindows() # 모든 창 닫기