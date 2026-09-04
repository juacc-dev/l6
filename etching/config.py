from pathlib import Path

SAVE_PLOT = False

DATA_DIR = Path("./data")
PLOT_DIR = Path("./plots")

FILE = None
DATASET = None
COMMAND = None


datasets = {
    "viejo": ["2", "3", "4"],
    "nuevo": ["5", "6", "7"],
    "8": ["8a", "8b", "8c"],
}


config = {
    "2": {
        "time": 31.58,
        "plane": [56, -1, 0, 60],
        "limits": None,
        "cut": (None, 50),
    },
    "3": {
        "time": 45.82,
        "plane": [60, -1, 0, 60],
        "limits": None,
        "cut": (None, 77),
    },
    "4": {
        "time": 60.03,
        "plane": [25, 60, 70, -1],
        "limits": None,
        "cut": (40, None),
    },
    "5": {
        "time": 31.29,
        "plane": [70, -1, 0, 35],
        "limits": None,
        "cut": (80, None),
    },
    "6": {
        "time": 45.22,
        "plane": [60, -1, 0, -1],
        "limits": None,
    },
    "7": {
        "time": 60.27,
        "plane": [33, 95, 60, -1],
        "limits": None,
    },
    "8a": {
        "time": 35.52,
        "plane": [85, -1, 0, 70],
        "limits": None,
    },
    "8b": {
        "time": 40.07,
        "plane": [80, -1, 5, 80],
        "limits": None,
    },
    "8c": {
        "time": 50.18,
        "plane": [0, 50, 0, 36],
        "limits": None,
    },
    "8a 2": {
        "time": 35.52,
        "plane": [80, -1, 20, -1],
        "limits": None,
    },
    "8c 2": {
        "time": 50.18,
        "plane": [0, 35, 0, -1],
        "limits": None,
    },
}
