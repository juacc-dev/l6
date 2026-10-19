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
}

# dist_entre_contactos = {
#     "1y2": 500,
#     "2y3": 200,
#     "3y4": 150,
#     "4y5": 100,
# }
# dist_entre_contactos = {
#     "1y2": 190,
#     "2y3": 87,
#     "3y4": 68,
#     "4y5": 29,
# }

pares = ["4y5", "3y4", "2y3", "1y2"]
dist = [77.76907055, 179.17737673, 230.87416189, 494.47143254]
dist_err = np.array([1.34251393, 3.40998324, 3.45807, 10.50552932])

dist_entre_contactos = {par: d for par, d in zip(pares, dist)}
dist_err_dict = {par: err for par, err in zip(pares, dist_err)}
