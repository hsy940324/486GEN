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
import Single_Mode

# TFLite 모델 로딩
modelPath = 'RPS_PreTrained_DenseNet_Augmentation.tflite'
interpreter = tflite.Interpreter(model_path = modelPath) # 모델 로딩
interpreter.allocate_tensors() # tensor 할당
input_details = interpreter.get_input_details()  # input tensor 정보 얻기
output_details = interpreter.get_output_details() # output tensor 정보 얻기
input_dtype = input_details[0]['dtype']
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]
print('model input shape:', (height, width))

playerClassIdx = []
screen_width = 320
screen_height = 240
playerCors = []
userChoice = ""
computerChoice = ""
playerScore = []
computerScore = 0

classList = '_ Scissors Rock Paper'.split()
colorList = [(),(255,0,0),(0,255,0),(0,0,255)]
IMG_SIZE = 64
threshold = 0.8
def get_hand_img(img):
 
    mp_hands = mp.solutions.hands
 
    with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:
 
        results = hands.process(img)
 
    if results.multi_hand_landmarks is None: return img
 
    hand = results.multi_hand_landmarks[0]
    landmarks = hand.landmark
 
    imgH, imgW, _ = img.shape
    posX_list, posY_list = [], []
 
    for landmark in landmarks:
 
        posX, posY = int(landmark.x * imgW), int(landmark.y * imgH)
 
        posX_list.append(posX)
        posY_list.append(posY)
 
    min_x, max_x, min_y, max_y = min(posX_list), max(posX_list), min(posY_list), max(posY_list)
 
    padding_ratio = 0.3
 
    x_padding = int((max_x - min_x) * padding_ratio)
    y_padding = int((max_y - min_y) * padding_ratio)
 
    min_x = max(min_x - x_padding, 0)
    max_x = min(max_x + x_padding, imgW)
    min_y = max(min_y - y_padding, 0)
    max_y = min(max_y + y_padding, imgH)
 
    crop_img = img[min_y: max_y, min_x:max_x]
 
    return crop_img
 
def get_prediction(hand_img):
 
    hand_img = cv2.resize(hand_img, (IMG_SIZE, IMG_SIZE))
    hand_img = np.expand_dims(hand_img, 0)  
   

    interpreter.set_tensor(input_details[0]['index'], hand_img.astype(input_dtype))
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])[0]

    label = np.argmax(output_data)
    return label
 
def processImage(frame, cors):
    global playerClassIdx
   
    # BGR을 RGB로 변경
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
 
    # 모델의 입력 형태로 수정: (1,320,320,3)
    frame = cv2.resize(frame, (IMG_SIZE,IMG_SIZE))
    # frame = np.expand_dims(frame, 0)
 
    for id, cor in cors.items():
 
        img = frame[cor["min_y"] : cor["max_y"], cor["min_x"] : cor["max_x"]]
 
        hand_img = get_hand_img(img)
        playerClassIdx[id] = get_prediction(hand_img) + 1


# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Button:
    def __init__(self, text, pos, color):
        self.text = text
        self.pos = pos
        self.color = color
        self.rect = pygame.Rect(pos[0], pos[1], 200, 50)
        self.text_surface = font.render(text, True, WHITE)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surface, (self.pos[0] + 10, self.pos[1] + 10))
    
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def getPlayMode(screen, font):
    global RED
    global GREEN
    global playerClassIdx
    # 버튼 생성
    button1 = Button('Single', (110, 70), RED)
    button2 = Button('Multi', (110, 120), GREEN)
    modeResult = ''

    modeSelecting = True
    while modeSelecting:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                modeSelecting = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if button1.is_clicked(mouse_pos):
                    print("Single mode selected")
                    modeResult = 'single'
                    modeSelecting = False
                    playerClassIdx = [0]
                    playerScore = [0]
                elif button2.is_clicked(mouse_pos):
                    print("Multi mode selected")
                    modeResult = 'multi'
                    modeSelecting = False
                    playerClassIdx = [0,0]
                    playerScore = [0,0]
        
        button1.draw(screen)
        button2.draw(screen)
        
        pygame.display.flip()
    
    return modeResult

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

