def parityLadder(n):
    if n == 0:
        return "парное"
    elif n == 1:
        return "непарное"
    elif n == 2:
        return "парное"
    elif n == 3:
        return "непарное"
    elif n == 4:
        return "парное"
    elif n == 5:
        return "непарное"
    elif n == 6:
        return "парное"
    elif n == 7:
        return "непарное"
    elif n == 8:
        return "парное"
    elif n == 9:
        return "непарное"
    elif n == 10:
        return "парное"
    elif n == 11:
        return "непарное"
    elif n == 12:
        return "парное"
    elif n == 13:
        return "непарное"
    elif n < 0:
        return parityLadder(-n)
    else:
        return parityLadder(n - 14)


def validateParity(n):
    if isinstance(n, bool) or not isinstance(n, int):
        raise ValueError("n must be an integer")
    elif abs(n) > 5000:
        raise ValueError("n is too large for the ladder")
    else:
        return parityLadder(n)
