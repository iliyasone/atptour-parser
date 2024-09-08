from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


class Dictable:
    @classmethod
    def to_dict(cls):
        return {k: v for k, v in cls.__dict__.items() if not k.startswith("_")}


class Court(Dictable):
    heightM: float = 8.23
    widthM: float = 23.77


CourtType = type[Court] | Court


class CourtVision(TypedDict):
    players: list[Player]


class Player(TypedDict):
    player: str
    playerIndex: Literal[1, 2]
    sets: list[Set]


class Set(TypedDict):
    set: Literal[1, 2]
    shotsTypes: list[Shots]


class Shots(TypedDict):
    label: str
    shots: list[Shot]


class Shot(TypedDict):
    shotDescription: str
    type: str
    player: str

    balls: list[Ball]

    currentScore: CurrentScore
    attributes: dict[str, str]


class Ball(TypedDict):
    type: str
    cls: str
    x: float
    y: float
    rotate: NotRequired[float]


class CurrentScore(TypedDict):
    player1: Score
    player2: Score


class Score(TypedDict):
    game_score: int
    set_score_1: int
    set_score_2: int | None
