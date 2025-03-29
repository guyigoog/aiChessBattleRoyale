import streamlit as st
import chess
import chess.pgn
import chess.svg
import time
import logging
import openai
import anthropic
from google import genai
from datetime import datetime

import ai_wrappers
from logger import setup_logging
from ui import render_sidebar, render_main_ui, render_api_key_inputs
from ai_wrappers import ENGINE_FUNCTIONS
from move_logic import safe_get_move

st.set_page_config(
    page_title="AI Chess Battle Royale - Guy Perry",
    page_icon=":chess_pawn:",
    layout="wide"
)

# ========== Logging Setup ==========
setup_logging(filename='game_log.pgn')

# ========== Render the Sidebar UI first ==========
debug_mode, speedup_choice = render_sidebar()

# ========== Check for user-provided keys ==========
user_keys = render_api_key_inputs()


# ========== API Key Handling ==========
def override_api_keys_if_provided(user_keys):
    """
    If the user typed a custom key, override the global or st.secrets-based keys.
    Otherwise, fallback to config or st.secrets (whatever ai_wrappers is currently using).
    :param user_keys: Dictionary of user-provided keys
    :return: None
    """
    # If user typed an OpenAI key, override openai.api_key.
    if user_keys["openai"]:
        openai.api_key = user_keys["openai"]

    # For Claude (Anthropic) API, we can set the client directly.
    if user_keys["claude"]:
        ai_wrappers.claude_client = anthropic.Anthropic(api_key=user_keys["claude"])

    # For DeepSeek, we can store it in session_state so our ai_wrappers uses it.
    if user_keys["deepseek"]:
        st.session_state["override_deepseek"] = user_keys["deepseek"]

    # For Gemini (Google), we can set the client directly.
    if user_keys["gemini"]:
        ai_wrappers.genai_client = genai.Client(api_key=user_keys["gemini"])


def debug_log(msg: str):
    """
    Helper to write debug logs if debug_mode is on.
    :param msg: Message to log
    """
    if debug_mode:
        st.sidebar.write(msg)


# ========== Main UI Setup ==========
user_params = render_main_ui()
white_engine = user_params["white_engine"]
white_sub_model = user_params["white_sub_model"]
black_engine = user_params["black_engine"]
black_sub_model = user_params["black_sub_model"]
time_control = user_params["time_control"]
minutes = user_params["minutes"]
increment = user_params["increment"]
random_fallback = user_params["random_fallback"]
start_button_clicked = user_params["start_button_clicked"]

# Prepare a dictionary for speeds
speed_dict = {"x1": 1, "x2": 2, "x3": 3, "x4": 4}

board_placeholder = st.empty()
move_placeholder = st.empty()
status_placeholder = st.empty()

# ======== Session State Setup ========
if 'board_history' not in st.session_state:
    st.session_state.board_history = []
if 'move_log' not in st.session_state:
    st.session_state.move_log = []

