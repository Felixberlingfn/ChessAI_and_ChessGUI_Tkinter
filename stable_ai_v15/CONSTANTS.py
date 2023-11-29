""" Constants (some of these are settings, and some of them should NEVER be changed)"""

""" DEPTH """
REAL_QUIESCENCE_START = 2  # 2 means my move, opponent move, my move, then evaluate or quiescence search

""" EVAL_BASED_QUIESCENCE_START: essentially a minimum number of evaluations - improves opening and endgame
A nice side effect: captures are automatically searched deeper because they are first with move ordering"""

""" maybe I can make this higher again and reduce extra depth"""
EVAL_BASED_QUIESCENCE_START = 190000
MAX_EVALS_SHORTEN_QUIESCENCE = 500000  # I will make quiescence shorter
EXTRA_DEPTH_BEFORE_LIMIT = 1  # The number of extra steps while above limit is not reached
CHECK_X_LIMITER = 20  # if I am in check there is no way I can put the opponent in check so actually this could be inf
QUIESCENCE_DEPTH = 11  # total counting from - 11 but starting from - 7 only knight capture are not calm etc.

""" Do not change these: """
INIT_DEPTH = 5 # REAL_QUIESCENCE_START + 1 + EXTRA_DEPTH_BEFORE_LIMIT
MAXIMUM_REAL_DEPTH = CHECK_X_LIMITER + 5
RELATIVE_QUIESCENCE_START = INIT_DEPTH - REAL_QUIESCENCE_START

""" Preference for more deeply evaluated moves """
PREFERENCE_DEEP = 0.1

""" for evaluations """
""" DEGRADATION_FACTOR: We give any material change far in the future a lower value, because of uncertainty"""
DEGRADATION_IMPACT_RATIO = 90  # 500 works the same but somehow 100 looses?
HORIZON_RISK_MULTIPLIER = 0.6
OPPORTUNITY_MULTIPLIER = 0.010  # it is really difficult to find the right value
GOOD_POS_BONUS = 0.1  # this has been working alright
POS_BONUS_MULTIPLIER = 0.1
BAD_POS_PUNISH = 0.01  # keep this low

""" for depth adjustment """
KNIGHT_THRESH = 3 * HORIZON_RISK_MULTIPLIER - 0.1  # at final step we extend based on horizon risk
BISHOP_THRESH = 3.33 * HORIZON_RISK_MULTIPLIER - 0.1
ROOK_THRESH = 5.63 * HORIZON_RISK_MULTIPLIER - 0.1
QUEEN_THRESH = 9.5 * HORIZON_RISK_MULTIPLIER - 0.1
KING_THRESH = 10 * HORIZON_RISK_MULTIPLIER - 0.1

REAL_DEPTH_AND_THRESHOLDS = ((INIT_DEPTH + 0, KNIGHT_THRESH), (INIT_DEPTH + 2, ROOK_THRESH), (INIT_DEPTH + 4, QUEEN_THRESH))
NEW_THRESHOLDS = ((-8, KNIGHT_THRESH), (-7, BISHOP_THRESH), (-5, ROOK_THRESH), (-3, QUEEN_THRESH), (-1, KING_THRESH))  # (-6, BISHOP_THRESH)

""" for readability """
CALM = 0
CAPTURE = 1
PROMOTION = 2
CHECK = 3

QUEEN_VALUE = 9.5
