# 모듈 로딩
import numpy as np
import time
import cv2 
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_SIZE, WHITE, BLACK, RED, GREEN, COUNTDOWN, POINTTOWIN
import process

running = True
isGameStarting = False
playerCors = {}
playerChoice = [0,0]
userChoice = ""
computerChoice = ""
playerScore = [0,0]
computerScore = 0
classList = '_ Scissors Rock Paper'.split()
playerClassIdx = [0,0]
timeWaiting = False
endCountDownTime = 0
result = ""
currentWinner = ""
reStartTime = 0
isGameEnd = False

def initData():
    global playerChoice
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

    playerChoice = [0,0]
    userChoice = ""
    computerChoice = ""
    playerScore = [0,0]
    computerScore = 0
    playerClassIdx = [0,0]
    timeWaiting = False
    endCountDownTime = 0
    result = ""
    currentWinner = ""
    reStartTime = 0
    isGameEnd = False

def makePlayerCors():
    result =  {
        0: {'min_x':0, 'min_y':0,'max_x':SCREEN_WIDTH//2,'max_y':SCREEN_HEIGHT},
        1: {'min_x':SCREEN_WIDTH//2, 'min_y':0,'max_x':SCREEN_WIDTH,'max_y':SCREEN_HEIGHT}
    }
    return result

def startCountDown():
    global timeWaiting
    global endCountDownTime

    timeWaiting = True
    endCountDownTime = time.time() + COUNTDOWN
    
def calGameResult():
    global result
    global playerChoice
    global userChoice
    global computerChoice
    global computerScore
    global currentWinner
    global playerClassIdx
    global playerScore
    global classList
    
    # Game Logic
    playerChoice[0] = classList[playerClassIdx[1]] # 역순으로 저장해야함
    playerChoice[1] = classList[playerClassIdx[0]]
    if playerChoice[0] == playerChoice[1]:
        currentWinner = ''
        result = 'Draw'
    elif (playerChoice[0] == 'Rock' and playerChoice[1] == 'Scissors') or \
            (playerChoice[0] == 'Scissors' and playerChoice[1] == 'Paper') or \
            (playerChoice[0] == 'Paper' and playerChoice[1] == 'Rock'):
        currentWinner = 'Player 1'
        playerScore[0] += 1
        result = 'Player 1 wins'
    else:
        currentWinner = 'Player 2'
        playerScore[1] += 1
        result = 'Player 2 wins'

def decideWinner():
    global playerScore

    resultWinner = ''
    if playerScore[0] == POINTTOWIN:
        resultWinner = 'Player 1'
    elif playerScore[1] == POINTTOWIN:
        resultWinner = 'Player 2'
    
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
    global playerChoice
    global computerScore
    global currentWinner
    global reStartTime
    global playerScore

    result_text = font.render(f'{playerChoice[0]}', True, BLACK)
    screen.blit(result_text, (100, 70))
    result_text = font.render(f'{playerChoice[1]}', True, BLACK)
    screen.blit(result_text, (SCREEN_WIDTH//2+50, 70))

    if currentWinner:
        x_loc = 0 if currentWinner == "Player 1" else SCREEN_WIDTH//2 + 50
        result_text = font.render(f'{currentWinner} Win!', True, RED)
        screen.blit(result_text, (x_loc, SCREEN_HEIGHT//2))
    else:
        result_text = font.render('Draw!', True, BLACK)
        screen.blit(result_text, (SCREEN_WIDTH//2 - 40, SCREEN_HEIGHT//2))

    if reStartTime == 0:
        reStartTime = time.time() + 2

def printScore(screen, font):
    global playerScore

    result_text = font.render(f'Player 1', True, BLACK)
    pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, 50))
    # pygame.draw.rect(screen, WHITE, (0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60))

    screen.blit(result_text, (10, 10))
    result_text = font.render(f'Player 2', True, BLACK)
    screen.blit(result_text, (SCREEN_WIDTH//2 + 170, 10))

    score_text = font.render(f'{playerScore[0]} : {playerScore[1]}', True, BLACK)
    screen.blit(score_text, (SCREEN_WIDTH//2 - 30, 10))

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
    pygame.display.set_caption("Rock Paper Scissors Game")
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
        frame_origin = frame
        if not ret: break
        
        # FPS 계산
        curTime = time.time()
        fps = 1/(curTime - startTime)
        startTime = curTime


        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            screen.blit(frame, (0, 0))

        if timeWaiting:
            nowTime = time.time()
            remain_time = round((endCountDownTime - nowTime)//1.5)
            result_text = font.render(str(remain_time), True, RED)
            screen.blit(result_text, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            if remain_time <= 0:
                process.processImage(frame_origin,playerCors,playerClassIdx)
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
            screen.blit(result_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2))

        if not isGameStarting:
            
            result_text = font.render('놀이 시작을 위해 스페이스 바를 누르시오.', True, BLACK)
            screen.blit(result_text, (10, SCREEN_HEIGHT - 50))

        # Multi Mode Line Draw 
        start_pos = (int(SCREEN_WIDTH//2),0)
        end_pos = (int(SCREEN_WIDTH//2), int(SCREEN_HEIGHT))
        pygame.draw.line(screen, BLACK, start_pos, end_pos, 5)

        printScore(screen,font)

        pygame.display.flip()
        clock.tick(30)

    cap.release()
    pygame.quit()
    cv2.destroyAllWindows() # 모든 창 닫기