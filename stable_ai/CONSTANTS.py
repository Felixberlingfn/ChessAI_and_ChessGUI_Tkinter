""" Constants """
INIT_DEPTH = 3  # initial depth for minimax
CAPTURE_EXTENSION = 3  # depth extension for captures and promotions aka quiescence search
CHECK_EXTENSION = 3  # depth extension for checks aka quiescence search

MAXIMUM_REAL_DEPTH = (INIT_DEPTH + CAPTURE_EXTENSION + CHECK_EXTENSION + 1) * 2
