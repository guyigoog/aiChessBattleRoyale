import random
import chess
import streamlit as st
from typing import Callable, Optional


def safe_get_move(
        board: chess.Board,
        engine_func: Callable,
        sub_model: str,
        turn: str,
        max_retries=3,
        random_fallback=True,
        debug_log=lambda m: None
) -> Optional[chess.Move]:
    """
    Attempt to get a valid/legal move from the engine_func up to max_retries times.
    If random_fallback is True, fallback to random legal move after repeated failures.
    If false, return None => forfeit.
    :param board: chess.Board object representing the current game state.
    :param engine_func: function to call for move generation.
    :param sub_model: sub-model to use for the engine.
    :param turn: current turn ('white' or 'black').
    :param max_retries: maximum number of attempts to get a valid move.
    :param random_fallback: whether to fallback to a random legal move if all attempts fail.
    :param debug_log: function to log debug messages.
    :return: a valid chess.Move object or None if no valid move is found.
    """
    excluded_moves = []

    for attempt in range(max_retries):
        raw_move = engine_func(board, sub_model, excluded_moves=excluded_moves, debug_log=debug_log).strip()
        debug_log(f"{turn.title()} raw attempt #{attempt + 1} [model={sub_model}]: {raw_move}")

        # Try parse UCI
        try:
            move = board.parse_uci(raw_move)
        except ValueError:
            # If not UCI, try SAN
            try:
                move = board.parse_san(raw_move)
            except ValueError:
                move = None

        if move is not None and move in board.legal_moves:
            return move

        # Exclude invalid so model won't repeat
        excluded_moves.append(raw_move)
        debug_log(f"Excluded move appended: {raw_move}")

    # After max_retries
    if random_fallback:
        st.warning(
            f"{turn.title()} gave invalid moves after {max_retries} tries. "
            "Using random legal move as fallback."
        )
        return random.choice(list(board.legal_moves))
    else:
        st.warning(
            f"{turn.title()} gave invalid moves after {max_retries} tries. "
            "No fallback — forfeit."
        )
        return None
