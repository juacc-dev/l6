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
    # "2": {
    #     "time": 31.58,
    #     "plane": [56, -1, 0, 60],
    #     "limits": None,
    #     "cut": (None, 50),
    #     "type": "csv",
    # },
    # "3": {
    #     "time": 45.82,
    #     "plane": [60, -1, 0, 60],
    #     "limits": None,
    #     "cut": (None, 77),
    #     "type": "wyko",
    # },
    # "4": {
    #     "time": 60.03,
    #     "plane": [25, 60, 70, -1],
    #     "limits": None,
    #     "cut": (40, None),
    #     "type": "wyko",
    # },
    "5": {
        "time": 31.29,
        "plane": [70, -1, 0, 35],
        "limits": None,
        "cut": (80, None),
        "type": "wyko",
    },
    "6": {
        "time": 45.22,
        "plane": [60, -1, 0, -1],
        "limits": None,
        "type": "wyko",
    },
    "7": {
        "time": 60.27,
        "plane": [33, 95, 60, -1],
        "limits": None,
        "type": "wyko",
    },
    "8a": {
        "time": 35.52,
        "plane": [85, -1, 0, 70],
        "limits": None,
        "type": "wyko",
    },
    "8b": {
        "time": 40.07,
        "plane": [80, -1, 5, 80],
        "limits": None,
        "type": "wyko",
    },
    "8c": {
        "time": 50.18,
        "plane": [0, 50, 0, 36],
        "limits": None,
        "type": "wyko",
    },
    "8a 2": {
        "time": 35.52,
        "plane": [80, -1, 20, -1],
        "limits": None,
        "type": "wyko",
    },
    "8c 2": {
        "time": 50.18,
        "plane": [0, 35, 0, -1],
        "limits": None,
        "type": "wyko",
    },
    "9-1.processed.luka": {
        "type": "gwyddion",
        # "time": 50.18,
        "plane": [0, 200, 0, 300],
        # "limits": None,
    },
    "9-1.processed": {
        "type": "gwyddion",
        # "time": 50.18,
        "plane": [0, 200, 0, 300],
        # "limits": None,
    },
    "9-1.raw": {
        "type": "gwyddion",
        # "time": 50.18,
        "plane": [0, 200, 0, 300],
        # "limits": None,
    },
    "triangulito del piso-50X.gwyd": {
        "type": "gwyddion",
        "plane": [500, -1, 25, -1],
        # "limits": None,
    },
    "triangulito del piso-50X": {
        "type": "wyko",
        # "plane": [450, -1, 150, -1],
        "plane": [500, -1, 25, -1],
        # "limits": None,
    },
    "2": {
        "time": 31.58,
        "plane": [30, -1, 60, -1],
    },
    "3": {
        "time": 45.82,
        "plane": [30, -1, 60, -1],

    },
    "4": {
        "time": 60.03,
        "plane": [0, 20, 20, 60],
    },
}
