import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Button:
    # def __init__(self, text, pos, color, screen, font):
    #     self.text = text
    #     self.pos = pos
    #     self.color = color
    #     self.screen = screen
    #     self.font = font
    #     self.rect = pygame.Rect(pos[0], pos[1], 200, 50)
    #     self.text_surface = font.render(text, True, WHITE)
    def __init__(self, text, pos, color, screen, font, width=None, height=None):
        self.text = text
        self.pos = pos
        self.color = color
        self.screen = screen
        self.font = font
        if width is None or height is None:
            self.width, self.height = 200, 50
        else:
            self.width = width
            self.height = height
        self.rect = pygame.Rect(pos[0], pos[1], self.width, self.height)
        self.normal_color = color
        self.hover_color = pygame.Color('dodgerblue2')  # 마우스 오버 시 색상 변경
        self.current_color = self.normal_color
        self.text_surface = font.render(text, True, WHITE)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.normal_color
    
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surface, (self.pos[0] + 10, self.pos[1] + 10))
    
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
