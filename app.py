"""
Chess Teaching App – Play against AI, learn the best move, save game history.
Features:
- Password login with Haitian flag (20082010)
- AI teaches the best move for the current position
- User chooses any legal move from a list
- AI plays as Black with strong moves
- Download full move history at any time
- Logout button
- Company info, WhatsApp, website in sidebar
"""

import streamlit as st
import chess
import chess.svg
from stockfish import Stockfish
import os
import time
from PIL import Image

# ------------------------------
# PAGE CONFIG & LOGIN
# ------------------------------
st.set_page_config(page_title="Chess Teaching AI", layout="wide")

def show_haitian_flag():
    flag_path = "haiti_flag.png"
    if os.path.exists(flag_path):
        flag_img = Image.open(flag_path)
        st.image(flag_img, width=150)
    else:
        st.markdown(
            """
            <div style="display: flex; align-items: center;">
                <div style="background-color: #00209F; width: 60px; height: 40px;"></div>
                <div style="background-color: #DE2119; width: 60px; height: 40px;"></div>
                <span style="font-size: 30px; margin-left: 10px;">🇭🇹</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption("Haitian Flag (blue & red with coat of arms)")

# Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login Required")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        show_haitian_flag()
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
# Show flag again
col_flag, col_title = st.columns([1, 3])
with col_flag:
    show_haitian_flag()
with col_title:
    st.markdown("<h1>♟️ Chess Teaching AI</h1>", unsafe_allow_html=True)
    st.markdown("*Learn the best move from Stockfish, then play against it*")

# ------------------------------
# SIDEBAR – INFO & LOGOUT
# ------------------------------
with st.sidebar:
    st.markdown("## 🇭🇹 GlobalInternet.py")
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
    # Find Stockfish (works on Streamlit Cloud with packages.txt)
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
        sf_path = "stockfish"  # hope it's in PATH
    try:
        st.session_state.stockfish = Stockfish(sf_path)
        st.session_state.stockfish.set_skill_level(15)  # strong but teachable
    except Exception as e:
        st.error(f"Stockfish not found. Please ensure packages.txt includes 'stockfish'. Error: {e}")
        st.stop()
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "last_move" not in st.session_state:
    st.session_state.last_move = None
if "move_history" not in st.session_state:
    st.session_state.move_history = []  # store moves in algebraic notation
if "ai_thinking" not in st.session_state:
    st.session_state.ai_thinking = False
if "best_move_suggestion" not in st.session_state:
    st.session_state.best_move_suggestion = None

# Update Stockfish FEN
st.session_state.stockfish.set_fen_position(st.session_state.board.fen())

# ------------------------------
# HELPER FUNCTIONS
# ------------------------------
def get_best_move():
    """Get the best move from Stockfish for the current position."""
    try:
        best = st.session_state.stockfish.get_best_move()
        if best:
            return chess.Move.from_uci(best)
    except:
        pass
    return None

def get_move_san(move):
    """Return algebraic notation of a move."""
    return st.session_state.board.san(move)

def update_move_history(move):
    """Add a move to history and store SAN."""
    san = get_move_san(move)
    st.session_state.move_history.append(san)

def save_game_history():
    """Return the move history as a downloadable string."""
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

# ------------------------------
# MAIN DISPLAY
# ------------------------------
col_board, col_controls = st.columns([2, 1])

with col_board:
    # Show chessboard
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
        # Show best move suggestion for the user
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
            # Build move options with SAN and UCI
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

    # Download game history
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

    # New game button
    st.markdown("---")
    if st.button("🔄 New Game", use_container_width=True):
        st.session_state.board = chess.Board()
        st.session_state.game_over = False
        st.session_state.last_move = None
        st.session_state.move_history = []
        st.session_state.best_move_suggestion = None
        st.rerun()

# ------------------------------
# GAME STATUS & AI MOVE
# ------------------------------
# Check game over conditions
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

# AI move (Black)
if not st.session_state.game_over and st.session_state.board.turn == chess.BLACK and not st.session_state.ai_thinking:
    st.session_state.ai_thinking = True
    with st.spinner("🤖 AI is calculating the best move..."):
        time.sleep(0.3)  # slight delay for UI
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

# Show game status messages
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

# Footer
st.markdown("---")
st.markdown("📘 **How to learn:** The AI shows the best move suggestion above. You can pick that move or any other legal move. After your move, the AI will play its best response. Download your move history anytime.")
