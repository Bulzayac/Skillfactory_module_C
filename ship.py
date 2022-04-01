# был спортивный интерес сделать всё самому, минимально опираясь на подсказки в задании и разбор, поэтому исполнение
# будет слегка отличаться от логики, прописанной в задании, но все условия игры были соблюдены

from random import randint
import copy  # deepcopy понадобится для создания доски компьютера


class Dot:  # самая "каноничная" часть
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Dot: ({self.x}, {self.y})'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, x, y, cur, lives):
        self.x = x
        self.y = y
        self.cur = cur
        self.lives = lives
        self.dts = []
        self.contour = []

    def check_ship_dots(self):  # автоматически будем подгонять координаты так, чтобы корабли умещались на нашем поле
        if self.lives == 3 and self.cur == 0 and self.x > 3:
            self.x = 3
        elif self.lives == 3 and self.cur == 1 and self.y > 3:
            self.y = 3
        elif self.lives == 2 and self.cur == 0 and self.x > 4:
            self.x = 4
        elif self.lives == 2 and self.cur == 1 and self.y > 4:
            self.y = 4

    def dots(self):
        if self.cur == 0:
            for i in range(self.lives):
                self.dts.append(Dot(self.x + i, self.y))
        elif self.cur == 1:
            for i in range(self.lives):
                self.dts.append(Dot(self.x, self.y + i))

    def cont(self):
        cntour = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]
        for j in self.dts:
            for i in cntour:
                if (j.x + i[0] >= 0) and (j.y + i[1] >= 0):  # убираем отрицательные индексы, чтобы наш контур не
                    # отрисовывался где не надо, если корабль находится в "нулевых" координатах
                    self.contour.append(Dot(j.x + i[0], j.y + i[1]))

    def represent(self):  # с помощью одной функции наполняем наши списки точками, чтобы потом использовать их для
        # отрисовки на поле и для определения пересечений при наполнении и попаданий непосредственно в игре
        self.check_ship_dots()
        self.dots()
        self.cont()


class Field:
    def __init__(self, size=6, hid=False):
        self.size = size
        self.hid = hid
        self.field = [["O"] * self.size for _ in range(self.size)]
        self.ships_on_field = []  # основной список, через который будет реализовываться логика развёртки и игры
        self.list_len_ships = [3, 2, 2, 1, 1, 1, 1]

    def show(self):
        print(f'  0 1 2 3 4 5')
        num = 0
        if self.hid:
            _ = copy.deepcopy(self.field)  # через глубокую копию будем реализовывать вывод доски компьютера
            for i in _:                    # в то время как "под капотом" у нас останется та же логика, что и у игрока
                while "■" in i:
                    i.insert(i.index("■"), 'O')
                    i.remove("■")
            for i in _:
                print(str(num), '|'.join(i))
                num += 1
        else:
            for i in self.field:
                print(str(num), '|'.join(i))
                num += 1

    def check_deploy(self, ship):
        _ = 0
        for i in ship.dts:
            if self.field[i.x][i.y] == "O":
                _ += 1
        if _ == ship.lives:
            self.deploy(ship)  # отрисовываемся если кол-во пустых клеток совпало с кол-вом жизней корабля
        else:
            return 1  # а если что-то пошло не так, сообщаем об этом другой функции с помощью "костыля"

    def deploy(self, ship):  # непосредственно, отрисовка
        for i in ship.dts:
            self.field[i.x][i.y] = "■"  # корабль за доску не выйдет, тут мы всё учли
        for j in ship.contour:
            try:
                if self.field[j.x][j.y] == "O":
                    self.field[j.x][j.y] = "."
            except IndexError:  # а вот контур может, отлавливаем
                pass

    def clear(self):
        self.field = [["O"] * self.size for _ in range(self.size)]
        self.ships_on_field = []
        self.list_len_ships = [3, 2, 2, 1, 1, 1, 1]

    def deploy_all(self):  # основной алгоритм создания доски. Наверняка можно провести рефакторинг и сократить его
        # вдвое, но уж очень долго я пытался его заставить работать так, как задумывалось
        counter = 0
        ship_index_to_pop = 0
        len_ships_to_pop = []  # сюда закидываем индексы "удачных" кораблей, которые удалось разместить на доске
        wrong_ships_to_pop = []  # а сюда - тех, что не удалось "пихнуть"
        for i in self.list_len_ships:
            self.ships_on_field.append(Ship(randint(0, 5), randint(0, 5), randint(0, 1), i))
            self.ships_on_field[-1].represent()
            if self.check_deploy(self.ships_on_field[-1]) != 1:  # тот самый "костыль"
                len_ships_to_pop.append(ship_index_to_pop)
            else:
                wrong_ships_to_pop.append(ship_index_to_pop)
            ship_index_to_pop += 1
        for i in len_ships_to_pop[::-1]:  # из списка с жизнями кораблей убираем те значения, по которым удалось удачно
            # отрисоваться
            self.list_len_ships.pop(i)
        for i in wrong_ships_to_pop[::-1]:  # а тут из нашего списка кораблей на поле убираем те, у которых
            # отрисоваться не получилось
            self.ships_on_field.pop(i)
        while len(self.list_len_ships) != 0:  # повторяем процесс, пока не кончатся значения в списке с жизнями
            ship_index_to_pop_in_cyc = len(self.ships_on_field)
            len_index_to_pop_in_cyc = 0
            len_ships_to_pop_in_cyc = []
            wrong_ships_to_pop_in_cyc = []
            for i in self.list_len_ships:
                self.ships_on_field.append(Ship(randint(0, 5), randint(0, 5), randint(0, 1), i))
                self.ships_on_field[-1].represent()
                if self.check_deploy(self.ships_on_field[-1]) != 1:
                    len_ships_to_pop_in_cyc.append(len_index_to_pop_in_cyc)
                else:
                    wrong_ships_to_pop_in_cyc.append(ship_index_to_pop_in_cyc)
                ship_index_to_pop_in_cyc += 1
                len_index_to_pop_in_cyc += 1
            for i in len_ships_to_pop_in_cyc[::-1]:
                self.list_len_ships.pop(i)
            for i in wrong_ships_to_pop_in_cyc[::-1]:
                self.ships_on_field.pop(i)
            counter += 1
            if counter == 15:  # если процесс затянулся, всё стираем и пробуем заново
                print('redeploying...')
                self.clear()
                self.deploy_all()

    def start(self):  # перед началом игры убираем отрисовку контуров, которая помогала нам расставлять корабли
        for i in self.field:
            while '.' in i:
                i.insert(i.index('.'), 'O')
                i.remove('.')


