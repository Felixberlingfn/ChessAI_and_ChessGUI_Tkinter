""" activate or deactivate features here """

AI_NAME = "V15"


def activate_presets():
    win_against_stockfish_4()

    activate_new_promising_settings()

    activate_castling()

    # activate_experimental_settings()


""" settings initialization """
stand_pat_active = False

horizon_risk_activated = True
horizon_risk_weight: float = 0.6  # sometimes leads to bad decisions but often improves play too

lost_castling_activated = True
lost_castling_weight = 1
castling_reward = 10
lost_castling_punish = 40

opportunity_score_activated = True
opportunity_score_weight = 1

degradation_activated = False
degradation_weight = 1 / 90

"""activating check extensions can affect quiescence! need to refine how it is handled"""
check_extension_minimax_active = True  # extends minimax search by one
check_extension_q_active = True  # continues quiescence search for check evasions

always_extend_high_value = False
lower_last_victim_value = False
lower_the_bound_val = 3
high_value_bound = 6

delta_pruning_in_quiescence_active = True
delta_safety_margin = 1
victim_safety_margin = 1

max_repetitions = 2


""" preconfigured settings """


def win_against_stockfish_4():
    print("setting 'win_against_stockfish_4' active. This setting has proven to win against stf 4 but is slower")
    global horizon_risk_activated, lost_castling_activated, opportunity_score_activated, degradation_activated
    global check_extension_minimax_active, check_extension_q_active, delta_pruning_in_quiescence_active
    global victim_safety_margin, AI_NAME

    """ deactivate """
    horizon_risk_activated = False
    lost_castling_activated = False
    opportunity_score_activated = False
    delta_pruning_in_quiescence_active = False
    victim_safety_margin = 0
    check_extension_q_active = False
    check_extension_minimax_active = False

    """ activate """
    degradation_activated = True

    AI_NAME = AI_NAME + " + " + "win_against_stockfish_4_settings"

    # there is no alpha beta pruning is V14fix but this shouldn't affect the outcome
    # still trying to find the right settings that caused the win and will comment here when successfull


def activate_new_promising_settings():
    """ new features after 01.12.2023 not proven yet but should improve performance and/or elo """
    global always_extend_high_value, lower_last_victim_value, lower_the_bound_val, high_value_bound, AI_NAME
    always_extend_high_value = True
    lower_last_victim_value = True
    lower_the_bound_val = 5
    high_value_bound = 6

    AI_NAME = AI_NAME + " + " + "new_promising_settings"


def activate_experimental_settings():
    """ just experimental """
    global check_extension_q_active, max_repetitions, AI_NAME, stand_pat_active
    check_extension_q_active = True
    stand_pat_active = True # this is probably implemented wrong as I asked chatgpt
    max_repetitions = 3  # you especially don't want to be blind to the opponent being able to do repetition
    AI_NAME = AI_NAME + " + " + "experimental_settings"


def activate_castling():
    global lost_castling_activated
    lost_castling_activated = True


activate_presets()


""" THE FOLLOWING MUST STAY AT THE BOTTOM - ignore everything below """
q_check_ext_deactivated = not check_extension_q_active

delta_safety_margin = delta_safety_margin if delta_pruning_in_quiescence_active else float("inf")

horizon_risk_weight = horizon_risk_weight if horizon_risk_activated else 0

lost_castling_weight = lost_castling_weight if lost_castling_activated else 0

opportunity_score_weight = opportunity_score_weight if opportunity_score_activated else 0
