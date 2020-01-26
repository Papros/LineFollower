import pygame
import numpy as np


class Car(pygame.sprite.Sprite):
    posX = 100  # pozycja X sprita
    posY = 100  # pozycja Y sprita
    angle = 0  # kąt o jaki obrócony jest robot
    detColor = (255, 160, 1, 255)  # kolor obudowy czujnika
    vectorDir = (0.0, -1.0)  # wektor kierunku
    onLine = False  # "flaga" czy robot znajduje się na linij
    vectorDet = (0.0, -23.0)  # wektor od centrum sprita do punktu "pomiaru"
    startPos = (-20, -7)

    def __init__(self):  # inicjowanie
        pygame.sprite.Sprite.__init__(self)
        self.posX = 0
        self.posY = 0
        self.angle = 0
        self.image = pygame.image.load("images/lineFol.png")
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
        self.rotate_point()
        pass

    # przesunięcie robota o zadaną wartość "power", zgodnie z kierunkiem,
    # power > 0  - do przodu
    # power < 0  - do tyłu
    def forward(self, power):
        x, y = self.vectorDir
        self.posY += y * power
        self.posX += x * power

    # zwrcanie koloru w miejscu "pomiaru" z poprawką (i,j) - wynikającą z przybliżeń
    def detecColor(self, screen, i, j):
        a, b = self.rect.center
        p, q = self.vectorDet
        color = screen.get_at((int(self.posX + int(a + p)) + i, int(self.posY + int(b + q)) + j))
        return color

    # zwracanie zmierzonego koloru, z popraką na pomiar koloru z robota
    def colorDetector(self, screen):
        color = self.detecColor(screen, 0, 0)
        if color == self.detColor:
            color = self.detecColor(screen, 0, 1)
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
    def rotate_point(self):
        x, y = (0, -23)
        xp = x * np.cos(np.deg2rad(-self.angle)) - y * np.sin(np.deg2rad(-self.angle))
        yp = x * np.sin(np.deg2rad(-self.angle)) + y * np.cos(np.deg2rad(-self.angle))
        self.vectorDet = (xp, yp)

    # proste sterowanie algorytmem śledzenia krawędzi linij
    def folow(self, screen, line_color, end_color, background_c):
        color = self.colorDetector(screen)
        forward_pow = 3
        rot_pow = 3

        if (color != end_color):

            if color == background_c and self.onLine:
                self.onLine = False
            else:
                if color == line_color and not self.onLine:
                    self.onLine = True

            if self.onLine:
                self.forward(forward_pow)
                self.rot(-rot_pow)
            else:
                self.forward(forward_pow)
                self.rot(rot_pow)
            return False
        else:
            return True

    def print(self, screen):
        color = self.colorDetector(screen)
        print("col:" + color)