# Derived from Colorama

CSI = "\033["


class Fore:
    BLACK = f"\033[{30}m"
    RED = f"\033[{31}m"
    GREEN = f"\033[{32}m"
    YELLOW = f"\033[{33}m"
    BLUE = f"\033[{34}m"
    MAGENTA = f"\033[{35}m"
    CYAN = f"\033[{36}m"
    WHITE = f"\033[{37}m"
    RESET = f"\033[{39}m"

    LIGHTBLACK_EX = f"\033[{90}m"
    LIGHTRED_EX = f"\033[{91}m"
    LIGHTGREEN_EX = f"\033[{92}m"
    LIGHTYELLOW_EX = f"\033[{93}m"
    LIGHTBLUE_EX = f"\033[{94}m"
    LIGHTMAGENTA_EX = f"\033[{95}m"
    LIGHTCYAN_EX = f"\033[{96}m"
    LIGHTWHITE_EX = f"\033[{97}m"


class Back:
    BLACK = f"\033[{40}m"
    RED = f"\033[{41}m"
    GREEN = f"\033[{42}m"
    YELLOW = f"\033[{43}m"
    BLUE = f"\033[{44}m"
    MAGENTA = f"\033[{45}m"
    CYAN = f"\033[{46}m"
    WHITE = f"\033[{47}m"
    RESET = f"\033[{49}m"

    LIGHTBLACK_EX = f"\033[{100}m"
    LIGHTRED_EX = f"\033[{101}m"
    LIGHTGREEN_EX = f"\033[{102}m"
    LIGHTYELLOW_EX = f"\033[{103}m"
    LIGHTBLUE_EX = f"\033[{104}m"
    LIGHTMAGENTA_EX = f"\033[{105}m"
    LIGHTCYAN_EX = f"\033[{106}m"
    LIGHTWHITE_EX = f"\033[{107}m"


class Style:
    BRIGHT = f"\033[{1}m"
    DIM = f"\033[{2}m"
    NORMAL = f"\033[{22}m"
    RESET_ALL = f"\033[{0}m"