# ======== If Start Game is clicked ========
if start_button_clicked:
    # Override API keys if provided
    override_api_keys_if_provided(user_keys)
    # Set up engines
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers.update({
        'Event': 'AI Chess Battle Royale',
        'Date': datetime.now().strftime('%Y.%m.%d'),
        'White': f"{white_engine}({white_sub_model})",
        'Black': f"{black_engine}({black_sub_model})"
    })
    st.session_state.board_history.clear()
    st.session_state.board = board
    st.session_state.pgn = game
    st.session_state.node = game
    st.session_state.move_log.clear()

    # Setup clocks
    st.session_state.move_clock = {
        'white': minutes * 60 if (time_control and minutes) else None,
        'black': minutes * 60 if (time_control and minutes) else None
    }

    # Display initial board
    board_svg = chess.svg.board(board=board, size=400)
    st.session_state.board_history.append(board_svg)
    board_placeholder.markdown("### Current Position")
    board_placeholder.markdown(board_svg, unsafe_allow_html=True)

    turn = 'white'
    forfeit_winner = None

    while not board.is_game_over():
        # Identify engine & sub-model
        if turn == 'white':
            engine_func = ENGINE_FUNCTIONS[white_engine]
            sub_model = white_sub_model
        else:
            engine_func = ENGINE_FUNCTIONS[black_engine]
            sub_model = black_sub_model

        start_time = time.time()
        move = safe_get_move(
            board=board,
            engine_func=engine_func,
            sub_model=sub_model,
            turn=turn,
            max_retries=3,
            random_fallback=random_fallback,
            debug_log=debug_log
        )

        # If no move => forfeit
        if move is None:
            forfeit_winner = 'black' if turn == 'white' else 'white'
            break

        # Push the move
        san = board.san(move)
        board.push(move)

        # Update board
        current_board_svg = chess.svg.board(board=board, size=400)
        st.session_state.board_history.append(current_board_svg)
        board_placeholder.markdown("### Current Position")
        board_placeholder.markdown(current_board_svg, unsafe_allow_html=True)

        # Time control
        elapsed = time.time() - start_time
        if time_control and st.session_state.move_clock[turn] is not None:
            st.session_state.move_clock[turn] -= elapsed
            # st.session_state.move_clock[turn] += increment  # If you want increment
            if st.session_state.move_clock[turn] <= 0:
                st.warning(f"{turn.title()} ran out of time — forfeit.")
                forfeit_winner = 'black' if turn == 'white' else 'white'
                break

        # Logging/PGN
        st.session_state.node = st.session_state.node.add_variation(move)
        st.session_state.move_log.append(f"{turn.title()} played: {san}")

        # Clocks
        if time_control:
            clocks = (
                f"W={st.session_state.move_clock['white']:.1f}s | "
                f"B={st.session_state.move_clock['black']:.1f}s"
            )
        else:
            clocks = "Timeless"

        move_placeholder.markdown(f"**Move**: {san} ({turn}) — {clocks}")

        # Speed factor
        speed_factor = speed_dict[speedup_choice]
        time.sleep(1.0 / speed_factor)

        turn = 'black' if turn == 'white' else 'white'

    # ======== Game Over ========
    if forfeit_winner is not None:
        if forfeit_winner == 'white':
            final_msg = f"White ({white_engine}/{white_sub_model}) wins by forfeit!"
            final_result = "1-0"
        else:
            final_msg = f"Black ({black_engine}/{black_sub_model}) wins by forfeit!"
            final_result = "0-1"
        status_placeholder.markdown(f"### Game over: {final_msg} ({final_result})")
    else:
        result = board.result()  # e.g. '1-0', '0-1', '1/2-1/2'
        if result == "1-0":
            final_msg = f"White ({white_engine}/{white_sub_model}) wins!"
        elif result == "0-1":
            final_msg = f"Black ({black_engine}/{black_sub_model}) wins!"
        else:
            final_msg = "Draw!"
        status_placeholder.markdown(f"### Game over: {final_msg} ({result})")

    # Save PGN
    exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=False)
    pgn_text = st.session_state.pgn.accept(exporter)
    logging.info(pgn_text)
    st.download_button('Download PGN', data=pgn_text, file_name='game.pgn')

# ======== Slider for Historical Positions ========
if 'board_history' in st.session_state and st.session_state.board_history:
    if len(st.session_state.board_history) > 1:
        move_number = st.slider(
            "View previous positions",
            0,
            len(st.session_state.board_history) - 1,
            len(st.session_state.board_history) - 1
        )
    else:
        move_number = 0
        st.text("Initial position")

    st.markdown(st.session_state.board_history[move_number], unsafe_allow_html=True)
    if move_number < len(st.session_state.move_log):
        st.write(f"Position after: {st.session_state.move_log[move_number]}")
    else:
        st.write("No move info available for this position.")
