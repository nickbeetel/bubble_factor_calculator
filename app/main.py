from models import Player, PayoutStructure, TournamentState
from icm import *


def main(stack_sizes, payouts):
    """
    Compute ICM EVs and bubble factors for given stack sizes and payout structure.

    :param stack_sizes: list of chip counts per player
    :param payouts: list of payouts for finishing positions
    """
    # Create Player objects with IDs
    players = [Player(id=i, chips=chips)
               for i, chips in enumerate(stack_sizes)]

    # Create tournament state
    payout_structure = PayoutStructure(payouts)
    state = TournamentState(players, payout_structure)

    # Compute ICM $EVs
    evs = compute_icm_evs(state)
    print("ICM $EVs:")
    for player, ev in zip(players, evs):
        print(f"Player {player.id}: ${ev:.2f}")

    bf_matrix, req_eq_matrix = compute_bubble_factor_matrix_with_equity(state)
    print_bubble_factor_matrix(state, bf_matrix, req_eq_matrix)


if __name__ == "__main__":
    # Example usage
    # replace with your list of stacks
    stack_sizes = [2000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
    payouts = [500, 300, 200]          # replace with payout structure
    main(stack_sizes, payouts)
