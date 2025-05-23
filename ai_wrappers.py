import chess
from google import genai
import anthropic
import streamlit as st
from openai_client import OpenAIClient
from config import (
    USE_STREAMLIT_SECRETS,
    OPENAI_API_KEY,
    CLAUDE_API_KEY,
    DEEPSEEK_API_URL,
    DEEPSEEK_API_KEY,
    GEMINI_API_KEY
)

# Initialize clients
standard_client = OpenAIClient(api_key=st.secrets["OPENAI_API_KEY"] if USE_STREAMLIT_SECRETS else OPENAI_API_KEY)
genai_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"] if USE_STREAMLIT_SECRETS else GEMINI_API_KEY)
claude_client = anthropic.Anthropic(api_key=st.secrets["CLAUDE_API_KEY"] if USE_STREAMLIT_SECRETS else CLAUDE_API_KEY)
deepseek_client = OpenAIClient(
    api_key=st.secrets["DEEPSEEK_API_KEY"] if USE_STREAMLIT_SECRETS else DEEPSEEK_API_KEY,
    api_base=DEEPSEEK_API_URL
)


def get_openai_move(board: chess.Board, sub_model: str, excluded_moves=None, debug_log=lambda m: None,
                    include_valid_moves=False) -> str:
    """
    Get a move from OpenAI's API based on the current board state and excluded moves.
    :param board:  chess.Board object representing the current game state.
    :param sub_model:  The specific OpenAI model to use (e.g., "gpt-4o-mini").
    :param excluded_moves:  List of moves that are invalid or previously attempted.
    :param debug_log:  Function to log debug messages.
    :param include_valid_moves:  Whether to include a list of valid moves in the prompt.
    :return:  The best move in UCI format as a string.
    """

    prompt = build_chess_prompt(board, excluded_moves=excluded_moves, include_valid_moves=include_valid_moves)

    debug_log(f"[OpenAI/{sub_model}] Prompt:\n{prompt}")

    resp = standard_client.chat_completion(
        model=sub_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    raw = resp.choices[0].message.content.strip()
    debug_log(f"[OpenAI/{sub_model}] Raw Response: {raw}")
    return raw


def get_claude_move(board: chess.Board, sub_model: str, excluded_moves=None, debug_log=lambda m: None,
                    include_valid_moves=False) -> str:
    """
    Get a move from Claude's API based on the current board state and excluded moves.
    :param board:  chess.Board object representing the current game state.
    :param sub_model:  The specific Claude model to use (e.g., "claude-3-5-haiku-20241022").
    :param excluded_moves:  List of moves that are invalid or previously attempted.
    :param debug_log:  Function to log debug messages.
    :param include_valid_moves:  Whether to include a list of valid moves in the prompt.
    :return:  The best move in UCI format as a string.
    """

    prompt = build_chess_prompt(board, excluded_moves=excluded_moves, include_valid_moves=include_valid_moves)

    debug_log(f"[Claude/{sub_model}] Prompt:\n{prompt}")

    response = claude_client.messages.create(
        model=sub_model,
        max_tokens=360,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.content
    if isinstance(content, list):
        content = "".join(getattr(block, 'text', str(block)) for block in content)
    raw = content.strip()
    debug_log(f"[Claude/{sub_model}] Raw: {raw}")
    return raw


def get_deepseek_move(board: chess.Board, sub_model: str, excluded_moves=None, debug_log=lambda m: None,
                      include_valid_moves=False) -> str:
    """
    Get a move from DeepSeek's API based on the current board state and excluded moves.
    :param board:  chess.Board object representing the current game state.
    :param sub_model:  The specific DeepSeek model to use (e.g., "deepseek-chat").
    :param excluded_moves:  List of moves that are invalid or previously attempted.
    :param debug_log:  Function to log debug messages.
    :param include_valid_moves:  Whether to include a list of valid moves in the prompt.
    :return:  The best move in UCI format as a string.
    """

    prompt = build_chess_prompt(board, excluded_moves=excluded_moves, include_valid_moves=include_valid_moves)

    debug_log(f"[DeepSeek/{sub_model}] Prompt:\n{prompt}")

    resp = deepseek_client.chat_completion(
        model=sub_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    raw = resp.choices[0].message.content.strip()
    debug_log(f"[DeepSeek/{sub_model}] Raw Response: {raw}")
    return raw


def get_gemini_move(board: chess.Board, sub_model: str, excluded_moves=None, debug_log=lambda m: None,
                    include_valid_moves=False) -> str:
    """
    Get a move from Gemini's API based on the current board state and excluded moves.
    :param board:  chess.Board object representing the current game state.
    :param sub_model:  The specific Gemini model to use (e.g., "gemini-2.0-flash").
    :param excluded_moves:  List of moves that are invalid or previously attempted.
    :param debug_log:  Function to log debug messages.
    :param include_valid_moves:  Whether to include a list of valid moves in the prompt.
    :return:  The best move in UCI format as a string.
    """

    prompt = build_chess_prompt(board, excluded_moves=excluded_moves, include_valid_moves=include_valid_moves)

    debug_log(f"[Gemini/{sub_model}] Prompt:\n{prompt}")

    response = genai_client.models.generate_content(model=sub_model, contents=prompt)
    raw = response.text.strip()
    debug_log(f"[Gemini/{sub_model}] Raw: {raw}")
    return raw


def build_chess_prompt(
        board: chess.Board,
        excluded_moves: object = None,
        include_valid_moves: bool = False
) -> str:
    """
    Constructs a prompt for move generation based on the current board state,
    excluded moves, and optionally includes the list of legal moves.

    :param board: The current chess.Board object.
    :param excluded_moves: List of moves to exclude from the suggestion.
    :param include_valid_moves: Whether to append a list of legal moves to the prompt.
    :return: The constructed prompt string.
    """
    if excluded_moves is None:
        excluded_moves = []
    color_str = "White" if board.turn == chess.WHITE else "Black"

    exclusion_text = ""
    valid_moves_str = ""
    if excluded_moves:
        exclusion_text = (
            f"Invalid or previously attempted moves that are NOT allowed:\n{excluded_moves}\n"
            "Do not return any of those moves, and do not return any illegal moves.\n"
        )

    if include_valid_moves:
        # Append legal moves to the prompt
        legal_moves = ", ".join(move.uci() for move in board.legal_moves)
        valid_moves_str = (
            f"Here is a list of legal moves: {legal_moves}\n"
            "Please choose one of these moves.\n"
        )

    current_move_prompt = (
        f"You are a chess engine. It is {color_str}'s turn.\n"
        f"Given this FEN: {board.fen()}, return a legal best move in UCI format only.\n"
        f"{valid_moves_str}"
        "Do not return any explanations or additional text.\n"
        f"{exclusion_text}"
    )

    return current_move_prompt


ENGINE_FUNCTIONS = {
    'OpenAI': get_openai_move,
    'Claude': get_claude_move,
    'DeepSeek': get_deepseek_move,
    'Gemini': get_gemini_move
}
