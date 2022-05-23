from time import sleep
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

def get_pos(number, player, hist):
    # while True:
        with sr.Microphone() as source:
            try:
                if number == 1:
                    text = f"Gracz {player} podaj pozycję początkową: "
                    game.Game.display_text(text)
                    game.Game.display_history("HISTORIA TO JEST")
                elif number == 2:
                    text = f"Gracz {player} podaj pozycję docelową"
                    game.Game.display_text(text)
                    game.Game.display_history("HISTORIA TO JEST")
                audio = r.listen(source, timeout=5)
                text = r.recognize_google(audio, language='pl-PL')
                if text != "":
                    check_val = checkChar(text)
                    if check_val == 0:
                        game.Game.select_field(text.lower(), hist, player)
                        return str(text).lower()
                    elif check_val == 1:
                        text = "Nie ma takiego pola!"
                        game.Game.display_text(text)
                        game.Game.display_history("HISTORIA TO JEST")

                    elif check_val == 2:
                        text = "Źle wprowadzona komenda - za długa!"
                        game.Game.display_text(text)
                        game.Game.display_history("HISTORIA TO JEST")
                # continue
            except:
                text = "Nie udało się wprowadzić polecenia"
                game.Game.display_text(text)
                game.Game.display_history("HISTORIA TO JEST")
                # continue

def confirm(move):
    while True:
        with sr.Microphone() as source:
            try:
                game.Game.display_text(f"Czy potwierdzasz wprowadzoną pozycję: {move}?")
                game.Game.display_history("HISTORIA TO JEST")
                audio = r.listen(source, timeout=5)
                text = r.recognize_google(audio, language='pl-PL')
                if text != "":
                    if text == "tak" or text == "Tak" or text == "TAK":
                        return 0
                    elif text == "nie" or text == "Nie" or text == "NIE":
                        return 1
            except:
                game.Game.display_text("Nie udało się wprowadzić potwierdzenia")
                game.Game.display_history("HISTORIA TO JEST")
                continue

if __name__ == "__main__":
    confirm("dupa")
