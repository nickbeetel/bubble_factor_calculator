from typing import List
from models import Player, TournamentState, PayoutStructure

# GLOBAL VARS
icm_cache = {}   # cache for compute_icm_evs
sim_cache = {}   # cache for simulate_allin_win / loss


def get_state_key(players: List[Player], payouts: PayoutStructure):
    """Return a tuple key for caching based on chip stacks and payouts, preserving player order."""
    stacks = tuple(p.chips for p in players)  # DO NOT SORT
    payouts_tuple = tuple(payouts.payouts)
    return (stacks, payouts_tuple)


def compute_icm_evs(state: TournamentState) -> List[float]:
    """Compute ICM $EV for each player with memoization."""
    key = get_state_key(state.players, state.payout_structure)
    if key in icm_cache:
        return icm_cache[key]

    players = state.players
    payouts = state.payout_structure.payouts
    n = len(players)

    if n == 1:
        ev = [payouts[-1] if payouts else 0.0]
        icm_cache[key] = ev
        return ev

    total_chips = sum(p.chips for p in players)
    ev = [0.0 for _ in range(n)]

    for i, player in enumerate(players):
        p_first = player.chips / total_chips
        remaining_players = players[:i] + players[i + 1:]
        remaining_payouts = payouts[1:]
        remaining_state = TournamentState(
            remaining_players, PayoutStructure(remaining_payouts)
        )
        remaining_ev = compute_icm_evs(remaining_state)

        ev[i] += p_first * (payouts[0] if payouts else 0.0)

        idx = 0
        for j in range(n):
            if j == i:
                continue
            ev[j] += p_first * remaining_ev[idx]
            idx += 1

    icm_cache[key] = ev
    return ev


def simulate_allin_win(state: TournamentState, A: int, B: int) -> float:
    """
    Simulate A winning an all-in vs B.
    Use cache to avoid recomputing ICM.
    """
    players = [Player(p.id, p.chips) for p in state.players]
    transfer = min(players[A].chips, players[B].chips)
    players[A].chips += transfer
    players[B].chips -= transfer

    key = get_state_key(players, state.payout_structure)
    if key in sim_cache:
        return sim_cache[key][A]

    ev = compute_icm_evs(TournamentState(players, state.payout_structure))
    sim_cache[key] = ev
    return ev[A]


def simulate_allin_loss(state: TournamentState, A: int, B: int) -> float:
    """
    Simulate A losing an all-in vs B.
    Use cache to avoid recomputing ICM.
    """
    players = [Player(p.id, p.chips) for p in state.players]
    transfer = players[A].chips
    players[A].chips -= transfer
    players[B].chips += transfer

    key = get_state_key(players, state.payout_structure)
    if key in sim_cache:
        return sim_cache[key][A]

    ev = compute_icm_evs(TournamentState(players, state.payout_structure))
    sim_cache[key] = ev
    return ev[A]


def compute_bubble_factor(base_ev: float, ev_win: float, ev_lose: float) -> float:
    ev_lost = base_ev - ev_lose
    ev_gained = ev_win - base_ev
    return ev_lost / ev_gained if ev_gained > 0 else 0.0


def compute_required_equity(bf: float) -> float:
    """ Converts bubble factor to required equity. """
    return bf / (bf + 1) if bf > 0 else 0.0


def compute_bubble_factor_matrix_with_equity(state: TournamentState):
    """
    Compute bubble factors + required equity with caching.
    """
    n = len(state.players)
    bf_matrix = [[0.0] * n for _ in range(n)]
    req_eq_matrix = [[0.0] * n for _ in range(n)]

    base_ev = compute_icm_evs(state)

    for A in range(n):
        for B in range(n):
            if A == B:
                continue

            ev_win = simulate_allin_win(state, A, B)
            ev_lose = simulate_allin_loss(state, A, B)

            bf = compute_bubble_factor(base_ev[A], ev_win, ev_lose)
            bf_matrix[A][B] = bf
            req_eq_matrix[A][B] = compute_required_equity(bf)

    return bf_matrix, req_eq_matrix
