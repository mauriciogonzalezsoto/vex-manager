from enum import Enum


class ColorScheme(Enum):
    PLAIN = {"name": "plain", "color": (216, 221, 222)}

    STRINGS = {"name": "strings", "color": (121, 169, 120)}

    NUMBERS = {"name": "numbers", "color": (235, 184, 69)}

    COMMENTS = {"name": "comments", "color": (123, 126, 132)}

    FUNCTIONS = {"name": "functions", "color": (136, 136, 193)}

    KEYWORDS = {"name": "keywords", "color": (103, 153, 192)}

    TYPES = {"name": "types", "color": (147, 212, 235)}

    REFERENCES = {"name": "references", "color": (210, 207, 156)}
