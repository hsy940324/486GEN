import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Button:
    def __init__(self, text, pos, color, screen, font):
        self.text = text
        self.pos = pos
        self.color = color
        self.screen = screen
        self.font = font
        self.rect = pygame.Rect(pos[0], pos[1], 200, 50)
        self.text_surface = font.render(text, True, WHITE)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surface, (self.pos[0] + 10, self.pos[1] + 10))
    
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
