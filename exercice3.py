"""Exercice 3 - Voyageur de commerce : recherche taboue, recuit simule, algorithme genetique."""
import itertools
import math
import random

# Distances symetriques ; les "-" de l'enonce = aretes inexistantes
_d = {
    (1, 2): 14, (1, 3): 15, (1, 8): 17,
    (2, 3): 13, (2, 4): 14, (2, 5): 20, (2, 8): 21,
    (3, 4): 11, (3, 5): 21, (3, 6): 17, (3, 7): 9, (3, 8): 9,
    (4, 5): 11, (4, 6): 10, (4, 7): 8, (4, 8): 20,
    (5, 6): 15, (5, 7): 18,
    (6, 7): 9,
    (7, 8): 13,
}
DIST = {}
for (a, b), v in _d.items():
    DIST[(a, b)] = DIST[(b, a)] = v
PENALITE = 1000  # cout d'une arete inexistante (tour non realisable)


def longueur(tour):
    """tour = [1, ..., 8] ; le retour a la ville de depart est ajoute automatiquement."""
    chemin = tour + [tour[0]]
    return sum(DIST.get((chemin[k], chemin[k + 1]), PENALITE) for k in range(len(tour)))


def realisable(tour):
    return longueur(tour) < PENALITE


def afficher(tour):
    return "-".join(map(str, tour + [tour[0]]))


# ---------------------------------------------------------------- 1. TABOU
def tabou(initial, iter_max=15, taille_tabou=4):
    x = initial[:]
    best, f_best = x[:], longueur(x)
    liste = []
    print(f"Initiale {afficher(x)} L = {f_best}")
    for it in range(1, iter_max + 1):
        cand = []
        for i, j in itertools.combinations(range(1, len(x)), 2):  # la ville 1 reste fixe
            y = x[:]
            y[i], y[j] = y[j], y[i]
            f = longueur(y)
            mv = (x[i], x[j])
            if (mv not in liste and mv[::-1] not in liste) or f < f_best:  # aspiration
                cand.append((f, mv, y))
        f, mv, y = min(cand, key=lambda c: c[0])
        x = y
        liste.append(mv)
        if len(liste) > taille_tabou:
            liste.pop(0)
        if f < f_best:
            best, f_best = y[:], f
        print(f"Iter {it:2d} | echange villes {mv} | {afficher(x)} L = {f:3d} | meilleur = {f_best}")
    return best, f_best


# ------------------------------------------------------- 2. RECUIT SIMULE
def voisin_realisable(x):
    """Echange de deux villes (hors ville 1), en rejetant les tours non realisables."""
    while True:
        i, j = random.sample(range(1, len(x)), 2)
        y = x[:]
        y[i], y[j] = y[j], y[i]
        if realisable(y):
            return y, (x[i], x[j])


def recuit(initial, T0=20.0, alpha=0.5, n_iter=5, seed=1, verbose=True):
    random.seed(seed)
    x, fx = initial[:], longueur(initial)
    best, f_best = x[:], fx
    T = T0
    if verbose:
        print(f"Initiale {afficher(x)} L = {fx} | T0 = {T0}, alpha = {alpha}, seed = {seed}")
    for it in range(1, n_iter + 1):
        y, mv = voisin_realisable(x)
        fy = longueur(y)
        delta = fy - fx
        if delta <= 0:
            p, r, accepte = 1.0, None, True
        else:
            p = math.exp(-delta / T)
            r = random.random()
            accepte = r < p
        if verbose:
            tirage = "  -  " if r is None else f"{r:.3f}"
            print(f"Iter {it} | T = {T:5.2f} | echange {mv} | L' = {fy:3d} | delta = {delta:3d} | "
                  f"p = {p:.3f} | r = {tirage} | {'accepte' if accepte else 'rejete'}")
        if accepte:
            x, fx = y, fy
            if fx < f_best:
                best, f_best = x[:], fx
        T *= alpha  # variation empirique de T : decroissance geometrique
    return best, f_best


# ------------------------------------------------- 3. ALGORITHME GENETIQUE
def croisement_ox(p1, p2):
    """Order crossover (la ville 1 reste en tete)."""
    n = len(p1)
    a, b = sorted(random.sample(range(1, n), 2))
    enfant = [None] * n
    enfant[0] = p1[0]
    enfant[a:b + 1] = p1[a:b + 1]
    reste = [v for v in p2 if v not in enfant]
    for k in range(n):
        if enfant[k] is None:
            enfant[k] = reste.pop(0)
    return enfant


def mutation(t, pm=0.2):
    t = t[:]
    if random.random() < pm:
        i, j = random.sample(range(1, len(t)), 2)
        t[i], t[j] = t[j], t[i]
    return t


def genetique(taille_pop=10, generations=30, seed=1):
    random.seed(seed)
    villes = list(range(2, 9))
    pop = []
    for _ in range(taille_pop):
        random.shuffle(villes)
        pop.append([1] + villes[:])
    best = min(pop, key=longueur)
    for g in range(1, generations + 1):
        pop.sort(key=longueur)
        elite = pop[:taille_pop // 2]              # selection : la meilleure moitie survit
        enfants = []
        while len(elite) + len(enfants) < taille_pop:
            p1, p2 = random.sample(elite, 2)
            enfants.append(mutation(croisement_ox(p1, p2)))
        pop = elite + enfants
        cand = min(pop, key=longueur)
        if longueur(cand) < longueur(best):
            best = cand[:]
        if g in (1, 5, 10, 20, 30):
            print(f"Generation {g:2d} | meilleur = {afficher(best)} L = {longueur(best)}")
    return best, longueur(best)


# ------------------------------------------------------------- verification
def optimum_exact():
    return min(([1] + list(p) for p in itertools.permutations(range(2, 9))), key=longueur)


if __name__ == "__main__":
    init = [1, 2, 3, 4, 5, 6, 7, 8]
    print("=== 1. Recherche taboue ===")
    b, f = tabou(init)
    print("=> Meilleur :", afficher(b), f)

    print("\n=== 2. Recuit simule ===")
    b, f = recuit(init)
    print("=> Meilleur :", afficher(b), f)
    res = [recuit(init, seed=s, verbose=False)[1] for s in range(1, 101)]
    print(f"Robustesse (100 graines) : moyenne = {sum(res)/len(res):.1f}, "
          f"min = {min(res)}, amelioration de 103 dans {sum(r < 103 for r in res)} cas")

    print("\n=== 3. Algorithme genetique ===")
    b, f = genetique()
    print("=> Meilleur :", afficher(b), f)

    opt = optimum_exact()
    print("\nOptimum exact (force brute, 7! = 5040 tours) :", afficher(opt), longueur(opt))
