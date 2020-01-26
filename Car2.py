import pygame
import numpy as np


# Klasa dla pojazdu z dwoma czujnikami

class Car2(pygame.sprite.Sprite):
    posX = 100  # pozycja X sprita
    posY = 100  # pozycja Y sprita
    angle = 0  # kąt o jaki obrócony jest robot
    detColor = (255, 159, 0, 255)  # kolor obudowy czujnika

    forward_pow = 2  # domyślna wartość dla jazdy naprzód
    rot_pow = 4  # domyślna wartośc dla skrętu
    vectorDir = (0.0, -1.0)  # wektor kierunku

    vectorDet1 = (-9.0, -23.0)  # wektor od centrum sprita do punktu1 "pomiaru"
    vectorDet2 = (8.0, -23.0)  # wektor od centrum sprita do punktu1 "pomiaru"
    startPos = (-20, 0)

    left = False  # flaga dla lewego i prawego czujnika
    right = False

    def __init__(self):  # inicjowanie
        pygame.sprite.Sprite.__init__(self)
        self.posX = 0
        self.posY = 0
        self.angle = 0
        self.image = pygame.image.load("images/lineFol2.png")
        self.orginal_image = self.image
        self.rect = self.image.get_rect()

    def draw(self, screen):  # rysowanie robota
        screen.blit(self.image, (self.posX, self.posY))

    def rot(self, angle):  # obrót robota o kąt, wyznaczenie nowego wektora kierunki i jego normalizacja
        self.angle += angle
        self.angle = self.angle % 360
        self.dirVector_normalize()
        self.image = pygame.transform.rotate(self.orginal_image, self.angle)
        self.rect = self.image.get_rect()

    def update(self):  # metoda klasy sprite
        self.rot(0)
        pass

    # przesunięcie robota o zadaną wartość "power", zgodnie z kierunkiem,
    # power > 0  - do przodu
    # power < 0  - do tyłu
    def forward(self, power):
        x, y = self.vectorDir
        self.posY += y * power
        self.posX += x * power

    # zwrcanie koloru w miejscu "pomiaru" z poprawką (i,j) - wynikającą z przybliżeń
    def detecColorL(self, screen, i, j):
        a, b = self.rect.center
        x, y = self.vectorDet1
        p, q = self.rotate_point((x + i, y + j))
        color = screen.get_at((int(self.posX + int(a + p)), int(self.posY + int(b + q))))
        return color

    def detecColorR(self, screen, i, j):
        a, b = self.rect.center
        x, y = self.vectorDet2
        p, q = self.rotate_point((x + i, y + j))
        color = screen.get_at((int(self.posX + int(a + p)), int(self.posY + int(b + q))))
        return color

    #obroty obrazka sprawiają że kolor interpoluje i nie jest dokładnie taki jak ustawiono na początku
    # kolor uznaję za "taki sam" jeżeli różnica składowych jest mniejsza niż 20
    #w celu uniknięcia pomyłek wybrałem wyraźiste jaskrawe kolory
    def colorSimilar(self, colorA, colorB):
        r, g, b,a= colorA
        x, y, z,a = colorB
        d = np.abs(r - x) + np.abs(g - y) + np.abs(b - z)
        return d < 20

    # zwracanie zmierzonego koloru, z poprawką na pomiar koloru z robota
    def colorDetectorR(self, screen):
        color = self.detecColorR(screen, 0, 0)
        if color == self.detColor:
            color = self.detecColorR(screen, 0, 1)
            if color == self.detColor:
                color = self.detecColorR(screen, 1, 1)
                if color == self.detColor:
                    color = self.detecColorR(screen, 1, 0)
        return color

    # zwracanie zmierzonego koloru, z poprawką na pomiar koloru z robota
    def colorDetectorL(self, screen):
        color = self.detecColorL(screen, 0, 0)
        if color == self.detColor:
            color = self.detecColorL(screen, 0, 1)
        return color

    # tworzenie nowego wektora, tworzymy nowy a nie transformujemy porpzedni żeby zniwelować efekt zaokrągleń
    def dirVector_normalize(self):
        x, y = (0, -1)
        xp = x * np.cos(np.deg2rad(-self.angle)) - y * np.sin(np.deg2rad(-self.angle))
        yp = x * np.sin(np.deg2rad(-self.angle)) + y * np.cos(np.deg2rad(-self.angle))
        d = np.sqrt(xp * xp + yp * yp)
        xp = xp / d
        yp = yp / d
        self.vectorDir = (xp, yp)

    # wyznaczenie pozycji punktu pomiaru
    def rotate_point(self, vec):
        x, y = vec
        xp = x * np.cos(np.deg2rad(-self.angle)) - y * np.sin(np.deg2rad(-self.angle))
        yp = x * np.sin(np.deg2rad(-self.angle)) + y * np.cos(np.deg2rad(-self.angle))
        return xp, yp

    # algorytm śledzenia linij
    def folow(self, screen, line_color, end_color, background_c):
        colorL = self.colorDetectorL(screen)
        colorR = self.colorDetectorR(screen)

        left = self.colorSimilar(line_color, colorL)
        right = self.colorSimilar(line_color, colorR)
        end = self.colorSimilar(end_color,colorR) or self.colorSimilar(end_color,colorL)
        #pygame.draw.rect(screen, colorL, pygame.Rect(500, 0, 50, 50))
        #pygame.draw.rect(screen, colorR, pygame.Rect(550, 0, 50, 50))

        if not end:
            if right and left:
                self.forward(self.forward_pow)

            if not right and not left:
                self.forward(self.forward_pow)

            if right and not left:
                self.forward(self.forward_pow / 2)
                self.rot(-self.rot_pow)

            if left and not right:
                self.forward(self.forward_pow / 2)
                self.rot(self.rot_pow)

            return False
        else:
            return True

    def print(self, screen):
        colorL = self.colorDetectorL(screen)
        colorR = self.colorDetectorR(screen)
        r, g, b, a = colorL
        print("L: [ " + str(r) + " , " + str(g) + " , " + str(b) + " , " + str(a) + " ]")
        r, g, b, a = colorR
        print("R: [ " + str(r) + " , " + str(g) + " , " + str(b) + " , " + str(a) + " ]")
