CSI = "\033["


def code(n):
    return f"{CSI}{n}m"


class Fore:
    BLACK = code(30)
    RED = code(31)
    GREEN = code(32)
    YELLOW = code(33)
    BLUE = code(34)
    MAGENTA = code(35)
    CYAN = code(36)
    WHITE = code(37)
    RESET = code(39)

    LIGHTBLACK_EX = code(90)
    LIGHTRED_EX = code(91)
    LIGHTGREEN_EX = code(92)
    LIGHTYELLOW_EX = code(93)
    LIGHTBLUE_EX = code(94)
    LIGHTMAGENTA_EX = code(95)
    LIGHTCYAN_EX = code(96)
    LIGHTWHITE_EX = code(97)


class Back:
    BLACK = code(40)
    RED = code(41)
    GREEN = code(42)
    YELLOW = code(43)
    BLUE = code(44)
    MAGENTA = code(45)
    CYAN = code(46)
    WHITE = code(47)
    RESET = code(49)

    LIGHTBLACK_EX = code(100)
    LIGHTRED_EX = code(101)
    LIGHTGREEN_EX = code(102)
    LIGHTYELLOW_EX = code(103)
    LIGHTBLUE_EX = code(104)
    LIGHTMAGENTA_EX = code(105)
    LIGHTCYAN_EX = code(106)
    LIGHTWHITE_EX = code(107)


class Style:
    BRIGHT = code(1)
    DIM = code(2)
    NORMAL = code(22)
    RESET_ALL = code(0)
