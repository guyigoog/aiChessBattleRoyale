# AI Chess Battle Royale

The Ultimate AI Chess Showdown Battle Royale! (Untill we can teach them to play Call of Duty).

![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/guyigoog/aiChessBattleRoyale)
![GitHub contributors](https://img.shields.io/github/contributors/guyigoog/aiChessBattleRoyale)
![GitHub stars](https://img.shields.io/github/stars/guyigoog/aiChessBattleRoyale?style=social)
![GitHub forks](https://img.shields.io/github/forks/guyigoog/aiChessBattleRoyale?style=social)
![GitHub issues](https://img.shields.io/github/issues/guyigoog/aiChessBattleRoyale)
![GitHub license](https://img.shields.io/github/license/guyigoog/aiChessBattleRoyale)
![GitHub top language](https://img.shields.io/github/languages/top/guyigoog/aiChessBattleRoyale)

An AI-vs.-AI chess app built with Streamlit. 
You can pit multiple engines (OpenAI, Claude, DeepSeek, and Gemini) against each other, 
each with selectable sub-models (e.g. GPT‑4 vs GPT‑3.5). Features include:
- Time control
- Random-fallback for invalid moves
- Speed-up factor (x1, x2, x3, x4)
- UI for replaying moves
- Downloadable PGN of each game

## Features

- **Engine vs. Engine**: Choose any combination of [OpenAI, Claude, DeepSeek, Gemini].
- **Different Sub-Models**: For example, GPT‑4 vs. GPT‑3.5 within the same engine (OpenAI).
- **Time Control**: Optionally set minutes per side and increments.
- **Invalid Move Recovery**: Attempt multiple retries. If invalid, fallback to random or forfeit.
- **Speed Factor**: Control the delay between moves (speed up or slow down).
- **PGN Logging**: Logs every move and provides a downloadable PGN file.

## Setup & Installation

1. **Clone** the repo:
   ```bash
   git clone https://github.com/guyigoog/aiChessBattleRoyale.git
   ```
2. **Navigate** to the directory:
   ```bash
   cd aiChessBattleRoyale
    ```
3. **Install** the required packages:
4. ```bash
   pip install -r requirements.txt
   ```
5. **Set up** your AI API key:
Edit the `config.py` file to include your API keys for the engines you want to use.
- **For Local runs:** set the `USE_STREAMLIT_SECRETS` variable to `False`.
  - For OpenAI, set the `OPENAI_API_KEY` environment variable.
  - For Claude, set the `CLAUDE_API_KEY` environment variable.
  - For DeepSeek, set the `DEEPEEK_API_KEY` environment variable and set the `DEEPEEK_API_URL` environment variable.
  - For Gemini, set the `GEMINI_API_KEY` environment variable.
- **For Streamlit Cloud:** set the `USE_STREAMLIT_SECRETS` variable to `True` and add your API keys in the Streamlit secrets management.
- **Optionally,** you can override these keys at runtime via the UI.
6. **Run** the app:
   ```bash
   streamlit run main.py
   ```

## Usage

- After launching, open your browser to the displayed local URL (e.g. http://localhost:8501).

- Select the White Engine (OpenAI, Claude, etc.) and a sub-model (e.g. GPT-4).

- Select the Black Engine and sub-model.

- Optionally enable Time Control and specify minutes/inc.

- Optionally override the API keys for each engine to use your own keys, from the UI.

- Fallback: Decide if invalid moves should fallback to a random legal move or forfeit.

- Toggle whether to include a list of legal moves in the prompt. (Increase accuracy, but potentially increase token usage.)

- Choose a speed on the sidebar (x1 = normal, x2/x3/x4 = faster).

- Click Start Game.

The game will begin, and you can watch the moves unfold in real-time.
You can also replay the moves in the UI.
You can download the PGN file of the game for later analysis.

## Files
``` plaintext
.
├── main.py           # Main application file
├── config.py         # API keys and config constants
├── openai_client.py  # OpenAIClient class with context manager and API key setter for multi-client support
├── ai_wrappers.py    # Engine-specific 'get_move' functions
├── move_logic.py     # 'safe_get_move' logic and invalid-move handling
├── ui.py             # Streamlit UI components
├── logger_setup.py   # Logging configuration
├── requirements.txt  # Python dependencies
├── .gitignore        # Git ignore file
├── LICENSE           # MIT License file
└── README.md         # This file
```

## Contributing
Contributions are welcome! If you have suggestions or improvements, please open an issue or submit a pull request.

## Known Issues
- Gpt is trying to cheat by playing illegal moves quite often.

## License
This project is licensed under the [MIT License](LICENSE).