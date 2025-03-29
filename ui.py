import streamlit as st

# More models can be added here
ENGINE_MODELS = {
    "OpenAI": [
        "gpt-4o-mini",
        "gpt-3.5-turbo",
        "gpt-4o", "o3-mini",
        "o1-mini"
    ],
    "Claude": [
        "claude-3-5-haiku-20241022",
        "claude-3-haiku-20240307",
        "claude-3-7-sonnet-20250219",
        "claude-3-opus-20240229"
    ],
    "DeepSeek": [
        "deepseek-chat",
        "deepseek-reasoner"
    ],
    "Gemini": [
        "gemini-2.0-flash",
        "gemini-pro",
        "gemini-2.0-flash-lite"
    ]
}


def render_sidebar():
    """
    Renders the Streamlit sidebar elements for debugging, speed, and logs.
    Returns:
        debug_mode (bool), speedup_choice (str)
    """
    debug_mode = st.sidebar.checkbox("Enable Debug Mode?")
    speed_options = ["x1", "x2", "x3", "x4"]
    speedup_choice = st.sidebar.selectbox("Move Speed", speed_options, index=0)

    with st.sidebar.expander("AI Response Log"):
        if 'move_log' in st.session_state:
            st.text_area("Move Log", value="\n".join(st.session_state.move_log), height=400)
        else:
            st.text_area("Move Log", value="", height=400)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Credits")
    st.sidebar.markdown("Developed by: **Guy Perry**")

    st.sidebar.markdown(
        "[![GitHub icon](https://img.icons8.com/ios-glyphs/30/000000/github.png)]"
        "(https://github.com/guyigoog) "
        "[![LinkedIn icon](https://img.icons8.com/ios-glyphs/30/000000/linkedin.png)]"
        "(https://www.linkedin.com/in/guy-perry/)"
    )
    return debug_mode, speedup_choice


def render_main_ui():
    """
    Renders the main UI area (title, engine selects, time controls, fallback checkbox).
    Returns all selected user parameters in a dictionary.
    :return: dict of main UI parameters based on user input
    """
    st.title('AI Chess Battle Royale')

    col1, col2 = st.columns(2)
    with col1:
        # White choices
        white_engine = st.selectbox('White Engine', list(ENGINE_MODELS.keys()), key="white_engine")
        white_sub_model = st.selectbox(
            "White Sub-Model",
            ENGINE_MODELS[white_engine],
            key="white_sub_model"
        )
    with col2:
        # Black choices
        black_engine = st.selectbox('Black Engine', list(ENGINE_MODELS.keys()), key="black_engine")
        black_sub_model = st.selectbox(
            "Black Sub-Model",
            ENGINE_MODELS[black_engine],
            key="black_sub_model"
        )

    # Time control
    time_control = st.checkbox('Use Time Control?')
    if time_control:
        minutes = st.number_input('Minutes per side', min_value=1, value=5)
        increment = st.number_input('Increment (sec)', min_value=0, value=0)
    else:
        minutes = None
        increment = 0

    # Fallback or forfeit
    random_fallback = st.toggle(
        "Fallback to random move if engine can't produce a valid move?",
        value=True
    )
    # Include a list valid moves in prompt
    include_valid_moves = st.toggle(
        "Include list of current legal moves in prompt to improve accuracy?",
        value=False,
        help="When enabled, "
             "this option sends the current list of legal moves along with the board state to the model. "
             "This extra context can lead to more accurate move suggestions. "
             "It can potentially decrease API calls but will increase token usage."
    )

    start_button_clicked = st.button('Start Game')

    return {
        "white_engine": white_engine,
        "white_sub_model": white_sub_model,
        "black_engine": black_engine,
        "black_sub_model": black_sub_model,
        "time_control": time_control,
        "minutes": minutes,
        "increment": increment,
        "random_fallback": random_fallback,
        "include_valid_moves": include_valid_moves,
        "start_button_clicked": start_button_clicked
    }


def render_api_key_inputs():
    """
    Renders text inputs in the sidebar for optional user-provided API keys.
    Returns a dict with the user-provided keys, which may be empty strings if none entered.
    :return: dict of API keys
    """
    user_keys = {"openai": "", "claude": "", "deepseek": "", "gemini": ""}

    with st.sidebar.expander("Provide Your Own API Keys (Optional)", expanded=False):
        user_keys["openai"] = st.text_input(
            "OpenAI API Key",
            value="",
            type="password",
            help="If left blank, fallback to config.py or st.secrets."
        )
        user_keys["claude"] = st.text_input(
            "Claude API Key",
            value="",
            type="password",
            help="If left blank, fallback to config.py or st.secrets."
        )
        user_keys["deepseek"] = st.text_input(
            "DeepSeek API Key",
            value="",
            type="password",
            help="If left blank, fallback to config.py or st.secrets."
        )
        user_keys["gemini"] = st.text_input(
            "Gemini API Key",
            value="",
            type="password",
            help="If left blank, fallback to config.py or st.secrets."
        )

    user_keys = {k: v.strip() for k, v in user_keys.items()}
    return user_keys
