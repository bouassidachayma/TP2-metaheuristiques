"""Exercice 2 - Probleme de transport resolu par recherche taboue."""
import itertools

COUT = [[5, 3, 4],      # D1 -> M1, M2, M3
        [6, 7, 2]]      # D2 -> M1, M2, M3
OFFRE = [8, 9]          # capacites des depots D1, D2
DEMANDE = [4, 5, 8]     # demandes M1, M2, M3
NB_D, NB_M = len(OFFRE), len(DEMANDE)


def cout_total(x):
    return sum(COUT[i][j] * x[i][j] for i in range(NB_D) for j in range(NB_M))


def solution_initiale():
    """Methode du coin nord-ouest : solution realisable de depart."""
    x = [[0] * NB_M for _ in range(NB_D)]
    offre, demande = OFFRE[:], DEMANDE[:]
    i = j = 0
    while i < NB_D and j < NB_M:
        q = min(offre[i], demande[j])
        x[i][j] += q
        offre[i] -= q
        demande[j] -= q
        if offre[i] == 0:
            i += 1
        else:
            j += 1
    return x


def voisins(x):
    """Voisinage : cycle 2x2 (+1,-1,-1,+1) qui conserve offre et demande."""
    for i1, i2 in itertools.permutations(range(NB_D), 2):
        for j1, j2 in itertools.permutations(range(NB_M), 2):
            # on ajoute 1 en (i1,j1) et (i2,j2), on retire 1 en (i1,j2) et (i2,j1)
            if x[i1][j2] >= 1 and x[i2][j1] >= 1:
                y = [ligne[:] for ligne in x]
                y[i1][j1] += 1
                y[i2][j2] += 1
                y[i1][j2] -= 1
                y[i2][j1] -= 1
                yield (i1, i2, j1, j2), y


def recherche_taboue(iter_max=10, taille_tabou=3):
    x = solution_initiale()
    meilleur, f_meilleur = [l[:] for l in x], cout_total(x)
    tabou = []  # liste FIFO de mouvements interdits
    print(f"Solution initiale (coin nord-ouest) : {x}  cout = {cout_total(x)}")
    for it in range(1, iter_max + 1):
        candidats = []
        for mv, y in voisins(x):
            f = cout_total(y)
            # critere d'aspiration : un mouvement tabou est permis s'il bat le record
            if mv not in tabou or f < f_meilleur:
                candidats.append((f, mv, y))
        if not candidats:
            break
        f, mv, y = min(candidats, key=lambda c: c[0])
        x = y
        i1, i2, j1, j2 = mv
        tabou.append((i1, i2, j2, j1))     # interdit le mouvement inverse
        if len(tabou) > taille_tabou:
            tabou.pop(0)
        if f < f_meilleur:
            meilleur, f_meilleur = [l[:] for l in y], f
        print(f"Iter {it:2d} | mouvement {mv} | cout = {f:2d} | meilleur = {f_meilleur}")
    return meilleur, f_meilleur


if __name__ == "__main__":
    sol, f = recherche_taboue()
    print("\nMeilleure solution :")
    for i, ligne in enumerate(sol, 1):
        print(f"  D{i} -> M1,M2,M3 = {ligne}")
    print("Cout minimal trouve :", f)
