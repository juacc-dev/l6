import numpy as np

temp = {
    "ETH#1": 450,
    # "ETH#2": 0,   para paula
    "ETH#3": 470,
    "ETH#4": 490,
    "ETH#5": 510,
    "ETH#6": 530,
    "ETH#7": 560,
    "ETH#8": 460,
    "M9#1": 470,
    "M9#2": 490,
    "M9#3": 510,
    # "M9#4": ,     para paula
    "M9#5": 530,
    "M9#6": 560,
    # "TEST#1": 0,  para paula
    "TEST#2": 500,
    "TEST#3": 550,
    "TEST#4": 520,
    "TEST#5": 580,
    "410C": 410,
    "420C": 420,
    "430C": 430,
    "440C": 440,
}

dist_entre_contactos = {
    "1y2": 480,
    "2y3": 230,
    "3y4": 180,
    "4y5": 80,
}


camino_al_canal = 170

dist_entre_contactos = {
    "1y2": 680 + camino_al_canal,
    "2y3": 380 + camino_al_canal,
    "3y4": 330 + camino_al_canal,
    "4y5": 280 + camino_al_canal,
}

