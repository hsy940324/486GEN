import tflite_runtime.interpreter as tflite
import numpy as np
import mediapipe as mp
import cv2 
from config import IMG_SIZE

# TFLite 모델 로딩
modelPath = 'RPS_PreTrained_DenseNet_Augmentation.tflite'
interpreter = tflite.Interpreter(model_path = modelPath) # 모델 로딩
interpreter.allocate_tensors() # tensor 할당
input_details = interpreter.get_input_details()  # input tensor 정보 얻기
output_details = interpreter.get_output_details() # output tensor 정보 얻기
input_dtype = input_details[0]['dtype']

def get_hand_img(img):
    mp_hands = mp.solutions.hands
    print(img.shape)

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

def processImage(frame, cors, idxList):
    # BGR을 RGB로 변경
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

    # 모델의 입력 형태로 수정: (1,320,320,3)
    
    # frame = np.expand_dims(frame, 0)

    for id, cor in cors.items():
        
        img = frame[cor["min_y"] : cor["max_y"], cor["min_x"] : cor["max_x"]]

        hand_img = get_hand_img(img)
        hand_img = cv2.resize(hand_img, (IMG_SIZE,IMG_SIZE))
        idxList[id] = get_prediction(hand_img) + 1

def init():
    global input_details
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    print('model input shape:', (height, width))