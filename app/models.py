from dataclasses import dataclass
from typing import List


@dataclass
class Player:
    """
    Represents a single player in an ICM calculation.
    """
    id: int
    chips: float


@dataclass
class PayoutStructure:
    """
    Represents tournament payouts.
    Example: payouts = [500, 300, 200] for top 3.
    """
    payouts: List[float]


@dataclass
class TournamentState:
    """
    Represents a snapshot of the tournament relevant to ICM.
    """
    players: List[Player]
    payout_structure: PayoutStructure

    def total_chips(self) -> float:
        return sum(p.chips for p in self.players)

    def num_players(self) -> int:
        return len(self.players)
