
# written by cwa 25/2/2024

import pygame
import math

class SimpleStatView:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 1000))
        self.font = pygame.font.Font(None, 27)
        self.clock = pygame.time.Clock() 

    def value_to_screen(self, state, value):
        if state.day_high == state.day_low:
            return 0
        normalized_value = (value - (state.day_low - 2000)) / ((state.day_high + 2000) - (state.day_low - 2000)) # i played around with this value - it is like 'padding' and helps show the scale of the day high and low
        return self.screen.get_height() - (normalized_value * self.screen.get_height())
    
    def text_to_screen(self, text, x, y=10, color=(233, 233, 233)):
        textobj = self.font.render(text, True, color)
        self.screen.blit(textobj, (x, y))

    def draw_button(self, screen, text, x, y, width, height, color, text_color):
        textobj = self.font.render(text, True, text_color)
        textbox = textobj.get_rect(center=(x + width // 2, y + height // 2))
        pygame.draw.rect(screen, color, (x, y, width, height))
        screen.blit(textobj, textbox)

    def button_click(self, x, y, width, height, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        return (x <= mouse_x <= x + width) and (y <= mouse_y <= y + height)

    def draw(self, state, account, data, index):
        
        # bg
        self.screen.fill((11, 11, 11))

        # resize data dynamically 
        price = self.value_to_screen(state, state.price)
        high  = self.value_to_screen(state, state.day_high)
        low = self.value_to_screen(state, state.day_low)
        vwap = self.value_to_screen(state, state.vwap)
        vahigh = self.value_to_screen(state, state.va_high)
        valow = self.value_to_screen(state, state.va_low)
        ma7 = self.value_to_screen(state, state.ma7)
        ma17 = self.value_to_screen(state, state.ma17)
        ma41 = self.value_to_screen(state, state.ma41)

        # lines
        pygame.draw.polygon(self.screen, (246, 238, 171), [(0, high), (self.screen.get_width(), high), (self.screen.get_width(), low), (0, low)])
        pygame.draw.polygon(self.screen, (201, 221, 148), [(50, vahigh), (self.screen.get_width() - 50, vahigh), (self.screen.get_width() - 50, valow), (50, valow)])
        pygame.draw.line(self.screen, (157, 207, 148), (100, vwap), (self.screen.get_width() - 100, vwap), 21)
        pygame.draw.line(self.screen, (126, 199, 150), (150, ma41), (850, ma41), 15)
        pygame.draw.line(self.screen, (94, 189, 150), (200, ma17), (800, ma17), 11)
        pygame.draw.line(self.screen, (17, 167, 151), (250, ma7), (750, ma7), 7)

        # button
        self.draw_button(self.screen, "buy", 10, 70, 50, 20, (100, 100, 0), (0, 255, 255))
        self.draw_button(self.screen, "sell", 70, 70, 50, 20, (100, 100, 0), (0, 255, 255))

        # text
        self.text_to_screen('balance:    ' + str(account.balance), 10)
        self.text_to_screen('daily P/L:   ' + str(account.daily_pl), 10, 37)
        self.text_to_screen('position:    ' + str(account.positionquantity), 820)
        self.text_to_screen('open P/L:   ' + str(account.open_pl), 820, 37)
        self.text_to_screen(str(data['DateTime'].iloc[index]), 377, 10)

        # trade
        if account.positionquantity > 0:
            entry = self.value_to_screen(state, account.position.entry)
            if entry < price:
                pygame.draw.polygon(self.screen, (73, 73, 77), [(300, entry), (700, entry), (700, price), (300, price)])
            else:
                pygame.draw.polygon(self.screen, (139, 128, 249), [(300, entry), (700, entry), (700, price), (300, price)])
            pygame.draw.line(self.screen, (255, 255, 255), (300, entry), (700, entry), 5)
        elif account.positionquantity < 0:
            entry = self.value_to_screen(state, account.position.entry)
            if entry > price:
                pygame.draw.polygon(self.screen, (73, 73, 77), [(300, entry), (700, entry), (700, price), (300, price)])
            else:
                pygame.draw.polygon(self.screen, (255, 163, 175), [(300, entry), (700, entry), (700, price), (300, price)])
            pygame.draw.line(self.screen, (255, 255, 255), (300, entry), (700, entry), 5)

        pygame.draw.line(self.screen, (111, 71, 197), (300, price), (700, price), 5)

        pygame.display.flip()

    def quit(self):
        pygame.quit()