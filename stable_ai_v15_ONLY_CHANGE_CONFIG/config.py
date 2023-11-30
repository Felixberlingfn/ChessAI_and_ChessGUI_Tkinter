""" activate or deactivate features here """

# The features may still impact performance.
# They will just not be added too final scores. This is useful for testing.
AI_NAME = "V15"

horizon_risk_activated = False  # read: https://www.chessprogramming.org/Static_Exchange_Evaluation
horizon_risk_weight = 0.6 if horizon_risk_activated else 0

lost_castling_activated = False
lost_castling_weight = 1 if lost_castling_activated else 0

opportunity_score_activated = False
opportunity_score_weight = 1 if opportunity_score_activated else 0
# important note on op_score: currently works because not converting to centi-pawns

degradation_activated = False
degradation_weight = 1 if degradation_activated else 0

check_extension_minimax_active = True
q_check_ext_deactivated = False

delta_pruning_in_quiescence_active = True
delta_safety_margin = 1 if delta_pruning_in_quiescence_active else float("inf")
