"""
Chess Teaching App – Play against AI, learn the best move, save game history.
Features:
- Difficulty levels (Beginner, Intermediate, Advanced)
- Move notation explained (N = Knight, B = Bishop, etc.)
- Piece reference legend with symbols
- Three winning strategies for each level
- Login with Haitian flag (same as GlobalInternet.py website)
- Download move history
- Logout and company info
"""

import streamlit as st
import chess
import chess.svg
from stockfish import Stockfish
import os
import time

# ------------------------------
# PAGE CONFIG & LOGIN
# ------------------------------
st.set_page_config(page_title="Chess Teaching AI", layout="wide")

# Haitian flag from your website
def show_haitian_flag(width=100):
    st.image("https://flagcdn.com/w320/ht.png", width=width)

# Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login Required")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        show_haitian_flag(150)
        st.markdown("<h2 style='text-align: center;'>Chess Teaching AI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>by GlobalInternet.py</p>", unsafe_allow_html=True)
        password_input = st.text_input("Enter password to play", type="password")
        if st.button("Login"):
            if password_input == "20082010":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password. Access denied.")
    st.stop()

# ------------------------------
# AFTER LOGIN – MAIN APP
# ------------------------------
col_flag, col_title = st.columns([1, 3])
with col_flag:
    show_haitian_flag(120)
with col_title:
    st.markdown("<h1>♟️ Chess Teaching AI</h1>", unsafe_allow_html=True)
    st.markdown("*Learn the best move from Stockfish, then play against it*")

# ------------------------------
# SIDEBAR – INFO & LOGOUT & PIECE LEGEND
# ------------------------------
with st.sidebar:
    st.markdown("## 🇭🇹 GlobalInternet.py")
    show_haitian_flag(80)
    st.markdown("### Smart Chess Tutor")
    st.markdown("---")
    st.markdown("**Founder & Developer:**")
    st.markdown("Gesner Deslandes")
    st.markdown("📞 **WhatsApp:** [509 4738-5663](https://wa.me/50947385663)")
    st.markdown("📧 **Email:** deslandes78@gmail.com")
    st.markdown("🌐 **Website:** [www.globalinternet.py](https://www.globalinternet.py)")
    st.markdown("---")
    st.markdown("### 💰 Price")
    st.markdown("**$149 USD** (lifetime license)")
    st.markdown("---")
    
    # 🧩 Piece Reference Legend
    st.markdown("### ♟️ Piece Reference")
    st.markdown("""
    | Piece | Symbol | Letter |
    |-------|--------|--------|
    | King | ♔ | K |
    | Queen | ♕ | Q |
    | Rook | ♖ | R |
    | Bishop | ♗ | B |
    | Knight | ♘ | N |
    | Pawn | ♙ | (no letter) |
    """)
    st.caption("In notation, 'N' stands for Knight (because 'K' is King).")
    
    st.markdown("---")
    st.markdown("### © 2025 GlobalInternet.py")
    st.markdown("All Rights Reserved")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ------------------------------
# INITIALIZE GAME STATE
# ------------------------------
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "stockfish" not in st.session_state:
    stockfish_paths = [
        "stockfish", "stockfish.exe",
        "/usr/games/stockfish", "/usr/local/bin/stockfish",
        "/mount/src/chess-app/stockfish/stockfish",
    ]
    sf_path = None
    for p in stockfish_paths:
        if os.path.exists(p):
            sf_path = p
            break
    if sf_path is None:
        sf_path = "stockfish"
    try:
        st.session_state.stockfish = Stockfish(sf_path)
        st.session_state.stockfish.set_skill_level(10)  # default intermediate
    except Exception as e:
        st.error(f"Stockfish not found. Please ensure packages.txt includes 'stockfish'. Error: {e}")
        st.stop()
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "last_move" not in st.session_state:
    st.session_state.last_move = None
if "move_history" not in st.session_state:
    st.session_state.move_history = []
if "ai_thinking" not in st.session_state:
    st.session_state.ai_thinking = False
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Intermediate"

# Update Stockfish FEN
st.session_state.stockfish.set_fen_position(st.session_state.board.fen())

# ------------------------------
# HELPER FUNCTIONS
# ------------------------------
def get_best_move():
    try:
        best = st.session_state.stockfish.get_best_move()
        if best:
            return chess.Move.from_uci(best)
    except:
        pass
    return None

