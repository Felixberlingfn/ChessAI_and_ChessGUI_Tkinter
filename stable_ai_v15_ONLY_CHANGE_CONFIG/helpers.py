

def to_centi(pawns: float) -> int:
    """ usage will eventually help me find where I still use pawns instead of centi-pawns """
    return round(pawns * 100)


def to_pawns(centi_pawns: int) -> float:
    return round(centi_pawns * 100, 2)