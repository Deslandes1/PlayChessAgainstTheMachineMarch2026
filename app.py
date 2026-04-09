"""
Streamlit Chess App with AI Opponent
Features:
- Play against Stockfish AI
- Adjustable AI difficulty (1-20)
- Legal move highlighting
- Move history with algebraic notation
- Game state tracking (check, checkmate, stalemate)
- Reset button to start a new game
"""

import streamlit as st
import chess
import chess.svg
import random
from stockfish import Stockfish
import time
import os

# Page config
st.set_page_config(page_title="Chess Master AI", layout="wide")

# Custom CSS for better UI
st.markdown("""
<style>
    .stButton button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px;
    }
    .chess-board {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "stockfish" not in st.session_state:
    # Try to find Stockfish in common locations
    stockfish_paths = [
        "stockfish",
        "stockfish.exe",
        "/usr/games/stockfish",
        "/usr/local/bin/stockfish",
        "C:/stockfish/stockfish.exe",
        "C:/Program Files/stockfish/stockfish.exe",
        "/mount/src/chess-app/stockfish/stockfish",
        "/mount/src/chess-app/stockfish/stockfish.exe"
    ]
    stockfish_path = None
    for path in stockfish_paths:
        if os.path.exists(path):
            stockfish_path = path
            break
    if stockfish_path is None:
        # Use a default path - will try to install if not found
        stockfish_path = "stockfish"
    try:
        st.session_state.stockfish = Stockfish(stockfish_path)
        st.session_state.stockfish.set_skill_level(10)
    except Exception as e:
        st.error(f"⚠️ Stockfish not found. Please install it with:\n\nsudo apt-get install stockfish\n\nOr download from https://stockfishchess.org/download/")
        st.stop()
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "last_move" not in st.session_state:
    st.session_state.last_move = None
if "selected_square" not in st.session_state:
    st.session_state.selected_square = None
if "ai_thinking" not in st.session_state:
    st.session_state.ai_thinking = False

# Title
st.title("♟️ Chess Master AI")
st.markdown("### Play against a powerful chess engine!")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Difficulty slider
    difficulty = st.slider("AI Difficulty Level", 1, 20, 10, 
                          help="1 = Beginner, 20 = Grandmaster")
    st.session_state.stockfish.set_skill_level(difficulty)
    
    st.markdown("---")
    
    # Game info
    st.header("📊 Game Info")
    
    # Whose turn?
    if not st.session_state.game_over:
        if st.session_state.board.turn == chess.WHITE:
            st.info("🟢 Your turn!")
        else:
            st.warning("🔴 AI is thinking...")
    else:
        st.error("🏁 Game Over!")
    
    # Move history
    st.header("📜 Move History")
    move_history = list(st.session_state.board.move_stack)
    if move_history:
        history_text = ""
        for i, move in enumerate(move_history):
            if i % 2 == 0:
                history_text += f"{i//2 + 1}. {move} "
            else:
                history_text += f"{move}\n"
        if len(move_history) % 2 == 1:
            history_text += "..."
        st.text_area("Moves", history_text, height=200, label_visibility="collapsed")
    else:
        st.caption("No moves yet")
    
    # Reset button
    if st.button("🔄 New Game", use_container_width=True):
        st.session_state.board = chess.Board()
        st.session_state.game_over = False
        st.session_state.last_move = None
        st.session_state.selected_square = None
        st.rerun()

# Main board display
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="chess-board">', unsafe_allow_html=True)
    
    # Get board SVG
    try:
        # Prepare squares for highlighting
        highlight_squares = []
        if st.session_state.selected_square is not None:
            highlight_squares.append(st.session_state.selected_square)
            # Highlight legal moves from selected square
            for move in st.session_state.board.legal_moves:
                if move.from_square == st.session_state.selected_square:
                    highlight_squares.append(move.to_square)
        
        # Generate board SVG
        board_svg = chess.svg.board(
            st.session_state.board,
            size=500,
            squares=highlight_squares,
            lastmove=st.session_state.last_move,
            check=st.session_state.board.king(st.session_state.board.turn) if st.session_state.board.is_check() else None
        )
        st.components.v1.html(board_svg, height=550, width=550)
    except Exception as e:
        st.error(f"Error displaying board: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    
    # Game status
    if not st.session_state.game_over:
        if st.session_state.board.is_check():
            if st.session_state.board.turn == chess.WHITE:
                st.error("⚠️ CHECK! Your king is in danger!")
            else:
                st.error("⚠️ CHECK! AI's king is in danger!")
        elif st.session_state.board.is_checkmate():
            st.session_state.game_over = True
            if st.session_state.board.turn == chess.WHITE:
                st.success("🏆 Checkmate! AI wins! 🏆")
            else:
                st.success("🏆 Checkmate! You win! 🏆")
        elif st.session_state.board.is_stalemate():
            st.session_state.game_over = True
            st.info("♟️ Stalemate! Game drawn.")
        elif st.session_state.board.is_insufficient_material():
            st.session_state.game_over = True
            st.info("♟️ Insufficient material for checkmate. Game drawn.")
        else:
            if st.session_state.board.turn == chess.WHITE:
                st.info("👑 Your move")
            else:
                st.info("🤖 AI is thinking...")
    else:
        if st.session_state.board.is_checkmate():
            if st.session_state.board.turn == chess.WHITE:
                st.success("🏆 Checkmate! AI wins! 🏆")
            else:
                st.success("🏆 Checkmate! You win! 🏆")
        else:
            st.info("♟️ Game Over")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Handle player move via click coordinates (using a simpler approach)
# Since chess.svg doesn't directly give click events, we'll use selectbox for moves
if not st.session_state.game_over and st.session_state.board.turn == chess.WHITE and not st.session_state.ai_thinking:
    st.markdown("### 🎯 Make your move")
    
    # Get legal moves for display
    legal_moves = list(st.session_state.board.legal_moves)
    if legal_moves:
        # Create a dictionary mapping move strings to move objects
        move_options = {}
        for move in legal_moves:
            move_str = f"{chess.square_name(move.from_square)} → {chess.square_name(move.to_square)}"
            if move.promotion:
                move_str += f" (promote to {chess.PIECE_SYMBOLS[move.promotion].upper()})"
            move_options[move_str] = move
        
        # Select move from dropdown
        selected_move_str = st.selectbox("Choose your move:", list(move_options.keys()))
        
        # Make move button
        if st.button("▶️ Make Move", use_container_width=True):
            move = move_options[selected_move_str]
            st.session_state.board.push(move)
            st.session_state.last_move = move
            st.session_state.selected_square = None
            st.rerun()
    else:
        st.error("No legal moves available!")
        st.session_state.game_over = True

# AI Move
if not st.session_state.game_over and st.session_state.board.turn == chess.BLACK and not st.session_state.ai_thinking:
    st.session_state.ai_thinking = True
    with st.spinner("🤖 AI is analyzing the position..."):
        time.sleep(0.5)  # Give the UI time to update
        try:
            # Get best move from Stockfish
            st.session_state.stockfish.set_fen_position(st.session_state.board.fen())
            best_move = st.session_state.stockfish.get_best_move()
            if best_move:
                move = chess.Move.from_uci(best_move)
                if move in st.session_state.board.legal_moves:
                    st.session_state.board.push(move)
                    st.session_state.last_move = move
        except Exception as e:
            st.error(f"AI error: {e}")
    st.session_state.ai_thinking = False
    st.rerun()

# Game over message
if st.session_state.game_over:
    st.balloons()
    st.markdown("### 🎉 Game Over! Click 'New Game' to play again.")

# Footer
st.markdown("---")
st.markdown("### ℹ️ How to Play")
st.markdown("""
1. **White moves first** - you control the white pieces
2. **Select your move** from the dropdown menu
3. **Click 'Make Move'** to execute your move
4. **AI will automatically respond** with its move
5. **Adjust difficulty** in the sidebar (1-20)
6. **New Game** button starts a fresh match
""")