def get_move_san(move):
    return st.session_state.board.san(move)

def update_move_history(move):
    san = get_move_san(move)
    st.session_state.move_history.append(san)

def save_game_history():
    if not st.session_state.move_history:
        return "No moves played yet."
    history_str = "Game Moves:\n"
    for i, move in enumerate(st.session_state.move_history):
        if i % 2 == 0:
            history_str += f"{i//2 + 1}. {move} "
        else:
            history_str += f"{move}\n"
    if len(st.session_state.move_history) % 2 == 1:
        history_str += "..."
    return history_str

def set_difficulty(level):
    """Set Stockfish skill level based on difficulty."""
    skill_map = {
        "Beginner": 1,
        "Intermediate": 10,
        "Advanced": 18
    }
    st.session_state.stockfish.set_skill_level(skill_map[level])
    st.session_state.difficulty = level

# ------------------------------
# MOVE NOTATION EXPLANATION
# ------------------------------
with st.expander("📖 How to read chess moves (e.g., Nh3)"):
    st.markdown("""
    **Piece letters:**
    - **K** = King
    - **Q** = Queen
    - **R** = Rook
    - **B** = Bishop
    - **N** = Knight (because K is already used for King)
    - (no letter for pawn moves, e.g., `e4` means pawn to e4)
    
    **Coordinates:** Each square has a letter (a-h) for file and a number (1-8) for rank.
    - `Nh3` = Knight moves to square h3
    - `Bxf7` = Bishop captures on f7
    - `O-O` = kingside castling, `O-O-O` = queenside castling
    - `+` means check, `#` means checkmate.
    """)

# ------------------------------
# DIFFICULTY SELECTOR
# ------------------------------
difficulty = st.radio(
    "🎮 Chess Game Level:",
    ["Beginner", "Intermediate", "Advanced"],
    index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.difficulty),
    horizontal=True
)
if difficulty != st.session_state.difficulty:
    set_difficulty(difficulty)
    st.rerun()

# ------------------------------
# WINNING STRATEGIES BY LEVEL
# ------------------------------
st.markdown("### 🧠 Three winning moves/strategies for this level")
strategies = {
    "Beginner": [
        "1. **Fool's Mate (2 moves):** 1. f3 e5 2. g4?? Qh4# – Black delivers checkmate in two moves. Learn to spot unprotected kings.",
        "2. **Scholar's Mate (4 moves):** 1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6?? 4. Qxf7# – Attack the f7 square early.",
        "3. **Four-Move Checkmate defense:** As White, play 1. e4, 2. Bc4, 3. Qf3, 4. Qxf7# if Black doesn't defend f7."
    ],
    "Intermediate": [
        "1. **Italian Game – Fried Liver Attack:** 1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 4. Ng5 d5 5. exd5 Nxd5?? 6. Nxf7! winning the queen.",
        "2. **Queen's Gambit Accepted:** 1. d4 d5 2. c4 dxc4 3. e3 – develop quickly and regain the pawn with active pieces.",
        "3. **King's Indian Defense:** As Black, play 1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 – solid and counter-attacking."
    ],
    "Advanced": [
        "1. **Sicilian Dragon – Yugoslav Attack:** 1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 g6 6. Be3 Bg7 7. f3 – aggressive kingside attack.",
        "2. **Ruy Lopez – Marshall Attack:** 1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 O-O 8. c3 d5 – sharp tactical counterplay.",
        "3. **French Defense – Winawer Variation:** 1. e4 e6 2. d4 d5 3. Nc3 Bb4 4. e5 c5 5. a3 Bxc3+ 6. bxc3 – imbalanced pawn structure with attacking chances."
    ]
}

for i, strat in enumerate(strategies[difficulty], 1):
    st.markdown(f"{i}. {strat}")

st.markdown("---")

# ------------------------------
# MAIN GAME DISPLAY
# ------------------------------
col_board, col_controls = st.columns([2, 1])

