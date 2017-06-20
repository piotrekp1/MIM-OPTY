from itertools import product

DIE_FACES = 3
PLAYERS = 2


class Bet:
    @staticmethod
    def from_letter(letter):
        letter_num = ord(letter) - ord('a')
        if letter_num == PLAYERS * DIE_FACES:
            return CallBluff()
        faces = letter_num % DIE_FACES
        dices = int((letter_num - faces) / DIE_FACES)
        return RegBet(dices + 1, faces + 1)


class RegBet:
    def __init__(self, dices, faces):
        self.dices = dices
        self.faces = faces

    def __str__(self):
        """Bet represented as a letter (like in Lanctot paper)."""
        return chr(ord('a') + (self.dices - 1) * DIE_FACES + (self.faces - 1))

    def possible_bets_afterwards(self):
        for faces in range(self.faces + 1, DIE_FACES + 1):
            yield RegBet(self.dices, faces)
        for i in product(range(self.dices + 1, PLAYERS + 1), range(1, DIE_FACES + 1)):
            yield RegBet(*i)
        yield CallBluff()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.dices == other.dices and self.faces == other.faces


class CallBluff:
    def __str__(self):
        """Bet represented as a letter (like in Lanctot paper)."""
        return chr(ord('a') + PLAYERS * DIE_FACES)

    def possible_bets_afterwards(self):
        # empty generator
        return iter(())

    def __eq__(self, other):
        return isinstance(other, self.__class__)


class Move:
    def __init__(self, player, faces_thrown, bets_made):
        self.player = player
        self.faces_thrown = faces_thrown
        self.bets_made = bets_made

    def __str__(self):
        return str(self.player) + str(self.faces_thrown) + ''.join(map(str, self.bets_made))

    def __eq__(self, other):
        return self.player == other.player and \
               self.faces_thrown == other.faces_thrown and \
               self.bets_made == other.bets_made

    @property
    def last_bet(self):
        return self.bets_made[-1]

    @staticmethod
    def from_string(str):
        """Assumes that string is in correct format"""
        player = str[0]
        faces_thrown = int(str[1])
        bets_made = list(map(Bet.from_letter, str[2:]))
        return Move(player, faces_thrown, bets_made)


class Move2:
    def __init__(self, player, faces_thrown1, faces_thrown2, bets_made):
        self.player = player
        self.faces_thrown2 = faces_thrown2
        self.faces_thrown1 = faces_thrown1
        self.bets_made = bets_made

    def __str__(self):
        return str(self.player) + str(self.faces_thrown1) + str(self.faces_thrown2) + ''.join(map(str, self.bets_made))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.player == other.player and \
               self.faces_thrown1 == other.faces_thrown1 and \
               self.faces_thrown2 == other.faces_thrown2 and \
               self.bets_made == other.bets_made

    @property
    def last_bet(self):
        return self.bets_made[-1]

    @staticmethod
    def from_string(str):
        """Assumes that string is in correct format"""
        player = str[0]
        faces_thrown1 = int(str[1])
        faces_thrown2 = int(str[2])
        bets_made = list(map(Bet.from_letter, str[3:]))
        return Move2(player, faces_thrown1, faces_thrown2, bets_made)


def possible_reg_bets():
    for i in product(range(1, PLAYERS + 1), range(1, DIE_FACES + 1)):
        yield RegBet(*i)


def possible_bets():
    for bet in possible_reg_bets():
        yield bet
    yield CallBluff()


def possible_sequences_afterwards(seq):
    yield seq
    for bet in seq[-1].possible_bets_afterwards():
        for a in possible_sequences_afterwards(seq + [bet]):
            yield a


def possible_Xs():
    yield Move('X', 0, [])
    for thrown in range(1, DIE_FACES + 1):
        yield Move('X', thrown, [])

    for thrown in range(1, DIE_FACES + 1):
        for starting_bet in possible_reg_bets():
            for seq in possible_sequences_afterwards([starting_bet]):
                if len(seq) % 3 == 1:  # move made by first player
                    yield Move('X', thrown, seq)


def possible_Ys():
    yield Move2('Y', 0, 0, [])
    for thrown1, thrown2 in product(range(1, DIE_FACES + 1), range(1, DIE_FACES + 1)):
        yield Move2('Y', thrown1, thrown2, [])

    for thrown1, thrown2 in product(range(1, DIE_FACES + 1), range(1, DIE_FACES + 1)):
        for starting_bet in possible_reg_bets():
            for seq in possible_sequences_afterwards([starting_bet]):
                if len(seq) % 3 == 0 or (len(seq) % 3 == 2 and seq[-1] == CallBluff()):  # move made by first player
                    yield Move2('Y', thrown1, thrown2, seq)


