from random import randint

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

class BoardException(Exception):
    pass
class OutException(BoardException):
    def __str__(self):
        return "Мимо доски"
class UsedException(BoardException):
    def __str__(self):
        return "Вы сюда уже стреляли"
class WrongShipException(BoardException):
    pass

class Ship:
    def __init__(self, stem, length, bearings):
        self.stem = stem
        self.length = length
        self.bearings = bearings
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            current_x = self.stem.x
            current_y = self.stem.y
            if self.bearings == 0:
                current_x += i
            elif self.bearings == 1:
                current_y += i
            ship_dots.append(Dot(current_x, current_y))
        return ship_dots
    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, dodge = False, size = 6):
        self.size = size
        self.dodge = dodge

        self.count = 0
        self.field = [[" "] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise WrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                current = Dot(d.x + dx, d.y + dy)
                if not (self.out(current)) and current not in self.busy:
                    if verb:
                        self.field[current.x][current.y] = "•"
                    self.busy.append(current)

    def __str__(self):
        res = ""
        res += "  | A | B | C | D | F | G |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
        if self.dodge:
            res = res.replace('■', " ")
        return res
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise OutException()
        if d in self.busy:
            raise UsedException()
        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Убит")
                    return False
                else:
                    print("Попал")
                    return True
        self.field[d.x][d.y] = "•"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

class Player:
    def __init__(self, board, opponent):
        self.board = board
        self.opponent = opponent
    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.opponent.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Компьютер: {d.x + 1} {d.y + 1}")
        return d

class User(Player):
    def ask(self):
        while True:
            index = {"A": 1, "B": 2, "C": 3, "D": 4, "F": 5, "G":  6}
            cords = input("Ход игрока. Введите координаты - ").split()
            cords[1] = cords[1].upper()
            if len(cords) != 2:
                print("Введите координаты (x,y)")
                continue
            x, y = cords[0], cords[1]

            if not(x.isdigit()) or not(y.isalpha()):
                print("Введите цифру и букву")
                continue
            x, y = int(x), int(index[cords[1]])
            return Dot(x - 1, y - 1)
class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.dodge = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for length in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except WrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("/" * 50)
        print("""\t\t ИГРА: Морской бой
        Введите координаты:
             Х - номер строки
             У - номер столбца""")
        print("/" * 50)

    def loop(self):
        num = 0
        while True:
            print("/" * 50)
            print("\t\t\tИгрок:")
            print(self.us.board)
            print("/" * 50)
            print("\t\t\tКомпьютер: ")
            print(self.ai.board)
            print("/" * 50)
            if num % 2 == 0:
                print("ход игрока")
                repeat = self.us.move()
            else:
                print("ход компьютера")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == 7:
                print("/" * 50)
                print("Ты выиграл")
                print("/" * 50)
                break
            if self.us.board.count == 7:
                print("/" * 50)
                print("Ты проиграл")
                print("/" * 50)
                break
            num += 1
    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()