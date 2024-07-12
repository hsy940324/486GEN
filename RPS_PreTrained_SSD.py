import pygame
import Single_Mode
import Multi_Mode
from button import Button
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_SIZE, WHITE, BLACK, RED, GREEN

def getPlayMode(screen, font):
    background_image = pygame.image.load('background.jpg')
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    global RED
    global GREEN
    # 버튼 생성
    button_width = SCREEN_WIDTH//2
    button_height = SCREEN_HEIGHT//3
    button1 = Button('Single', (0, SCREEN_HEIGHT-button_height), RED, screen, font, width=button_width, height=button_height)
    button2 = Button('Multi', (SCREEN_WIDTH-button_width, SCREEN_HEIGHT-button_height), GREEN, screen, font, width=button_width, height=button_height)
    modeResult = ''

    modeSelecting = True
    

    while modeSelecting:
        # screen.fill(WHITE)
        screen.blit(background_image, (0, -50))
        text = font.render(f"Select Play Mode", True, BLACK)
        screen.blit(text, (10, 10))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                modeSelecting = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if button1.is_clicked(mouse_pos):
                    print("Single mode selected")
                    modeResult = 'single'
                    modeSelecting = False
                elif button2.is_clicked(mouse_pos):
                    print("Multi mode selected")
                    modeResult = 'multi'
                    modeSelecting = False
        button1.update(pygame.mouse.get_pos())
        button2.update(pygame.mouse.get_pos())
        button1.draw(screen)
        button2.draw(screen)
        
        pygame.display.flip()
    
    return modeResult

# Pygame Setup
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font_path = './game_font.ttf'
font = pygame.font.Font(font_path, FONT_SIZE)
pygame.display.set_caption("Select Play Mode")
playMode = getPlayMode(screen, font)

if playMode == 'single':
    Single_Mode.run()
else:
    Multi_Mode.run()