def checkBetValidity(bet, *args):
    got_dices = 0
    for arg in args:
        if arg == bet.faces or arg == 1:
            got_dices += 1
    return True if got_dices >= bet.dices else False


def A_val(x_move, y_move):
    if len(x_move.bets_made) == 0 or len(y_move.bets_made) == 0:
        return 0  # nie czas wyplaty

    if x_move.last_bet == CallBluff() and y_move.last_bet == CallBluff():
        return 0  # niepoprawne, obydwaj rzekomo zrobili call
    if not x_move.last_bet == CallBluff() and not y_move.last_bet == CallBluff():
        return 0  # to jeszcze nie jest czas wyplaty

    if len(y_move.bets_made) % 3 == 0:
        return 1  # ktorys z graczy y odpada

    if x_move.last_bet == CallBluff():
        if not x_move.bets_made[:-1] == y_move.bets_made:
            return 0  # nie zgadzaja sie ciagi akcji
        return -1 if checkBetValidity(y_move.last_bet, x_move.faces_thrown, y_move.faces_thrown1,
                                      y_move.faces_thrown2) else 1

    if y_move.bets_made[:-1] != x_move.bets_made:
        return 0
    return 1 if checkBetValidity(x_move.last_bet, x_move.faces_thrown, y_move.faces_thrown1,
                                 y_move.faces_thrown2) else -1


possible_xs = list(possible_Xs())
possible_ys = list(possible_Ys())


def A_mat():
    A = []
    for y in possible_ys:
        A_in = []
        for x in possible_xs:
            A_in += [A_val(x, y)]
        A += [A_in]
    return A


A_T = A_mat()


def print_A_MAT():
    X_str = ""
    for x in possible_xs:
        X_str += str(x) + " "

    print("       ", X_str)
    for y_ind in range(len(possible_ys)):
        print('{:5s}: {}'.format(str(possible_ys[y_ind]), A_T[y_ind]))




def x_information_sets():
    empty_move = Move('X', 0, [])
    yield (empty_move, [empty_move])

    for i in range(1, DIE_FACES + 1):
        yield (empty_move, [Move('X', i, [])])

    for i in range(1, DIE_FACES + 1):
        yield (Move('X', i, []),
               [Move('X', i, [bet]) for bet in possible_reg_bets()]
               )

    for x_move in possible_xs[DIE_FACES + 1:]:
        bets = x_move.bets_made
        for y_bet1 in bets[-1].possible_bets_afterwards():
            for y_bet2 in y_bet1.possible_bets_afterwards():
                y_bets_x_reactions = [
                    Move('X', x_move.faces_thrown, bets + [y_bet1, y_bet2, x_bet])
                    for x_bet in y_bet2.possible_bets_afterwards()
                    ]
                if len(y_bets_x_reactions) > 0:
                    yield (x_move, y_bets_x_reactions)


def y_information_sets():
    empty_move = Move2('Y', 0, 0, [])
    yield (empty_move, [empty_move])

    for i1, i2 in product(range(1, DIE_FACES + 1), range(1, DIE_FACES + 1)):
        yield (empty_move, [Move2('Y', i1, i2, [])])

    for i1, i2 in product(range(1, DIE_FACES + 1), range(1, DIE_FACES + 1)):
        for starting_bet in possible_reg_bets():
            instant_call = [Move2('Y', i1, i2, [starting_bet, CallBluff()])]
            starting_bet_reactions = [
                Move2('Y', i1, i2, [starting_bet, y_bet_reaction_bet1, y_bet_reaction_bet2])
                for y_bet_reaction_bet1 in starting_bet.possible_bets_afterwards()
                for y_bet_reaction_bet2 in y_bet_reaction_bet1.possible_bets_afterwards()
                ]
            if len(starting_bet_reactions) > 0:
                yield (Move2('Y', i1, i2, []), instant_call + starting_bet_reactions)

    for y_move in possible_ys[DIE_FACES ** 2 + 1:]:
        bets = y_move.bets_made

        i1, i2 = y_move.faces_thrown1, y_move.faces_thrown2

        for x_bet in bets[-1].possible_bets_afterwards():
            i1, i2 = y_move.faces_thrown1, y_move.faces_thrown2
            instant_call = [Move2('Y', i1, i2, bets + [x_bet, CallBluff()])]
            x_bet_y_reactions = [
                Move2('Y', i1, i2, bets + [x_bet, y_bet1, y_bet2])
                for y_bet1 in x_bet.possible_bets_afterwards()
                for y_bet2 in y_bet1.possible_bets_afterwards()
                ]
            if len(x_bet_y_reactions) > 0:
                yield (y_move, instant_call + x_bet_y_reactions)


