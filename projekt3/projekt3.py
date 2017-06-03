tree = [[1, 0, 1, 2],
        [2, 0, 1, 2],
        [2, 1, 2, 0],
        [2, 1, 0, 1],
        [1, 3, 0, 0]]


V = range(0, len(tree))
WSA_tree, union_tree = zip(*[(node[::2], node[1::2]) for node in tree])


class Hierarchy:
    def __init__(self, tree):
        self.V = range(len(tree))
        self.children_dict = {
            v: [child for child in V if tree[child][0] == v and child != v] for v in V
            }  # wlasciwie dzieci
        self.parent = {v: tree[v][0] for v in V}
        self.restrictions = {v: tree[v][1] for v in V}

    def offspring(self, v):
        for child in self.children_dict[v]:
            for off in self.offspring(child):
                yield off
        yield v

    def feasible_advancements(self, v):
        par = self.parent[v]
        if par != v:
            for adv in self.feasible_advancements(par):
                yield adv
        yield v

WSA = Hierarchy(WSA_tree)
Union = Hierarchy(union_tree)

p = MixedIntegerLinearProgram(maximization=False)


Xwsa = p.new_variable(binary=True, nonnegative=True)
Xunion = p.new_variable(binary=True, nonnegative=True)
# indeksowane parami (szt, prac) - gdzie i to numer sztabu (numer pracownika który na poczatku byl szefem sztabu), a j to numer pracownika
# zmienna wsa[szt, prac] == 1 oznacza, że pracownik prac będzie na miejscu gdzie wcześniej pracował szt
# uwaga: dopuszczamy tylko te zmienne, ze j jest potomkiem i w oryginalnym drzewie (zapobiega skokom na rownych poziomach)

p.set_objective(
    sum(Xwsa[szt, prac] for szt in V for prac in WSA.offspring(szt)) + sum(Xunion[szt, prac] for szt in V for prac in Union.offspring(szt)) # suma wszystkich zmiennych
)

for szt in V:
    # wymagania dotyczace liczebnosci sztabu
    p.add_constraint(sum(sum(Xwsa[child_szt, i] for i in WSA.offspring(child_szt))for child_szt in WSA.offspring(szt)) >= WSA.restrictions[szt])
    p.add_constraint(sum(sum(Xunion[child_szt, i] for i in Union.offspring(child_szt)) for child_szt in Union.offspring(szt)) >= Union.restrictions[szt])

    # w każdym sztabie z niezerowym constraint musi pozostać jakiś pracownik
    WSA_must_exist = 1 if WSA.restrictions[szt] > 0 else 0
    Union_must_exist = 1 if Union.restrictions[szt] > 0 else 0
    p.add_constraint(sum(Xwsa[szt, prac] for prac in WSA.offspring(szt)) == WSA_must_exist)
    p.add_constraint(sum(Xunion[szt, prac] for prac in Union.offspring(szt)) == Union_must_exist)

for prac in V:
    # kazdy pracownik na conajwyzej jednym miejscu
    p.add_constraint(sum(Xwsa[szt, prac] for szt in WSA.feasible_advancements(prac)) <= 1)
    p.add_constraint(sum(Xunion[szt, prac] for szt in Union.feasible_advancements(prac)) <= 1)

    # kazdy pracownik albo w obu firmach albo w zadnej
    p.add_constraint(sum(Xwsa[szt, prac] for szt in WSA.feasible_advancements(prac)) - sum(Xunion[szt, prac] for szt in Union.feasible_advancements(prac)) == 0)

res = p.solve()
#print('Optymalna wartosc funkcji celu = ', res)
#for szt in V:
#    for prac in WSA.offspring(szt):
#        print 'WSA_{},{}'.format(szt,prac), '=', p.get_values(Xwsa[szt, prac])
#    for prac in Union.offspring(szt):
#        print 'Union_{},{}'.format(szt,prac), '=', p.get_values(Xunion[szt, prac])

wyrzuceni = list(filter(lambda prac: sum(p.get_values(Xunion[szt, prac]) for szt in Union.feasible_advancements(prac)) == 0, V))
print wyrzuceni