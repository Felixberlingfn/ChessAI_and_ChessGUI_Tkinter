""" Constants """
INIT_DEPTH = 7  # initial depth for minimax
QUIESCENCE_START = 5

CAPTURE_EXTENSION = 1
CHECK_EXTENSION = 1
PROMOTION_EXTENSION = 1

MAXIMUM_REAL_DEPTH = (INIT_DEPTH + CAPTURE_EXTENSION + CHECK_EXTENSION + 1) * 2

""" Constants relevant for evaluations """

HORIZON_RISK_MULTIPLIER = 0.5
OPPORTUNITY_MULTIPLIER = 0.010  # it is really difficult to find the right value
GOOD_POS_BONUS = 0.1  # this has been working alright
BAD_POS_PUNISH = 0.01  # keep this low

""" Constants that help with readability while not using string comparison """
CALM = 0
CAPTURE = 1
PROMOTION = 2
CHECK = 3