y_inf_sets = list(y_information_sets())
x_inf_sets = list(x_information_sets())


def inf_set_to_inf_set_row(inf_set, space):
    inf_set_row = [0] * len(space)
    inf_set_from, inf_set_to_list = inf_set
    inf_set_row[space.index(inf_set_from)] = -1
    for el in inf_set_to_list:
        inf_set_row[space.index(el)] = 1
    return inf_set_row


x_inf_sets_mat = list(map(lambda x: inf_set_to_inf_set_row(x, possible_xs), x_inf_sets))
y_inf_sets_mat = list(map(lambda y: inf_set_to_inf_set_row(y, possible_ys), y_inf_sets))
y_inf_sets_mat_T = list(zip(*y_inf_sets_mat))
y_inf_set_names = ['y_set_' + str(i) for i in range(len(y_inf_sets_mat))]



def MatTimesVec(Matrix, Vec):
    """ Assumes that dimensions match"""
    ret = []
    for row in Matrix:
        ret.append(sum(row[i] * Vec[i] for i in range(len(row))))
    return ret



p = MixedIntegerLinearProgram(maximization=True)
y_set = p.new_variable()
x = p.new_variable(nonnegative=True)

p.set_objective(y_set[0])

possible_xs = list(map(str, possible_xs))
possible_ys = list(map(str, possible_ys))

if len(A_T) != len(y_inf_sets_mat_T) or len(y_inf_sets_mat_T) != len(possible_ys): # jeden constraint na kazda zmienna
    print("nie zgadzaja sie dlugosci")
for j in range(len(A_T)):
    row = A_T[j]
    constraints_row = y_inf_sets_mat_T[j]
    if len(row) != len(possible_xs):
        print("nie zgadzaja sie dlugosci2")
    p.add_constraint( sum(
            row[i] * x[possible_xs[i]] for i in range(len(possible_xs))) - sum(
            constraints_row[i] * y_set[i] for i in range(len(constraints_row))) >= 0)

row = x_inf_sets_mat[0]
p.add_constraint(sum(row[i] * x[possible_xs[i]] for i in range(len(row))) == 1)
for row in x_inf_sets_mat[1:]:
    p.add_constraint(sum(row[i] * x[possible_xs[i]] for i in range(len(row))) == 0)

res = p.solve()
print('res: ', res)
for x_name in possible_xs:
    if p.get_values(x[x_name]) > 0:
        print(x_name, ' val: ', p.get_values(x[x_name]))


# -------------------
# STRATEGIA DLA PODWOJNEGO GRACZA
y_inf_sets_mat_T = list(zip(*y_inf_sets_mat))
x_inf_sets_mat_T = list(zip(*x_inf_sets_mat))
A = list(zip(*A_T))

p2 = MixedIntegerLinearProgram(maximization=False)
x_set = p2.new_variable()
y = p2.new_variable(nonnegative=True)


p2.set_objective(x_set[0])

if len(A) != len(x_inf_sets_mat_T) or len(x_inf_sets_mat_T) != len(possible_xs): # jeden constraint na kazda zmienna
    print("nie zgadzaja sie dlugosci")
for j in range(len(A)):
    row = A[j]
    constraints_row = x_inf_sets_mat_T[j]
    if len(row) != len(possible_ys):
        print("nie zgadzaja sie dlugosci2")
    p2.add_constraint( sum(
            row[i] * y[possible_ys[i]] for i in range(len(possible_ys))) - sum(
            constraints_row[i] * x_set[i] for i in range(len(constraints_row))) <= 0)

row = y_inf_sets_mat[0]
p2.add_constraint(sum(row[i] * y[possible_ys[i]] for i in range(len(row))) == 1)
for row in y_inf_sets_mat[1:]:
    p2.add_constraint(sum(row[i] * y[possible_ys[i]] for i in range(len(row))) == 0)

res = p2.solve()
print('res: ', res)
for y_name in possible_ys:
    if p2.get_values(y[y_name]) > 0:
        print(y_name, ' val: ', p2.get_values(y[y_name]))