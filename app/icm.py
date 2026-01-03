from typing import List, Tuple
from models import Player, TournamentState, PayoutStructure


def compute_icm_evs(state: TournamentState) -> List[float]:
    """
    Compute ICM $EV for each player in the given tournament state.

    :param state: TournamentState containing players and payout structure
    :return: List of $EVs corresponding to players
    """
    players = state.players
    payouts = state.payout_structure.payouts

    n = len(players)

    # Base case: only one player left
    if n == 1:
        return [payouts[-1] if payouts else 0.0]

    total_chips = sum(p.chips for p in players)
    ev = [0.0 for _ in range(n)]

    # Recursive calculation
    for i, player in enumerate(players):
        p_first = player.chips / total_chips

        # Remaining players after player i finishes first
        remaining_players = players[:i] + players[i + 1:]
        remaining_payouts = payouts[1:]  # remove first place
        remaining_state = TournamentState(
            remaining_players, PayoutStructure(remaining_payouts))
        remaining_ev = compute_icm_evs(remaining_state)

        # Assign first place EV to current player
        ev[i] += p_first * (payouts[0] if payouts else 0.0)

        # Distribute remaining EVs to others
        idx = 0
        for j in range(n):
            if j == i:
                continue
            ev[j] += p_first * remaining_ev[idx]
            idx += 1

    return ev


def compute_bubble_factor_matrix_with_equity(state: TournamentState) -> Tuple[List[List[float]], List[List[float]]]:
    """
    Compute bubble factors assuming all-ins are full stack sizes,
    and also compute required equity for each matchup.

    Returns:
        bf_matrix: N x N list of bubble factors
        req_eq_matrix: N x N list of required equity percentages (0-1)
    """
    n = len(state.players)
    bf_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    req_eq_matrix = [[0.0 for _ in range(n)] for _ in range(n)]

    base_ev = compute_icm_evs(state)

    for A in range(n):
        for B in range(n):
            if A == B:
                continue

            # A wins all-in: A gains B's stack
            players_win = [Player(p.id, p.chips) for p in state.players]
            transfer = min(players_win[A].chips, players_win[B].chips)
            players_win[A].chips += transfer
            players_win[B].chips -= transfer
            ev_win = compute_icm_evs(TournamentState(
                players_win, state.payout_structure))[A]

            # A loses all-in: A loses their stack
            players_lose = [Player(p.id, p.chips) for p in state.players]
            transfer = players_lose[A].chips
            players_lose[A].chips -= transfer
            players_lose[B].chips += transfer
            ev_lose = compute_icm_evs(TournamentState(
                players_lose, state.payout_structure))[A]

            # Bubble Factor
            ev_lost = base_ev[A] - ev_lose
            ev_gained = ev_win - base_ev[A]
            bf = ev_lost / ev_gained if ev_gained != 0 else 0.0
            bf_matrix[A][B] = bf

            # Required Equity
            req_eq_matrix[A][B] = bf / (bf + 1) if bf != 0 else 0.0

    return bf_matrix, req_eq_matrix


def print_bubble_factor_matrix(state: TournamentState, bf_matrix: List[List[float]], req_eq_matrix: List[List[float]]):
    n = len(state.players)
    print("\nBubble Factor Matrix:")
    header = "\t" + "\t".join([f"ID{p.id}" for p in state.players])
    print(header)
    for i in range(n):
        row_str = "\t".join(f"{bf_matrix[i][j]:.2f}" for j in range(n))
        print(f"ID{state.players[i].id}\t{row_str}")

    print("\nRequired Equity Matrix:")
    print(header)
    for i in range(n):
        row_str = "\t".join(
            f"{req_eq_matrix[i][j]*100:.1f}%" for j in range(n))
        print(f"ID{state.players[i].id}\t{row_str}")
