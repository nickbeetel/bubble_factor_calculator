from models import Player, PayoutStructure, TournamentState
from icm import *


def build_state(stack_sizes, payouts):
    """Create a TournamentState from raw inputs."""
    players = [Player(id=i, chips=chips)
               for i, chips in enumerate(stack_sizes)]

    payout_structure = PayoutStructure(payouts)
    return TournamentState(players, payout_structure)


def print_icm_evs(players, evs):
    """Pretty-print ICM EVs."""
    print("\nICM $EVs:")
    for p, ev in zip(players, evs):
        print(f"  Player {p.id}: ${ev:.2f}")


def print_results(state, bf_matrix, req_eq_matrix):
    """Wrapper that prints bubble factor + required equity matrices."""
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


def main(stack_sizes, payouts):
    """
    Entry point for computing ICM EVs and bubble factors.
    Only orchestration — no heavy logic.
    """
    state = build_state(stack_sizes, payouts)

    evs = compute_icm_evs(state)
    print_icm_evs(state.players, evs)

    bf_matrix, req_eq_matrix = compute_bubble_factor_matrix_with_equity(state)
    print_results(state, bf_matrix, req_eq_matrix)


if __name__ == "__main__":
    # Example usage
    # replace with your list of stacks
    stack_sizes = [2000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
    payouts = [500, 300, 200]          # replace with payout structure
    main(stack_sizes, payouts)