def makePlayerCors():
    global playerCors
    if playMode == 'single':
        playerCors = {
            0: {'min_x':0, 'min_y':0,'max_x':screen_width,'max_y':screen_height}
        }
    else:
        playerCors = {
            0: {'min_x':0, 'min_y':0,'max_x':screen_width//2,'max_y':screen_height},
            1: {'min_x':screen_width//2, 'min_y':0,'max_x':screen_width,'max_y':screen_height}
        }

# Pygame Setup
pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
font = pygame.font.Font(None, 24)
pygame.display.set_caption("Select Play Mode")
playMode = getPlayMode(screen, font)
makePlayerCors()

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Rock Paper Scissors Game")
clock = pygame.time.Clock()

# 카메라 설정
cap = cv2.VideoCapture(0) # 0번 카메라 열기
cap.set(cv2.CAP_PROP_FRAME_WIDTH,screen_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,screen_height)
cap.set(cv2.CAP_PROP_BUFFERSIZE,1)

running = True
startTime = 0
result = ""
timeWaiting = False
endCountDownTime = 0
countDown = 6
singlePlayerScore = 0
multiPlayerScore = [0,0]
pointToWin = 3
endGameFlag = False
reStartTime = 0
currentWinner = ''
isGameEnd = False

def startCountDown():
    global timeWaiting
    global countDown
    global endCountDownTime

    timeWaiting = True
    endCountDownTime = time.time() + countDown
    
def calGameResult():
    global result
    global userChoice
    global computerChoice
    global singlePlayerScore
    global computerScore
    global multiPlayerScore
    global currentWinner
    
    # Game Logic
    if playMode == 'single':
        userChoice = classList[playerClassIdx[0]]
        computerChoice = random.choice(['Rock', 'Paper', 'Scissors'])
        if userChoice == computerChoice:
            currentWinner = ''
            result = 'Draw'
        elif (userChoice == 'Rock' and computerChoice == 'Scissors') or \
                (userChoice == 'Scissors' and computerChoice == 'Paper') or \
                (userChoice == 'Paper' and computerChoice == 'Rock'):
            currentWinner = 'Player'
            singlePlayerScore += 1
            result = 'User wins'
        else:
            currentWinner = 'Computer'
            computerScore += 1
            result = 'Computer wins'
    else: # multi
        userChoice = classList[playerClassIdx]
        computerChoice = random.choice(['Rock', 'Paper', 'Scissors'])
        if userChoice == computerChoice:
            result = 'Draw'
        elif (userChoice == 'Rock' and computerChoice == 'Scissors') or \
                (userChoice == 'Scissors' and computerChoice == 'Paper') or \
                (userChoice == 'Paper' and computerChoice == 'Rock'):
            result = 'User wins'
        else:
            result = 'Computer wins'

def decideWinner():
    global singlePlayerScore
    global computerScore
    global multiPlayerScore
    global pointToWin

    resultWinner = ''
    if playMode == 'single':
        if singlePlayerScore == pointToWin:
            resultWinner = 'Player'
        elif computerScore == pointToWin:
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

def printResult(screen):
    global playMode
    global userChoice
    global computerChoice
    global playerClassIdx
    global singlePlayerScore
    global multiPlayerScore
    global computerScore
    global currentWinner
    global screen_width
    global screen_height
    global reStartTime

    if playMode == 'single':
        result_text = font.render(f'Player: {userChoice}', True, WHITE)
        screen.blit(result_text, (10, 10))
        result_text = font.render(f'Computer: {computerChoice}', True, WHITE)
        screen.blit(result_text, (10, 25))
        result_text = font.render(f'Player Score: {singlePlayerScore}', True, WHITE)
        screen.blit(result_text, (10, 40))
        result_text = font.render(f'Computer Score: {computerScore}', True, WHITE)
        screen.blit(result_text, (10, 55))
        if currentWinner:
            result_text = font.render(f'{currentWinner} win!', True, BLACK)
            screen.blit(result_text, (screen_width//2, screen_height//2))
        else:
            result_text = font.render('Draw!', True, BLACK)
            screen.blit(result_text, (screen_width//2, screen_height//2))

        if reStartTime == 0:
            reStartTime = time.time() + 2
    else:
        result_text = font.render(f'Player: {userChoice}', True, WHITE)
        screen.blit(result_text, (10, 10))
        result_text = font.render(f'Computer: {computerChoice}', True, WHITE)
        screen.blit(result_text, (10, 25))
        result_text = font.render(f'Player Score: {singlePlayerScore}', True, WHITE)
        screen.blit(result_text, (10, 40))
        result_text = font.render(f'Computer Score: {computerScore}', True, WHITE)
        screen.blit(result_text, (10, 55))

while running:
    ret,frame=cap.read() # 과거에 캡처된 이미지 읽어서 버리기
    if not ret: break

    pygameHandler()

    screen.fill((255, 255, 255))

    ret,frame=cap.read() # 사진 찍기 -> (240,320,3)
    if not ret: break
    
    # Multi Mode Line Draw
    if playMode == 'multi':
        cv2.line(frame, (int(screen_width//2),0), (int(screen_width//2), int(screen_height)), RED, thickness=1)

    # FPS 계산
    curTime = time.time()
    fps = 1/(curTime - startTime)
    startTime = curTime

    processImage(frame,playerCors)

    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        screen.blit(frame, (0, 0))

    if timeWaiting:
        nowTime = time.time()
        remain_time = round((endCountDownTime - nowTime)//1.5)
        result_text = font.render(str(remain_time), True, BLACK)
        screen.blit(result_text, (screen_width//2, screen_height//2))
        if remain_time <= 0:
            timeWaiting = False
            calGameResult()

    if result:
        printResult(screen)
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
        screen.blit(result_text, (screen_width//2, screen_height//2))


    pygame.display.flip()
    clock.tick(30)

cap.release()
pygame.quit()
cv2.destroyAllWindows() # 모든 창 닫기