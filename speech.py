import speech_recognition as sr
import pygame

import game

r = sr.Recognizer()
r.dynamic_energy_threshold = False

##Funkcja pobierajaca dzwiek i zamieniajaca go na tekst
def checkChar(txt):
    field_name_letters = ("A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h")
    field_name_numbers = ("1", "2", "3", "4", "5", "6", "7", "8")
    if not txt == 0:
        print(txt)
    else:
        print("Mowa niezrozumiała")

    ## Sprawdzanie wprowadzonego polecenia wg kryteriów
    if len(txt) == 2:
        if (txt[0] in field_name_letters) and (txt[1] in field_name_numbers):
            return 0
        else:
            return 1
    else:
        return 2

def get_pos(number):
    while True:
        with sr.Microphone() as source:
            try:
                if number == 1:
                    print("Podaj pozycję początkową: ")
                    text = "Podaj pozycję początkową: "
                    game.Game.display_text(text)
                elif number == 2:
                    print("Podaj pozycję docelową: ")
                    text = "Podaj pozycję doeclową"
                    game.Game.display_text(text)
                audio = r.listen(source, timeout=2)
                text = r.recognize_google(audio, language='pl-PL')
                if text != "":
                    check_val = checkChar(text)
                    if check_val == 0:
                        # game.Game.select_field(text.lower())
                        # if confirm(text) == 0:
                            # game.Game.reset_board()
                        return str(text).lower()
                        # elif confirm(text) == 1:
                            # get_pos(number)
                    elif check_val == 1:
                        print("Nie ma takiego pola!")
                        text = "Nie ma takiego pola!"
                        game.Game.display_text(text)

                        #if game.event.get(game.keyboard.push):
                           #return(print("Wpisz pozycje na klawiaturze"))
                    elif check_val == 2:
                        print("Źle wprowadzona komenda - za długa!")
                        text = "Źle wprowadzona komenda - za długa!"
                        game.Game.display_text(text)
                continue
            except:
                print("Nie udało się wprowadzić polecenia")
                text = "Nie udało się wprowadzić polecenia"
                game.Game.display_text(text)
                continue

def confirm(text):
    while True:
        with sr.Microphone() as source:
            try:
                #game.Game.select_field(text.lower())
                print("Czy potwierdzasz wprowadzaoną pozycję?: ", text)
                audio = r.listen(source, timeout=5)
                text = r.recognize_google(audio, language='pl-PL')
                if text != "":
                    if len(text) == 3:
                        if text == "tak" or text == "Tak" or text == "TAK":
                            return 0
                        elif text == "nie" or text == "Nie" or text == "NIE":
                            return 1
            except:
                print("Nie udało się wprowadzić potwierdzenia")
                return 2

# events = pygame.event.get()
# for event in events:
#     if event.type == pygame.QUIT:
#         exit()
#     # if event.type == pygame.KEYDOWN
if __name__ == "__main__":
    get_pos(1)
    get_pos(2)
