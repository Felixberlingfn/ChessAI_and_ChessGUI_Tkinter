""" activate or deactivate features here """

# The features may still impact performance.
# They will just not be added too final scores. This is useful for testing.

horizon_risk_activated = False  # read: https://www.chessprogramming.org/Static_Exchange_Evaluation
horizon_risk_weight = 0.6
lost_castling_activated = False
opportunity_score_activated = False
degradation_activated = False
degradation_weight = 1

""" trying to find the settings that led to winning against stockfish lv 4"""
# degradation is actually activated in code