class Player:
    def __init__(self, human=True):
        self.human = human
        self.name = "Human" if self.human else "Robot"

    def shoot(self, field, name):  # вводим строку, затем столбец. Если есть попадание, ищем в каком корабле есть
        # точка с такими координатами, отнимаем одну жизнь, если жизней не остаётся, получаем сообщение об
        # уничтожении корабля, удаляем его из списка находящихся на доске. Кто первый опустошит список противника -
        # тот и победил.
        if not self.human:
            print("AI's turn")
            print("")
            x = randint(0, 5)
            y = randint(0, 5)
            print('-------------')
            print(y, x)
        else:
            print("your turn")
            print("")
            field.show()
            y = input("line: ")
            x = input("column: ")
            while not(y.isdigit() and x.isdigit() and (0 <= int(y) <= 5) and (0 <= int(y) <= 5)):
                print("invalid input, try again")
                y = input("line: ")
                x = input("column: ")
            y = int(y)
            x = int(x)
            print('-------------')
            print(y, x)
        if field.field[y][x] == '■':
            field.field[y][x] = 'X'
            print('boom')
            for i in field.ships_on_field:
                if Dot(y, x) in i.dts:
                    i.lives -= 1
                    if i.lives == 0:
                        for j in i.contour:
                            try:
                                if field.field[j.x][j.y] == "O" or field.field[j.x][j.y] == "T":
                                    field.field[j.x][j.y] = "."
                            except IndexError:
                                pass
                        field.ships_on_field.remove(i)
                        print('ship destroyed')
            if len(field.ships_on_field) == 0:
                print(f'{name} wins!')
                field.show()
                exit(0)
            field.show()
            self.shoot(field, name)
        elif field.field[y][x] == 'X' or field.field[y][x] == '.' or field.field[y][x] == 'T':
            print('this dot is already revealed, try again')
            self.shoot(field, name)
        else:
            print('miss')
            field.field[y][x] = 'T'


class Game:
    print('-----------------------------------------------')
    print('------------welcome to sea battle!-------------')
    print('-----------------------------------------------')
    print('please use integers from 1 to 5 to input coords')
    print('-----------------------------------------------')
    print('----------good luck and have fun---------------')
    print('-----------------------------------------------')

    def start_game(self):  # непосредственно, логика игры, создаём 2х игроков, даём им отрисованные поля, играем пока
        # у кого-то не кончатся корабли, получаем сообщение, где говорится, кто победил. Опция выхода из программы
        # прописана и в функции shoot, так что можно было в принципе написать и while True, но сделаем наверняка) В
        # целом, изменив пару настроек в этой функции можно зарубиться и в пару человек (правда всё видно будет),
        # либо устроить зарубу 2х ИИ. Называться они правда будут одинаково, но при желании это тоже правится за 2
        # минуты )))
        human = Player()
        ai = Player(False)
        human_field = Field()
        ai_field = Field(hid=True)
        ai_field.deploy_all()
        ai_field.start()
        human_field.deploy_all()
        human_field.start()
        human_field.show()
        while len(ai_field.ships_on_field) != 0 or len(human_field.ships_on_field) != 0:
            human.shoot(ai_field, human.name)
            ai_field.show()
            ai.shoot(human_field, ai.name)
            human_field.show()


g = Game()
g.start_game()

