import speech_recognition as sr

r = sr.Recognizer()

##Funkcja pobierajaca dzwiek i zamieniajaca go na tekst
def toText():
    with sr.Microphone() as source:
        try:
            print("Podaj pozycję początkową i docelową")
            audio = r.listen(source)
            text = r.recognize_google(audio, language='pl-PL')
            if text != "":
                return text
            return 1
        except:
            print("Nie udało się wprowadzić polecenia")
            return 2


def get_input():
    field_name_letters = ("A","a","B","b","C","c","D","d","E","e","F","f","G","g","H","h")
    field_name_numbers = ("1","2","3","4","5","6","7","8")
    txt = None
    while True:
        txt = toText()
        if not txt == 0:
            print(txt)
            break
        else:
            print("Mowa niezrozumiała")
            continue
    length = len(txt)
    ## Sprawdzanie wprowadzonego polecenia wg kryteriów
    if length == 5:
        if (txt[0] and txt[3] in field_name_letters) and (txt[1] and txt[4] in field_name_numbers):
            sun_command = txt[0]+txt[1]+txt[3]+txt[4]
            print(sun_command)
            return sun_command
        else:
            print("Nie ma takich pól!")
    else:
        print("Źle wprowadzona komenda")
        return 3

if __name__ == "__main__":
    get_input()