with col_board:
    highlight_squares = []
    if st.session_state.last_move:
        highlight_squares.append(st.session_state.last_move.from_square)
        highlight_squares.append(st.session_state.last_move.to_square)
    board_svg = chess.svg.board(
        st.session_state.board,
        size=500,
        lastmove=st.session_state.last_move,
        check=st.session_state.board.king(st.session_state.board.turn) if st.session_state.board.is_check() else None,
        squares=highlight_squares
    )
    st.components.v1.html(board_svg, height=550, width=550)

with col_controls:
    st.markdown("### 🎓 AI Teaching")
    if not st.session_state.game_over and st.session_state.board.turn == chess.WHITE:
        best_move = get_best_move()
        if best_move:
            best_san = get_move_san(best_move)
            st.info(f"💡 **Best move suggestion:** {best_san}")
            st.caption("This is the strongest move according to Stockfish. You can choose it or any other legal move.")
        else:
            st.warning("No best move found.")
    else:
        st.info("AI is thinking... (Black's turn)")

    st.markdown("---")
    st.markdown("### 🎯 Your Move")
    if not st.session_state.game_over and st.session_state.board.turn == chess.WHITE and not st.session_state.ai_thinking:
        legal_moves = list(st.session_state.board.legal_moves)
        if legal_moves:
            move_options = {}
            for move in legal_moves:
                san = get_move_san(move)
                move_options[san] = move
            selected_san = st.selectbox("Choose a move:", list(move_options.keys()))
            if st.button("▶️ Make Move", use_container_width=True):
                move = move_options[selected_san]
                st.session_state.board.push(move)
                update_move_history(move)
                st.session_state.last_move = move
                st.rerun()
        else:
            st.error("No legal moves! Game over.")
            st.session_state.game_over = True
    elif st.session_state.game_over:
        st.info("Game finished. Start a new game below.")
    else:
        st.info("AI is thinking... Please wait.")

    st.markdown("---")
    st.markdown("### 📥 Save Game")
    history_text = save_game_history()
    st.download_button(
        label="Download Move History",
        data=history_text,
        file_name=f"chess_game_{time.strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.markdown("---")
    if st.button("🔄 New Game", use_container_width=True):
        st.session_state.board = chess.Board()
        st.session_state.game_over = False
        st.session_state.last_move = None
        st.session_state.move_history = []
        st.rerun()

# ------------------------------
# GAME STATUS & AI MOVE
# ------------------------------
if not st.session_state.game_over:
    if st.session_state.board.is_checkmate():
        st.session_state.game_over = True
        if st.session_state.board.turn == chess.WHITE:
            st.success("🏆 Checkmate! Black (AI) wins.")
        else:
            st.success("🏆 Checkmate! White (You) wins!")
    elif st.session_state.board.is_stalemate():
        st.session_state.game_over = True
        st.info("♟️ Stalemate! Game drawn.")
    elif st.session_state.board.is_insufficient_material():
        st.session_state.game_over = True
        st.info("♟️ Insufficient material – drawn.")

if not st.session_state.game_over and st.session_state.board.turn == chess.BLACK and not st.session_state.ai_thinking:
    st.session_state.ai_thinking = True
    with st.spinner("🤖 AI is calculating the best move..."):
        time.sleep(0.3)
        try:
            st.session_state.stockfish.set_fen_position(st.session_state.board.fen())
            best_move_uci = st.session_state.stockfish.get_best_move()
            if best_move_uci:
                move = chess.Move.from_uci(best_move_uci)
                if move in st.session_state.board.legal_moves:
                    st.session_state.board.push(move)
                    update_move_history(move)
                    st.session_state.last_move = move
        except Exception as e:
            st.error(f"AI error: {e}")
    st.session_state.ai_thinking = False
    st.rerun()

if not st.session_state.game_over:
    if st.session_state.board.is_check():
        if st.session_state.board.turn == chess.WHITE:
            st.warning("⚠️ Your king is in CHECK! Defend it.")
        else:
            st.warning("⚠️ AI's king is in CHECK!")
    else:
        if st.session_state.board.turn == chess.WHITE:
            st.info("Your turn – choose a move from the dropdown.")
        else:
            st.info("AI is thinking – it will move shortly.")
else:
    st.balloons()
    st.markdown("### Game Over! Click 'New Game' to play again.")

st.markdown("---")
st.markdown("📘 **How to learn:** The AI shows the best move suggestion above. You can pick that move or any other legal move. After your move, the AI will play its best response. Download your move history anytime.")
