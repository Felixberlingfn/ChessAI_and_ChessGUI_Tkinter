""" activate or deactivate features here """

# The features may still impact performance.
# They will just not be added too final scores. This is useful for testing.
AI_NAME = "V15"

horizon_risk_activated = False  # read: https://www.chessprogramming.org/Static_Exchange_Evaluation
horizon_risk_weight = 0.6

lost_castling_activated = False
lost_castling_weight = 1

opportunity_score_activated = False
opportunity_score_weight = 1

degradation_activated = False
degradation_weight = 1

check_extension_minimax_active = True
