from dataclasses import dataclass


@dataclass
class Position:
    commit_position: int
    prepare_position: int
