""" Constants """
INIT_DEPTH = 7  # initial depth for minimax
QUIESCENCE_START = 5
CAPTURE_EXTENSION = 0  # depth extension for captures and promotions aka quiescence search
CHECK_EXTENSION = 1  # depth extension for checks aka quiescence search

MAXIMUM_REAL_DEPTH = (INIT_DEPTH + CAPTURE_EXTENSION + CHECK_EXTENSION + 1) * 2

""" Constants that help with readability while not using string comparison """
CALM = 0
CAPTURE = 1
PROMOTION = 2
CHECK = 3
