from tabnanny import check
from turtle import position
import pygame
import pygame_menu
import re
import time
import pyautogui

from sunfish import sunfish
from sunfish import compressed
import speech

width, height = pyautogui.size()
scale = (int(height/10-10), int(height/10-10))
white_king = pygame.image.load('Assets/Pieces/White_King.png')
white_king = pygame.transform.scale(white_king, scale)
black_king = pygame.image.load('Assets/Pieces/Black_King.png')
black_king = pygame.transform.scale(black_king, scale)

white_queen = pygame.image.load('Assets/Pieces/White_Queen.png')
white_queen = pygame.transform.scale(white_queen, scale)
black_queen = pygame.image.load('Assets/Pieces/Black_Queen.png')
black_queen = pygame.transform.scale(black_queen, scale)

white_rook = pygame.image.load('Assets/Pieces/White_Rook.png')
white_rook = pygame.transform.scale(white_rook, scale)
black_rook = pygame.image.load('Assets/Pieces/Black_Rook.png')
black_rook = pygame.transform.scale(black_rook, scale)

white_knight = pygame.image.load('Assets/Pieces/White_Knight.png')
white_knight = pygame.transform.scale(white_knight, scale)
black_knight = pygame.image.load('Assets/Pieces/Black_Knight.png')
black_knight = pygame.transform.scale(black_knight, scale)

white_bishop = pygame.image.load('Assets/Pieces/White_Bishop.png')
white_bishop = pygame.transform.scale(white_bishop, scale)
black_bishop = pygame.image.load('Assets/Pieces/Black_Bishop.png')
black_bishop = pygame.transform.scale(black_bishop, scale)

white_pawn = pygame.image.load('Assets/Pieces/White_Pawn.png')
white_pawn = pygame.transform.scale(white_pawn, scale)
black_pawn = pygame.image.load('Assets/Pieces/Black_Pawn.png')
black_pawn = pygame.transform.scale(black_pawn, scale)

white_field = pygame.image.load('Assets/Board/White_Pole.png')
white_field = pygame.transform.scale(white_field, scale)
black_field = pygame.image.load('Assets/Board/Black_Pole.png')
black_field = pygame.transform.scale(black_field, scale)

selected_field = pygame.image.load('Assets/Board/Selected_Pole.png')
selected_field = pygame.transform.scale(selected_field, scale)

empty_field = pygame.image.load('Assets/Board/Empty_Pole.png')
empty_field = pygame.transform.scale(empty_field, scale)

frame_field = pygame.image.load('Assets/Board/Board_Pole.png')
frame_field = pygame.transform.scale(frame_field, scale)

field_1 = pygame.image.load('Assets/Board/1.png')
field_1 = pygame.transform.scale(field_1, scale)

field_2 = pygame.image.load('Assets/Board/2.png')
field_2 = pygame.transform.scale(field_2, scale)

field_3 = pygame.image.load('Assets/Board/3.png')
field_3 = pygame.transform.scale(field_3, scale)

field_4 = pygame.image.load('Assets/Board/4.png')
field_4 = pygame.transform.scale(field_4, scale)

field_5 = pygame.image.load('Assets/Board/5.png')
field_5 = pygame.transform.scale(field_5, scale)

field_6 = pygame.image.load('Assets/Board/6.png')
field_6 = pygame.transform.scale(field_6, scale)

field_7 = pygame.image.load('Assets/Board/7.png')
field_7 = pygame.transform.scale(field_7, scale)

field_8 = pygame.image.load('Assets/Board/8.png')
field_8 = pygame.transform.scale(field_8, scale)

field_A = pygame.image.load('Assets/Board/A.png')
field_A = pygame.transform.scale(field_A, scale)

field_B = pygame.image.load('Assets/Board/B.png')
field_B = pygame.transform.scale(field_B, scale)

field_C = pygame.image.load('Assets/Board/C.png')
field_C = pygame.transform.scale(field_C, scale)

field_D = pygame.image.load('Assets/Board/D.png')
field_D = pygame.transform.scale(field_D, scale)

field_E = pygame.image.load('Assets/Board/E.png')
field_E = pygame.transform.scale(field_E, scale)

