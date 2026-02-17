import pandas as pd

def classer(valeur):
    if valeur < 0.2:
        return 1
    elif valeur < 0.4:
        return 2
    elif valeur < 0.6:
        return 3
    elif valeur < 0.8:
        return 4
    else:
        return 5
    

 Exemple test
exposition = 0.65
vulnerabilite = 0.7

classe_exp = classer(exposition)
classe_vul = classer(vulnerabilite)

risque = classe_exp * classe_vul

print("Classe risque :", risque)