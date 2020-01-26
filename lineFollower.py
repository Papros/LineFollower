# Źródła użyte do przygotowania programu
# https://forbot.pl/forum/topic/3723-algorytmy-pid-w-robotyce-amatorskiej-linefollower-cz1-czlon-p/
#
# Opis budowy robotów LF
# https://forbot.pl/blog/kurs-budowy-robotow-line-follower-czyli-bolid-f1-id19363
#
#   Sterowanie:
#   Naciśniecię myszy spowoduje rozpoczęcie rysowania linij, zwolnienie przycisku automatycznie ustawi robota na starcie i uruchomi go
#   robotem można sterować też za pomocą strzałek
#   Klawisze 1,2,3 zmieniają typ robota
#   1 - robot z algorytmem śledzenia krawędzi, i jednym detektorem
#   2 - robot z algorytmem śledzenia linij i dwoma detektorami
#   3 - robot z algorytmem PD steerowania linij i 7 detektorami



import pygame
from Car import Car
from Car2 import Car2
from Car3 import Car3

pygame.init()
screen = pygame.display.set_mode((600, 600))
done = False  # flaga sygnalizująca zamknięcie programu
drawing = False  # flaga sprawdzająca czy linia jest rysowana
line_pos = list()  # lista zawierająca pozycję rysowanej linii
line_color = (255, 0, 0,255)  # color rysowanej linij,
background_c = (200, 200, 200, 255)  # kolor tła
start_c = (150, 150, 150, 255)  # kolor pola startowewgo
end_color = (100, 255, 100, 255)  # kolor pola mety
car = Car2()  # sprite symbolizujący robota
line_width = 5  # szerokośc linij


def clear_screen():  # metoda rysująca jasnoszare tło ekranu
    screen.fill(background_c)
    pygame.draw.rect(screen, start_c, pygame.Rect(0, 550, 50, 50))


def reset_line():  # resetowanie linii
    line_pos.clear()


def draw_line():  # rysowanie linii
    if len(line_pos) > 1:
        pygame.draw.lines(screen, line_color, False, line_pos, line_width)
        x, y = line_pos[len(line_pos) - 1]
        pygame.draw.rect(screen, end_color, pygame.Rect(x, y, 10, 10))


clock = pygame.time.Clock()
start = False
while not done:  # pętla główna programu

    # pętla zdarzeń wychwyconych przez okno programu
    for event in pygame.event.get():

        if event.type == pygame.QUIT:  # zamkniącie programu
            done = True

        if event.type == pygame.MOUSEBUTTONDOWN:  # wciśnięcie klawisza myszy, rozpoczęcie rysowania linij
            reset_line()
            drawing = True
            pygame.mouse.set_pos(25, 550)
            start = False

        if event.type == pygame.MOUSEMOTION and drawing:  # poruszanie myszą przy wciśniętym klawiszu, rysowanie linij
            line_pos.append(pygame.mouse.get_pos())

        if event.type == pygame.MOUSEBUTTONUP:  # zwolnienie klawisza, zakończenie rysowania
            drawing = False
            x, y = line_pos[0]
            a, b = car.startPos
            car.posX, car.posY = x + a, y + b
            car.angle = 0
            start = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                car.rot(-10)
            if event.key == pygame.K_LEFT:
                car.rot(10)
            if event.key == pygame.K_UP:
                car.forward(10)
            if event.key == pygame.K_DOWN:
                car.forward(-10)
            if event.key == pygame.K_1:
                car = Car()
                line_width = 10
                start = False
            if event.key == pygame.K_2:
                car = Car2()
                line_width = 5
                start = False
            if event.key == pygame.K_3:
                car = Car3()
                line_width = 5
                start = False


    # ============================

    clear_screen()
    draw_line()
    car.draw(screen)
    if start:
        start = not car.folow(screen, line_color, end_color, background_c)
    pygame.display.flip()
    car.update()

    clock.tick(50)

# ============================
