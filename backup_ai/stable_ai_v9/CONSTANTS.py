""" Constants """
INIT_DEPTH = 5  # was 5 # after this depth only checks and captures with high value pieces are further investigated
EVAL_BASED_QUIESCENCE_START = 80000  # was 10000# increasing this means wider search but slower
REAL_QUIESCENCE_START = 2  # was 3 # increasing this means wider search

CHECK_X_LIMITER = 15  # using real_depth
MAXIMUM_REAL_DEPTH = CHECK_X_LIMITER + 3

""" for evaluations """
DEGRADATION_FACTOR = 500  # Capture Val * (real_depth/DEGRADATION_FACTOR)
HORIZON_RISK_MULTIPLIER = 0.6
OPPORTUNITY_MULTIPLIER = 0.010  # it is really difficult to find the right value
GOOD_POS_BONUS = 0.1  # this has been working alright
BAD_POS_PUNISH = 0.01  # keep this low

""" for depth adjustment """
KNIGHT_THRESH = 3 * HORIZON_RISK_MULTIPLIER - 0.1  # at final step we extend based on horizon risk
ROOK_THRESH = 5 * HORIZON_RISK_MULTIPLIER - 0.1
QUEEN_THRESH = 9 * HORIZON_RISK_MULTIPLIER - 0.1

REAL_DEPTH_AND_THRESHOLDS = ((INIT_DEPTH + 0, KNIGHT_THRESH), (INIT_DEPTH + 2, ROOK_THRESH), (INIT_DEPTH + 4, QUEEN_THRESH))
NEW_THRESHOLDS = ((-7, KNIGHT_THRESH), (-5, ROOK_THRESH), (-3, QUEEN_THRESH))

""" for readability """
CALM = 0
CAPTURE = 1
PROMOTION = 2
CHECK = 3

QUEEN_VALUE = 9
