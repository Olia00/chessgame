import speech_recognition as sr
from pynput import keyboard
import pygame as game

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

    length = len(txt)
    ## Sprawdzanie wprowadzonego polecenia wg kryteriów
    if length == 2:
        if (txt[0] in field_name_letters) and (txt[1] in field_name_numbers):
            return 0
        else:
            return 1
    else:
        return 2

def toText():
    while True:
        with sr.Microphone() as source:
            try:
                print("Podaj pozycję początkową")
                audio = r.listen(source, timeout=5)
                text = r.recognize_google(audio, language='pl-PL')
                if text != "":
                    check_val = checkChar(text)
                    if check_val == 0:
                        return text
                    elif check_val == 1:
                        print("Nie ma takiego pola!")
                        #if game.event.get(game.keyboard.push):
                           #return(print("Wpisz pozycje na klawiaturze"))
                    elif check_val == 2:
                        print("Źle wprowadzona komenda - za długa!")
                continue
            except:
                print("Nie udało się wprowadzić polecenia")
                continue


def get_input():
    txt = toText()


if __name__ == "__main__":
    get_input()