from SeaBattle import *

def main():
    sb = SeaBattle()
    print(sb.commandOrganizer("/info"))
    while True:
        mes = sb.commandOrganizer(input())
        print(mes)
        if mes == "Ты победил! Поздравляю!" or mes == "Бот победил!":
            break

if __name__ == '__main__':
    main()