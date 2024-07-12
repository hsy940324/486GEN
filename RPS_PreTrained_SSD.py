import pygame
import Single_Mode
import Multi_Mode
from button import Button
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_SIZE, WHITE, BLACK, RED, GREEN

def getPlayMode(screen, font):
    global RED
    global GREEN
    # 버튼 생성
    button1 = Button('Single', (110, 70), RED, screen, font)
    button2 = Button('Multi', (110, 120), GREEN, screen, font)
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
                elif button2.is_clicked(mouse_pos):
                    print("Multi mode selected")
                    modeResult = 'multi'
                    modeSelecting = False
        
        button1.draw(screen)
        button2.draw(screen)
        
        pygame.display.flip()
    
    return modeResult

# Pygame Setup
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font(None, FONT_SIZE)
pygame.display.set_caption("Select Play Mode")
playMode = getPlayMode(screen, font)

if playMode == 'single':
    Single_Mode.run()
else:
    Multi_Mode.run()