"""
Mudae $oc (Ouro Chest) puzzle solver core.

Grid 5x5. Red never at center (2,2). Spatial rules (any distance along line):

  Orange  — adjacent to red (Manhattan distance 1)
  Yellow  — on a diagonal line through red (|Δrow| == |Δcol|, any distance)
  Green   — same row OR column as red (any distance)
  Teal    — same row, column, OR diagonal line as red
  Blue    — never shares row, column, nor diagonal with red
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations
from typing import Dict, List, Optional, Set, Tuple

Pos = Tuple[int, int]
GRID_SIZE = 5
CENTER: Pos = (2, 2)

# All cells except center — red can spawn anywhere but never at center.
VALID_RED_POSITIONS: List[Pos] = [
    (r, c)
    for r in range(GRID_SIZE)
    for c in range(GRID_SIZE)
    if (r, c) != CENTER
]


class Color(Enum):
    BLUE = "blue"
    TEAL = "teal"
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"

    @property
    def value_sp(self) -> int:
        return {
            Color.BLUE: 1,
            Color.TEAL: 20,
            Color.GREEN: 35,
            Color.YELLOW: 55,
            Color.ORANGE: 90,
            Color.RED: 150,
        }[self]

    @property
    def hex(self) -> str:
        return {
            Color.BLUE: "#1E88E5",
            Color.TEAL: "#00EEFF",
            Color.GREEN: "#43A047",
            Color.YELLOW: "#FDD835",
            Color.ORANGE: "#FF9800",
            Color.RED: "#E53935",
        }[self]

    @property
    def label_pt(self) -> str:
        return {
            Color.BLUE: "Azul",
            Color.TEAL: "Teal",
            Color.GREEN: "Verde",
            Color.YELLOW: "Amarelo",
            Color.ORANGE: "Laranja",
            Color.RED: "Vermelho",
        }[self]


COLOR_CYCLE: List[Color] = [
    Color.BLUE,
    Color.TEAL,
    Color.GREEN,
    Color.YELLOW,
    Color.ORANGE,
    Color.RED,
]


def _adjacent(red: Pos, pos: Pos) -> bool:
    """Orthogonal neighbor — distance exactly 1."""
    return abs(red[0] - pos[0]) + abs(red[1] - pos[1]) == 1


def _on_diagonal_line(red: Pos, pos: Pos) -> bool:
    """Any cell on a diagonal line through red (bishop rays, any distance)."""
    if pos == red:
        return False
    return abs(red[0] - pos[0]) == abs(red[1] - pos[1])


def _in_row_or_column(red: Pos, pos: Pos) -> bool:
    """Same row or column as red (any distance)."""
    if pos == red:
        return False
    return pos[0] == red[0] or pos[1] == red[1]


def _in_teal_zone(red: Pos, pos: Pos) -> bool:
    """Row, column, or diagonal line relative to red."""
    if pos == red:
        return True
    return _in_row_or_column(red, pos) or _on_diagonal_line(red, pos)


def _in_blue_zone(red: Pos, pos: Pos) -> bool:
    return not _in_teal_zone(red, pos)


def observation_compatible(red: Pos, pos: Pos, color: Color) -> bool:
    """Geometric check: can this color appear at pos if red is at red?"""
    if color == Color.RED:
        return pos == red
    if color == Color.ORANGE:
        return _adjacent(red, pos)
    if color == Color.YELLOW:
        return _on_diagonal_line(red, pos)
    if color == Color.GREEN:
        return _in_row_or_column(red, pos)
    if color == Color.TEAL:
        return _in_teal_zone(red, pos)
    if color == Color.BLUE:
        return _in_blue_zone(red, pos)
    return False


def red_geometrically_valid(
    red: Pos, observations: Dict[Pos, Color]
) -> bool:
    return all(
        observation_compatible(red, pos, color)
        for pos, color in observations.items()
    )


def _teal_zone_cells(red: Pos) -> Set[Pos]:
    return {
        (i, j)
        for i in range(GRID_SIZE)
        for j in range(GRID_SIZE)
        if (i, j) != red and _in_teal_zone(red, (i, j))
    }


def _cells_adjacent_to(red: Pos) -> List[Pos]:
    r, c = red
    return [
        (i, j)
        for i in range(GRID_SIZE)
        for j in range(GRID_SIZE)
        if abs(i - r) + abs(j - c) == 1
    ]


def _cells_on_diagonal_line(red: Pos) -> List[Pos]:
    r, c = red
    return [
        (i, j)
        for i in range(GRID_SIZE)
        for j in range(GRID_SIZE)
        if (i, j) != red and abs(i - r) == abs(j - c)
    ]


def _cells_in_row_or_column(red: Pos) -> List[Pos]:
    r, c = red
    return [
        (i, j)
        for i in range(GRID_SIZE)
        for j in range(GRID_SIZE)
        if (i == r or j == c) and (i, j) != red
    ]


def generate_boards_for_red(red: Pos) -> List[Dict[Pos, Color]]:
    if red == CENTER:
        return []

    adj = _cells_adjacent_to(red)
    diag = _cells_on_diagonal_line(red)
    rowcol = _cells_in_row_or_column(red)
    teal_cells = _teal_zone_cells(red)

    if len(adj) < 2 or len(diag) < 3 or len(rowcol) < 4:
        return []

    boards: List[Dict[Pos, Color]] = []

    for orange in combinations(adj, 2):
        for yellow in combinations(diag, 3):
            green_candidates = [
                p for p in rowcol if p not in orange and p not in yellow
            ]
            if len(green_candidates) < 4:
                continue
            for green in combinations(green_candidates, 4):
                board: Dict[Pos, Color] = {red: Color.RED}
                for p in orange:
                    board[p] = Color.ORANGE
                for p in yellow:
                    board[p] = Color.YELLOW
                for p in green:
                    board[p] = Color.GREEN
                for i in range(GRID_SIZE):
                    for j in range(GRID_SIZE):
                        p = (i, j)
                        if p in board:
                            continue
                        board[p] = (
                            Color.TEAL if p in teal_cells else Color.BLUE
                        )
                boards.append(board)
    return boards


@dataclass
class BoardState:
    id: int
    red: Pos
    cells: Dict[Pos, Color]


def build_all_boards() -> List[BoardState]:
    all_boards: List[BoardState] = []
    idx = 0
    for red in VALID_RED_POSITIONS:
        for cells in generate_boards_for_red(red):
            all_boards.append(BoardState(id=idx, red=red, cells=cells))
            idx += 1
    return all_boards


ALL_BOARDS: List[BoardState] = build_all_boards()
TOTAL_RED_POSITIONS = len(VALID_RED_POSITIONS)


@dataclass
class PuzzleSession:
    board: BoardState
    max_clicks: int = 5
    clicks: List[Pos] = field(default_factory=list)
    score: int = 0
    found_red: bool = False

    def click(self, pos: Pos) -> Color:
        if self.found_red or len(self.clicks) >= self.max_clicks:
            raise RuntimeError("Sem cliques restantes.")
        if pos in self.clicks:
            raise RuntimeError("Célula já clicada.")
        color = self.board.cells[pos]
        self.clicks.append(pos)
        self.score += color.value_sp
        if color == Color.RED:
            self.found_red = True
        return color

    def remaining_clicks(self) -> int:
        return self.max_clicks - len(self.clicks)


def new_random_session() -> PuzzleSession:
    import random

    return PuzzleSession(board=random.choice(ALL_BOARDS))


@dataclass
class SolverState:
    observations: Dict[Pos, Color] = field(default_factory=dict)
    clicked: Set[Pos] = field(default_factory=set)

    def add_observation(self, pos: Pos, color: Color) -> None:
        if pos == CENTER and color == Color.RED:
            raise ValueError("Vermelho nunca pode estar no centro.")
        self.observations[pos] = color
        self.clicked.add(pos)

    def matching_boards(self) -> List[BoardState]:
        observations = self.observations

        if not hasattr(self, "_cached_observations"):
            self._cached_observations = None
            self._cached_boards = None

        if observations == self._cached_observations:
            return self._cached_boards

        if not observations:
            boards = ALL_BOARDS
        else:
            obs_items = tuple(observations.items())
            boards = []

            for board in ALL_BOARDS:
                if not red_geometrically_valid(board.red, observations):
                    continue

                cells = board.cells

                for pos, color in obs_items:
                    if cells[pos] != color:
                        break
                else:
                    boards.append(board)

        # update cache
        self._cached_observations = observations.copy()
        self._cached_boards = boards

        return boards

    def possible_red_positions(self) -> Set[Pos]:
        return {b.red for b in self.matching_boards()}

    def red_probability(self, pos: Pos) -> float:
        if pos == CENTER:
            return 0.0
        boards = self.matching_boards()
        if not boards:
            return 0.0
        return sum(1 for b in boards if b.red == pos) / len(boards)

    def cell_color_distribution(self, pos: Pos) -> Dict[Color, float]:
        boards = self.matching_boards()
        if not boards:
            return {}
        counts: Dict[Color, int] = {}
        for b in boards:
            c = b.cells[pos]
            counts[c] = counts.get(c, 0) + 1
        total = len(boards)
        return {c: n / total for c, n in counts.items()}

    def is_valid_configuration(self) -> bool:
        return len(self.matching_boards()) > 0

    def recommend_click(self) -> Optional[Pos]:
        boards = self.matching_boards()
        if not boards:
            return None

        unclicked = [
            (i, j)
            for i in range(GRID_SIZE)
            for j in range(GRID_SIZE)
            if (i, j) not in self.clicked
        ]
        if not unclicked:
            return None

        for pos in unclicked:
            if self.red_probability(pos) >= 1.0:
                return pos

        best_pos: Optional[Pos] = None
        best_score = -1.0

        for pos in unclicked:
            dist = self.cell_color_distribution(pos)
            if not dist:
                continue

            expected_sp = sum(
                prob * color.value_sp for color, prob in dist.items()
            )
            p_red = dist.get(Color.RED, 0.0)

            info = 0.0
            for color, prob in dist.items():
                if prob <= 0:
                    continue
                remaining = sum(1 for b in boards if b.cells[pos] == color)
                info += prob * (len(boards) - remaining)

            value = expected_sp + p_red * 200 + info * 0.15
            if value > best_score:
                best_score = value
                best_pos = pos

        return best_pos

    def recommendation_reason(self, pos: Pos) -> str:
        dist = self.cell_color_distribution(pos)
        p_red = dist.get(Color.RED, 0.0)
        expected = sum(prob * c.value_sp for c, prob in dist.items())
        possible = len(self.possible_red_positions())
        if p_red >= 1.0:
            return f"Red confirmed in ({pos[0]},{pos[1]})."
        if p_red > 0:
            return (
                f"Click ({pos[0]},{pos[1]}): {p_red:.0%} chance for red, "
                f"~{expected:.0f} SP expected, {possible} reds possible."
            )
        return (
            f"Click ({pos[0]},{pos[1]}): ~{expected:.0f} SP expected, "
            f"reducing candidates ({possible} reds remaining)."
        )
