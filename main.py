from random import randint


class GameException(Exception):
    pass


class UsedException(GameException):
    def __str__(self):
        return "Вы уже стреляли в эту точку, повторите попытку"


class ExitException(GameException):
    def __str__(self):
        return "Выход за пределы поля, повторите попытку"


class WrongShipException(GameException):
    pass


class Dot:  # класс точек
    def __init__(self, x, y):
        self.y = y
        self.x = x

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


class Ship:  # класс корабля
    def __init__(self, long, start_point, direct):
        self.long = long
        self.start_point = start_point
        self.life = long
        self.direct = direct

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.long):
            new_x = self.start_point.x
            new_y = self.start_point.y

            if self.direct == 0:
                new_x += i

            elif self.direct == 1:
                new_y += i

            ship_dots.append(Dot(new_x, new_y))

        return ship_dots

    def shoot(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size

        self.ships = []  # корабли на поле
        self.points = [["O"] * size for i in range(size)]
        self.value = 0  # количество поражённых кораблей
        self.busy = []  # количество занятых точек

    def __str__(self):
        board = " |"
        for i in range(0, self.size + 1):
            board += f" {i} |"
        for i, j in enumerate(self.points):
            board += f"\n | {i + 1} | " + " | ".join(j) + " |"

        if self.hid:
            board = board.replace("■", "0")
        return board

    def out(self, a):
        return not ((0 <= a.x < self.size) and (0 <= a.y < self.size))

    def contour(self, ship, flag=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for m in ship.dots:
            for x, y in near:
                new = Dot(m.x + x, m.y + y)
                if not (self.out(new)) and new not in self.busy:
                    if flag:
                        self.points[new.x][new.y] = "."
                    self.busy.append(new)

    def add_ship(self, ship):
        for i in ship.dots:
            if self.out(i) or i in self.busy:
                raise WrongShipException()
        for i in ship.dots:
            self.points[i.x][i.y] = "■"
            self.busy.append(i)
        self.ships.append(ship)
        self.contour(ship)

    def shoot(self, a):
        if a in self.busy:
            raise UsedException()
        if self.out(a):
            raise ExitException()
        self.busy.append(a)

        for sh in self.ships:
            if a in sh.dots:
                sh.life -= 1
                self.points[a.x][a.y] = "X"
                if sh.life == 0:
                    self.value += 1
                    self.contour(sh, flag=True)
                    print("Корабль уничтожен")
                    return False
                else:
                    print("Есть пробитие")
                    return True
        self.points[a.x][a.y] = '.'
        print("Промах")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                step1 = self.ask()
                step2 = self.enemy_board.shoot(step1)
                return step2
            except GameException as e:
                print(e)


class AI(Player):
    def ask(self):
        a = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера:({a.x + 1},{a.y + 1})")
        return a


class User(Player):
    def ask(self):
        print(f"Введите поочерёдно координаты точки:")
        while True:
            x = input()
            y = input()
            if not (x.isdigit()) or not (y.isdigit()):
                print("Это не числа, повторите ход.")
                continue
            if len(x) != 1 or len(y) != 1:
                print("Нужно однозначное число от 1 до 6!, повторите ход")
                continue
            return Dot(int(x) - 1, int(y) - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        user_board = self.random_board()
        ai_board = self.random_board()
        ai_board.hid = True

        self.ai = AI(ai_board, user_board)
        self.user = User(user_board, ai_board)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for i in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(i, Dot(randint(0, self.size), randint(0, self.size)), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except WrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("Добро пожаловать в игру: Морской бой!")
        print("Вводите поочерёдно через Enter номер столбца и номер строки")

    def loop(self):
        num = 0
        while True:
            print("✿" * 20)
            print("Доска пользователя:")
            print(self.user.board)
            print("✿" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("✿" * 20)
                print("Ходит пользователь!")
                repeat = self.user.move()
            else:
                print("✿" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.value == 7:
                print("✿" * 20)
                print("Пользователь выиграл💪!")
                break

            if self.user.board.value == 7:
                print("✿" * 20)
                print("Компьютер выиграл💀💀💀!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