field_F = pygame.image.load('Assets/Board/F.png')
field_F = pygame.transform.scale(field_F, scale)

field_G = pygame.image.load('Assets/Board/G.png')
field_G = pygame.transform.scale(field_G, scale)

field_H = pygame.image.load('Assets/Board/H.png')
field_H = pygame.transform.scale(field_H, scale)

BACK = (0, 0, 0)
width, height = empty_field.get_width(), empty_field.get_height()
WIDTH, HEIGHT = 16 * width, 10 * height
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blindfold Chess")
FPS = 60

class Menu:
    pygame.init()

    def start_game_single():
        Game.main(1)

    def start_game_multi():
        Game.main(2)      


    def draw_menu():
        menu = pygame_menu.Menu('Blindfold chess', WIDTH, HEIGHT, 
                                theme=pygame_menu.themes.THEME_BLUE)
        menu.add.button('SINGLEPLAYER', Menu.start_game_single)
        menu.add.button('MULTIPLAYER', Menu.start_game_multi)
        menu.add.button('WYJDŹ', pygame_menu.events.EXIT)
        menu.mainloop(WIN)

class Game:
    board = [   'FP',  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'FP',       # 0-9
                '8',   'b', 'w', 'b', 'w', 'b', 'w', 'b', 'w', '8',        # 10-19
                '7',   'w', 'b', 'w', 'b', 'w', 'b', 'w', 'b', '7',        # 20-29
                '6',   'b', 'w', 'b', 'w', 'b', 'w', 'b', 'w', '6',        # 30-39
                '5',   'w', 'b', 'w', 'b', 'w', 'b', 'w', 'b', '5',        # 40-49
                '4',   'b', 'w', 'b', 'w', 'b', 'w', 'b', 'w', '4',        # 50-59
                '3',   'w', 'b', 'w', 'b', 'w', 'b', 'w', 'b', '3',        # 60-69
                '2',   'b', 'w', 'b', 'w', 'b', 'w', 'b', 'w', '2',        # 70-79
                '1',   'w', 'b', 'w', 'b', 'w', 'b', 'w', 'b', '1',        # 80-89
                'FP',  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'FP'        # 90-99
                ]

    def display_text(text):
        box = pygame.Rect(10 * empty_field.get_width() + 1, 1, 6 * empty_field.get_width(), 1 * empty_field.get_width() - 1)
        font = pygame.font.Font(None, 32)
        board_color = (121, 103, 92)
        color = (255, 255, 255)
        text_surface = font.render(text, True, color)
        pygame.draw.rect(WIN, board_color, box, 0)
        WIN.blit(text_surface, (10 * width + 5, 5))
        pygame.display.update()

    def display_history_field():
        box = pygame.Rect(10 * empty_field.get_width() + 1, empty_field.get_width() + 1, 6 * empty_field.get_width(), 0.5 * empty_field.get_width() - 1)
        font = pygame.font.Font(None, 32)
        board_color = (121, 103, 92)
        color = (255, 255, 255)
        text = "HISTORIA"
        text_surface = font.render(text, True, color)
        pygame.draw.rect(WIN, board_color, box, 0)

        WIN.blit(text_surface, (12.4 * width + 5, width + 5))
        pygame.display.update()

    def display_players_field(player):
        if player == 1:
            box = pygame.Rect(10 * empty_field.get_width() + 1, 1.5 * empty_field.get_width() + 1, 3 * empty_field.get_width() - 1, 0.5 * empty_field.get_width() - 1)
            text = "Gracz 1"
        if player == 2:
            box = pygame.Rect(13 * empty_field.get_width() + 1, 1.5 * empty_field.get_width() + 1, 3 * empty_field.get_width(), 0.5 * empty_field.get_width() - 1)
            text = "Gracz 2"
        font = pygame.font.Font(None, 32)
        board_color = (121, 103, 92)
        color = (255, 255, 255)
        
        text_surface = font.render(text, True, color)
        pygame.draw.rect(WIN, board_color, box, 0)

        if player == 1:
            WIN.blit(text_surface, (11 * width + 5, 1.7 * width + 5))
        if player == 2:
            WIN.blit(text_surface, (14 * width + 5, 1.7 * width + 5))
        pygame.display.update()

    def display_history(hist):
        Game.display_history_field()
        Game.display_players_field(1)
        Game.display_players_field(2)
        box = pygame.Rect(10 * empty_field.get_width() + 1, 2 * empty_field.get_width() + 1, 6 * empty_field.get_width(), 8.5 * empty_field.get_width())
        font = pygame.font.Font(None, 32)
        board_color = (121, 103, 92)
        color = (255, 255, 255)
        text_surface = font.render(hist, True, color)
        pygame.draw.rect(WIN, board_color, box, 0)
        WIN.blit(text_surface, (10 * width + 5, 2 * width + 5))
        WIN.blit(text_surface, (10 * width + 5, 2 * width + 5))
        pygame.display.update()
    

    def draw_board(board):     
        WIN.fill(BACK)
        pos_x = 0
        pos_y = 0
        row = 1
        for i in board:
            if i == 'FP': field = frame_field
            if i == 'A': field = field_A
            if i == 'B': field = field_B
            if i == 'C': field = field_C
            if i == 'D': field = field_D
            if i == 'E': field = field_E
            if i == 'F': field = field_F
            if i == 'G': field = field_G
            if i == 'H': field = field_H
            if i == '1': field = field_1
            if i == '2': field = field_2
            if i == '3': field = field_3
            if i == '4': field = field_4
            if i == '5': field = field_5
            if i == '6': field = field_6
            if i == '7': field = field_7
            if i == '8': field = field_8
            if i == 'b': field = black_field
            if i == 'w': field = white_field
            if i == 's': field = selected_field
            WIN.blit(field, (pos_x, pos_y))
            pos_x += height
            if row%10 == 0:
                pos_y += height
                pos_x = 0
            row += 1

    def draw_pieces(pos):    
        Game.draw_board(Game.board)
        uni_pieces = {'R':white_rook, 'N':white_knight, 'B':white_bishop, 'Q':white_queen, 'K':white_king, 'P':white_pawn,
                    'r':black_rook, 'n':black_knight, 'b':black_bishop, 'q':black_queen, 'k':black_king, 'p':black_pawn, '.':empty_field}
        pos_x = height
        pos_y = height
        for i, row in enumerate(pos.board.split()):
            for p in row:
                piece = uni_pieces.get(p, p)
                piece.get_rect(center=(width/2, height/2))
                WIN.blit(piece, (pos_x, pos_y))
                pos_x += height
            pos_x = height
            pos_y += height

    def select_field(position, hist, player):
        Game.reset_board()
        field = sunfish.parse1(position)
        Game.board[field - 10] = "s"
        Game.draw_board(Game.board)
        if player == 1:
            Game.draw_pieces(hist[-1]) 
        elif player == 2:
            Game.draw_pieces(hist[-1].rotate())
        pygame.display.update()

    def reset_board():
        Game.board = [  'FP',  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'FP',       # 0-9
                        '8',   'b', 'w', 'b', 'w', 'b', 'w', 'b', 'w', '8',        # 10-19
                        '7',   'w', 'b', 'w', 'b', 'w', 'b', 'w', 'b', '7',        # 20-29
                        '6',   'b', 'w', 'b', 'w', 'b', 'w', 'b', 'w', '6',        # 30-39
                        '5',   'w', 'b', 'w', 'b', 'w', 'b', 'w', 'b', '5',        # 40-49
                        '4',   'b', 'w', 'b', 'w', 'b', 'w', 'b', 'w', '4',        # 50-59
                        '3',   'w', 'b', 'w', 'b', 'w', 'b', 'w', 'b', '3',        # 60-69
                        '2',   'b', 'w', 'b', 'w', 'b', 'w', 'b', 'w', '2',        # 70-79
                        '1',   'w', 'b', 'w', 'b', 'w', 'b', 'w', 'b', '1',        # 80-89
                        'FP',  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'FP'        # 90-99
                    ]

    def player_move(player, hist, hist_moves):
        # We query the user until she enters a (pseudo) legal move.
        move = None

        pygame.display.update()       
        while move not in hist[-1].gen_moves():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        match1 = re.match('([a-h][1-8])', (str(speech.get_pos(1, player, hist))))
                        if match1:
                            match2 = re.match('([a-h][1-8])', (str(speech.get_pos(2, player, hist))))
                        if match1 and match2:
                            if player == 1:
                                move = sunfish.parse1(match1.group(1)), sunfish.parse1(match2.group(1))

                            elif player == 2:
                                move = sunfish.parse2(match1.group(1)), sunfish.parse2(match2.group(1))
                
                            if speech.confirm(str(match1.group(1)) + str(match2.group(1))) == 0:
                                 hist.append(hist[-1].move(move))
                                 hist_moves.append((str(match1.group(1))+str(match2.group(1))).upper())
                            else:
                                Game.display_text('Odrzucono ruch')
                                Game.player_move(player, hist, hist_moves)
                                Game.display_history("HISTORIA TO JEST")

                        else:
                            #Inform the user when invalid input (e.g. "help") is entered
                            Game.display_text("Podaj poprawny ruch np. d2d4")
                            Game.display_history("HISTORIA TO JEST")
        print(hist)

    def engine_move(searcher, hist, hist_moves):
        Game.display_text("Ruch silnika")
        Game.display_history("HISTORIA TO JEST")
        # Fire up the engine to look for a move.
        start = time.time()
        for _depth, move, score in searcher.search(hist[-1], hist):
            if time.time() - start > 1:
                break

        if score == sunfish.MATE_UPPER:
            Game.display_text("Szach-mat!")
            Game.display_history("HISTORIA TO JEST")
        # The black player moves from a rotated position, so we have to
        # 'back rotate' the move before printing it.        
        # print("Mój ruch:", sunfish.render(119-move[0]) + sunfish.render(119-move[1]))
        text = sunfish.render(119-move[0]) + sunfish.render(119-move[1])    
        hist_moves.append(text.upper())
        Game.display_text(f"Mój ruch: {text}")
        Game.display_history("HISTORIA TO JEST")
        hist.append(hist[-1].move(move))

    def check_checkmate(hist, player, run):
        if hist[-1].score <= -sunfish.MATE_LOWER:
            Game.display_text(f"Gracz {player} wygrał")
            Game.display_history("HISTORIA TO JEST")
            time.sleep(5)
            run = False

    def main(players):
        
        clock = pygame.time.Clock()
        run = True
        hist = [sunfish.Position(sunfish.initial, 0, (True,True), (True,True), 0, 0)]
        searcher = compressed.Searcher()
        start_text = "Spacja aby rozpoczac"
        hist_moves = []

        while run:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit()
                
                Game.draw_pieces(hist[-1])            
                pygame.display.update()
                pygame.event.poll()
                if hist[-1].score <= -sunfish.MATE_LOWER:
                    Game.display_text("Przegrałeś")
                    Game.display_history("HISTORIA TO JEST")
                    run = False
                
                if players == 1:
                    Game.display_text(start_text)
                    Game.display_history("HISTORIA TO JEST")
                    Game.player_move(1, hist, hist_moves)
                    Game.draw_pieces(hist[-1].rotate())            
                    pygame.display.update()
                    pygame.event.poll()
                    Game.display_history("HISTORIA TO JEST")
                    Game.engine_move(searcher, hist, hist_moves)

                if players == 2:
                    player = 1
                    Game.display_text(start_text)
                    Game.display_history("hist")
                    Game.player_move(player, hist, hist_moves)
                    Game.draw_pieces(hist[-1].rotate())
                    Game.check_checkmate(hist, player, run)          
                    pygame.display.update()
                    pygame.event.poll()

                    player = 2
                    Game.display_text(start_text)
                    Game.display_history("HISTORIA TO JEST")
                    Game.player_move(player, hist, hist_moves)
                    Game.draw_pieces(hist[-1].rotate())
                    Game.check_checkmate(hist, player, run)          
                    pygame.display.update()
                    pygame.event.poll()

                    # After our move we rotate the board and print it again.
                    # This allows us to see the effect of our move.           
        pygame.quit()


if __name__ == '__main__':
    Menu.draw_menu()