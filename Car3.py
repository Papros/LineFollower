import pygame
import numpy as np


# Klasa dla pojazdu z dwoma czujnikami

class Car3(pygame.sprite.Sprite):
    posX = 100  # pozycja X sprita
    posY = 100  # pozycja Y sprita
    angle = 0  # kąt o jaki obrócony jest robot
    detColor = (255, 159, 0, 255)  # kolor obudowy czujnika

    DefoultPow = 4  # domyślna wartość dla jazdy naprzód
    PIDratio = 5  # domyślna wartośc dla skrętu

    vectorDir = (0.0, -1.0)  # wektor kierunku

    vectorDet1 = (-18.0, -19.0)  # wektor od centrum sprita do punktu1 "pomiaru"
    vectorDet2 = (-14.0, -23.0)  # wektor od centrum sprita do punktu2 "pomiaru"
    vectorDet3 = (-8.0, -25.0)  # wektor od centrum sprita do punktu3 "pomiaru"
    vectorDet4 = (-1.0, -27.0)  # wektor od centrum sprita do punktu4 "pomiaru"
    vectorDet5 = (7.0, -25.0)  # wektor od centrum sprita do punktu5 "pomiaru"
    vectorDet6 = (13.0, -23.0)  # wektor od centrum sprita do punktu6 "pomiaru"
    vectorDet7 = (17.0, -19.0)  # wektor od centrum sprita do punktu7 "pomiaru"

    idAct = 0
    idLast = 0

    startPos = (-20, 0)

    def __init__(self):  # inicjowanie
        pygame.sprite.Sprite.__init__(self)
        self.posX = 0
        self.posY = 0
        self.angle = 0
        self.image = pygame.image.load("images/lineFol7.png")
        self.orginal_image = self.image
        self.rect = self.image.get_rect()

    def draw(self, screen):  # rysowanie robota
        screen.blit(self.image, (self.posX, self.posY))


    def drawDot(self, vector, screen):
        a, b = self.rect.center
        x, y = self.rotate_point(vector)
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(a + x, b + y, 2, 2))

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
    def detecColor(self, screen, vector, i, j):
        a, b = self.rect.center
        x, y = vector
        p, q = self.rotate_point((x + i, y + j))
        color = screen.get_at((int(self.posX + int(a + p)), int(self.posY + int(b + q))))
        return color

    # obroty obrazka sprawiają że kolor interpoluje i nie jest dokładnie taki jak ustawiono na początku
    # kolor uznaję za "taki sam" jeżeli różnica składowych jest mniejsza niż 20
    # w celu uniknięcia pomyłek wybrałem wyraźiste jaskrawe kolory
    def colorSimilar(self, colorA, colorB):
        r, g, b, a = colorA
        x, y, z, a = colorB
        d = np.abs(r - x) + np.abs(g - y) + np.abs(b - z)
        return d < 20

    # zwracanie zmierzonego koloru, z poprawką na pomiar koloru z robota
    def colorDetector(self, screen, vector):
        color = self.detecColor(screen, vector, 0, 0)
        if self.colorSimilar(color,self.detColor):
            color = self.detecColor(screen, vector, 0, 1)
            if self.colorSimilar(color,self.detColor):
                color = self.detecColor(screen, vector, 1, 1)
                if self.colorSimilar(color,self.detColor):
                    color = self.detecColor(screen, vector, 1, 0)
                    if self.colorSimilar(color, self.detColor):
                        color = self.detecColor(screen, vector, 1, -1)
                        if self.colorSimilar(color, self.detColor):
                            color = self.detecColor(screen, vector, 0, -1)
                            if self.colorSimilar(color, self.detColor):
                                color = self.detecColor(screen, vector, -1, -1)
                                if self.colorSimilar(color, self.detColor):
                                    color = self.detecColor(screen, vector, -1, 0)
                                    if self.colorSimilar(color, self.detColor):
                                        color = self.detecColor(screen, vector, -1, -1)
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

        if not self.searchEnd(end_color, screen):

            zmiana = self.PIDratio * self.calcError(line_color, screen)
            self.forward(self.DefoultPow)
            self.rot(zmiana)
            return False
        else:
            return True

    def print(self, screen):
        pass

    def searchEnd(self, color_end, screen):
        color = list()
        color.append(self.colorSimilar(color_end, self.colorDetector(screen, self.vectorDet1)))
        color.append(self.colorSimilar(color_end, self.colorDetector(screen, self.vectorDet2)))
        color.append(self.colorSimilar(color_end, self.colorDetector(screen, self.vectorDet3)))
        color.append(self.colorSimilar(color_end, self.colorDetector(screen, self.vectorDet4)))
        color.append(self.colorSimilar(color_end, self.colorDetector(screen, self.vectorDet5)))
        color.append(self.colorSimilar(color_end, self.colorDetector(screen, self.vectorDet6)))
        color.append(self.colorSimilar(color_end, self.colorDetector(screen, self.vectorDet7)))

        for i in range(0, 6):
            if color[i]:
                return True

        return False

    def calcError(self, lineColor, screen):
        color = list()
        color.append(self.colorSimilar(lineColor, self.colorDetector(screen, self.vectorDet1)))
        color.append(self.colorSimilar(lineColor, self.colorDetector(screen, self.vectorDet2)))
        color.append(self.colorSimilar(lineColor, self.colorDetector(screen, self.vectorDet3)))
        color.append(self.colorSimilar(lineColor, self.colorDetector(screen, self.vectorDet4)))
        color.append(self.colorSimilar(lineColor, self.colorDetector(screen, self.vectorDet5)))
        color.append(self.colorSimilar(lineColor, self.colorDetector(screen, self.vectorDet6)))
        color.append(self.colorSimilar(lineColor, self.colorDetector(screen, self.vectorDet7)))

        odczytanych = 0
        sumaWag = 0

        for i in range(0, 6):
            if color[i]:
                sumaWag += i - 3
                odczytanych += 1
        if odczytanych > 0:
            error = sumaWag / odczytanych
        else:
            error = 0
        return -error
