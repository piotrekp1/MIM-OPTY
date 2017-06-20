from itertools import product


def A_val(X_str, Y_str):
    if len(X_str) != 3:
        return 0
    if len(Y_str) != 4:
        return 0
    if X_str[2] != Y_str[2]:
        return 0
    x_thrown = int(X_str[1])
    y_thrown = int(Y_str[1])
    pred_val = x_thrown + y_thrown
    x_bet = int(X_str[2])
    if Y_str[-1] == 'w':
        return -1 if pred_val >= x_bet else 1
    else:
        return -1 if pred_val < x_bet else 1


def possible_Xs():
    yield 'X0'
    for i in ('X' + str(i) for i in range(1, 4)):
        yield i
    for i in ('X' + str(i) + str(j) for (i, j) in product(range(1, 4), range(2, 6))):
        yield i


def possible_Ys():
    yield 'Y0'
    for i in ('Y' + str(i) for i in range(1, 3)):
        yield i
    for i in ('Y' + str(i) + str(j) + bet for (i, j, bet) in product(range(1, 3), range(2, 6), ['m', 'w'])):
        yield i


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
A = list(zip(*A_T))
X_str = ""
for x in possible_xs:
    X_str += x + " "

def y_information_sets():
    yield (('Y0', ['Y0']))
    for i in (('Y0', ['Y' + str(i)]) for i in [1, 2]):
        yield i
    for y_throw in [1, 2]:
        for how_high in range(2, 6):
            yield ('Y' + str(y_throw), list('Y' + str(y_throw) + str(how_high) + bet for bet in ['m', 'w']))


def x_information_sets():
    yield (('X0', ['X0']))
    for i in (('X0', ['X' + str(i)]) for i in [1, 2, 3]):
        yield i

    for i in (('X' + str(throw), list('X' + str(throw) + str(how_high) for how_high in range(2, 6))) for throw in
              [1, 2, 3]):
        yield i


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

X_strategy = [
    1,
    1 / 3, 1 / 3, 1 / 3,
    0, 1 / 3, 0, 0,
    0, 1 / 3, 0, 0,
    0, 1 / 3, 0, 0,
]
X_strategy_T = [[i] for i in X_strategy]

def MatTimesVec(Matrix, Vec):
    """ Assumes that dimensions match"""
    ret = []
    for row in Matrix:
        ret.append(sum(row[i] * Vec[i] for i in range(len(row))))
    return ret


wage_vector = MatTimesVec(A_T, X_strategy)

"""
# Program Prymalny
p = MixedIntegerLinearProgram(maximization=False)
y = p.new_variable(nonnegative=True)
p.set_objective( sum(wage_vector[i] * y[possible_ys[i]] for i in range(len(possible_ys))))

print("Constraint Matrix")
for row in y_inf_sets_mat:
    print(row)

row = y_inf_sets_mat[0]
p.add_constraint(sum(row[i] * y[possible_ys[i]] for i in range(len(row))) == 1)
for row in y_inf_sets_mat[1:]:
    p.add_constraint(sum(row[i] * y[possible_ys[i]] for i in range(len(row))) == 0)
"""

# Program Dualny:

p = MixedIntegerLinearProgram(maximization=True)
y_set = p.new_variable()
x = p.new_variable(nonnegative=True)

p.set_objective(y_set[0])


if len(A_T) != len(y_inf_sets_mat_T) or len(y_inf_sets_mat_T) != len(possible_ys): # jeden constraint na kazda zmienna
    print("nie zgadzaja sie dlugosci")
for j in range(len(A_T)):
    row = A_T[j]
    constraints_row = y_inf_sets_mat_T[j]
    p.add_constraint( sum(
            row[i] * x[possible_xs[i]] for i in range(len(possible_xs))) - sum(
            constraints_row[i] * y_set[i] for i in range(len(constraints_row))) >= 0)

row = x_inf_sets_mat[0]
p.add_constraint(sum(row[i] * x[possible_xs[i]] for i in range(len(row))) == 1)
for row in x_inf_sets_mat[1:]:
    p.add_constraint(sum(row[i] * x[possible_xs[i]] for i in range(len(row))) == 0)


p.show()
res = p.solve()
print("obliczylem program")
#for y_name in possible_ys:
#    print('{} val: {}'.format(y_name, p.get_values(y[y_name])))
for i in range(len(y_inf_sets_mat_T[0])):
    print('{} val: {}'.format('y_set' + str(i), p.get_values(y_set[i])))
for x_name in possible_xs:
    print(x_name, ' val: ', p.get_values(x[x_name]))