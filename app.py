import streamlit as st
import chess
import chess.svg
import random
import time

# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Play Chess Against the Machine",
    page_icon="♟️",
    layout="wide"
)

# ----------------------------------------------------------------------
# Custom CSS for the app (clean background, flag, etc.)
# ----------------------------------------------------------------------
st.markdown("""
<style>
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    .stApp {
        background: #f5f5f5;
    }
    .flag-img {
        width: 80px;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .game-title {
        font-size: 2rem;
        font-weight: bold;
        color: #d62c1e;
        text-align: center;
        margin: 0;
    }
    .price-tag {
        background: #d62c1e;
        display: inline-block;
        padding: 6px 18px;
        border-radius: 40px;
        font-weight: bold;
        color: white;
        margin-top: 8px;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 20px;
        font-size: 0.8rem;
        color: #666;
        border-top: 1px solid #ddd;
    }
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Helper functions (authentication, game logic)
# ----------------------------------------------------------------------
def check_password():
    """Returns True if password is correct."""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔐 Enter password to unlock", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔐 Enter password to unlock", type="password", on_change=password_entered, key="password")
        st.error("❌ Wrong password. Try again.")
        return False
    else:
        return True

def logout():
    """Log out by resetting the password flag and clearing game state."""
    # Reset the password flag
    st.session_state["password_correct"] = False
    # Clear any game-related session keys (optional, they will be reinitialized on login)
    keys_to_clear = ["board", "move_history", "game_over", "winner", "difficulty",
                     "last_user_move", "last_ai_move", "last_user_explanation",
                     "last_ai_explanation", "user_turn"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def piece_name(piece):
    """Return human-readable piece name."""
    if piece is None:
        return "piece"
    names = {
        chess.PAWN: "pawn",
        chess.KNIGHT: "knight",
        chess.BISHOP: "bishop",
        chess.ROOK: "rook",
        chess.QUEEN: "queen",
        chess.KING: "king"
    }
    return names[piece.piece_type]

def explain_move(board, move, player="You"):
    """Generate a simple explanation for a move."""
    piece = board.piece_at(move.from_square)
    captured = board.piece_at(move.to_square)
    piece_str = piece_name(piece) if piece else "piece"
    explanation = f"{player} moved the {piece_str} from {chess.square_name(move.from_square)} to {chess.square_name(move.to_square)}."
    if captured:
        explanation += f" That captured the opponent's {piece_name(captured)}!"
    else:
        to_sq = move.to_square
        if chess.square_rank(to_sq) in [3,4] and chess.square_file(to_sq) in [3,4]:
            explanation += " This moves the piece to a central square, giving you more control."
        elif piece and piece.piece_type == chess.KNIGHT and chess.square_rank(to_sq) in [2,3,4,5]:
            explanation += " Knights are often better on central squares."
        elif piece and piece.piece_type == chess.PAWN and chess.square_rank(to_sq) == 4:
            explanation += " Advancing the pawn to the 4th rank is a good developing move."
    board_copy = board.copy()
    board_copy.push(move)
    if board_copy.is_check():
        explanation += " This move puts the opponent in check!"
    return explanation

def ai_move(board, difficulty="easy"):
    """AI makes a move based on difficulty."""
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None
    if difficulty == "easy":
        return random.choice(legal_moves)
    elif difficulty == "medium":
        captures = [m for m in legal_moves if board.is_capture(m)]
        if captures and random.random() < 0.5:
            return random.choice(captures)
        else:
            return random.choice(legal_moves)
    else:  # hard – simple capture priority
        best_value = -1
        best_moves = []
        for move in legal_moves:
            value = 0
            if board.is_capture(move):
                captured = board.piece_at(move.to_square)
                if captured:
                    value = chess.piece_value(captured.piece_type)
            if value > best_value:
                best_value = value
                best_moves = [move]
            elif value == best_value:
                best_moves.append(move)
        if best_moves:
            return random.choice(best_moves)
        else:
            return random.choice(legal_moves)

# ----------------------------------------------------------------------
# Session state initialization
# ----------------------------------------------------------------------
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
    st.session_state.move_history = []
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.difficulty = "easy"
    st.session_state.last_user_move = None
    st.session_state.last_ai_move = None
    st.session_state.last_user_explanation = None
    st.session_state.last_ai_explanation = None
    st.session_state.user_turn = True

# ----------------------------------------------------------------------
# Sidebar with branding, game controls, move dashboard, and logout
# ----------------------------------------------------------------------
with st.sidebar:
    # Haitian flag and company header
    col_flag, col_name = st.columns([1, 3])
    with col_flag:
        st.image("https://flagcdn.com/w320/ht.png", width=60)
    with col_name:
        st.markdown("### **GlobalInternet.py**")
        st.markdown("*Owner: Gesner Deslandes*")
    
    st.divider()
    
    # Game controls
    st.markdown("## ♟️ Game Controls")
    difficulty = st.selectbox(
        "AI Difficulty",
        ["easy", "medium", "hard"],
        index=["easy","medium","hard"].index(st.session_state.difficulty)
    )
    if difficulty != st.session_state.difficulty:
        st.session_state.difficulty = difficulty

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Restart", use_container_width=True):
            st.session_state.board = chess.Board()
            st.session_state.move_history = []
            st.session_state.game_over = False
            st.session_state.winner = None
            st.session_state.last_user_move = None
            st.session_state.last_ai_move = None
            st.session_state.last_user_explanation = None
            st.session_state.last_ai_explanation = None
            st.session_state.user_turn = True
            st.rerun()
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    st.divider()
    
    # Move dashboard
    st.markdown("## 📊 Move Dashboard")
    st.subheader("Your last move")
    if st.session_state.last_user_move:
        st.write(f"Move: {chess.square_name(st.session_state.last_user_move.from_square)} → {chess.square_name(st.session_state.last_user_move.to_square)}")
        st.write(st.session_state.last_user_explanation)
    else:
        st.write("No move yet.")
    st.subheader("AI's last move")
    if st.session_state.last_ai_move:
        st.write(f"Move: {chess.square_name(st.session_state.last_ai_move.from_square)} → {chess.square_name(st.session_state.last_ai_move.to_square)}")
        st.write(st.session_state.last_ai_explanation)
    else:
        st.write("AI hasn't moved yet.")

    st.divider()
    
    # Game status
    st.subheader("Game Status")
    if st.session_state.game_over:
        if st.session_state.winner == "user":
            st.success("🎉 You won! Great job!")
        elif st.session_state.winner == "ai":
            st.error("AI won. Try again!")
        else:
            st.info("Stalemate.")
    else:
        st.info("Game in progress. It's your turn." if st.session_state.user_turn else "AI is thinking...")
    
    st.divider()
    
    # Pricing & license
    st.markdown("## 💰 Pricing")
    st.markdown("""
    <div class="price-tag">One‑time purchase: $20 USD</div>
    <div style="margin-top: 10px;">Includes lifetime access and free updates.</div>
    """, unsafe_allow_html=True)
    
    st.markdown("## 📞 Contact & Payment")
    st.markdown("""
    **📧 Email:** deslndes78@gmail.com  
    **📱 Moncash:** (509) 4738-5663 via Prisme Transfer  
    *Send payment and we'll activate your access.*
    """)
    
    st.divider()
    
    st.markdown("## 📜 License")
    st.markdown("""
    **All Rights Reserved** – Copyright © 2026 GlobalInternet.py  
    This software is for personal use only. Redistribution or resale without permission is prohibited.
    """)
    
    st.divider()
    
    st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <p>🇭🇹 Made in Haiti 🇭🇹</p>
        <p><small>by <strong>GlobalInternet.py</strong><br>Python Developer: Gesner Deslandes</small></p>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Main area: header with flag, title, and chessboard
# ----------------------------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.image("https://flagcdn.com/w320/ht.png", width=100)
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>♟️ Play Chess Against the Machine ♟️</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'><em>Learn by understanding every move</em></p>", unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div style='text-align: right;'>
        <b>GlobalInternet.py</b><br>
        Gesner Deslandes<br>
        Python Developer
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ----------------------------------------------------------------------
# Login check – if not logged in, show password input and description
# ----------------------------------------------------------------------
if not check_password():
    st.info("👋 Welcome to the chess teaching app! Enter the password to start.")
    st.stop()

# ----------------------------------------------------------------------
# Once logged in, display the game interface
# ----------------------------------------------------------------------
st.markdown("## ♟️ Make your move")
st.markdown("Select a piece and then a destination square from the dropdowns below. The dashboard on the left explains each move.")

# Display chessboard as SVG
board = st.session_state.board
board_svg = chess.svg.board(board=board, size=400)
st.image(board_svg, use_column_width=True)

# If game over, stop showing move controls
if st.session_state.game_over:
    st.stop()

# Input for user move (only if user's turn)
if st.session_state.user_turn:
    squares = [chess.square_name(i) for i in range(64)]
    with st.form("move_form"):
        from_sq = st.selectbox("From square", squares, index=0)
        to_sq = st.selectbox("To square", squares, index=0)
        submitted = st.form_submit_button("Make Move")
    if submitted:
        try:
            move = chess.Move.from_uci(from_sq + to_sq)
            if move in board.legal_moves:
                # Apply user move
                explanation = explain_move(board, move, player="You")
                board.push(move)
                st.session_state.last_user_move = move
                st.session_state.last_user_explanation = explanation
                st.session_state.move_history.append(("user", move, explanation))
                # Check for win/draw
                if board.is_checkmate():
                    st.session_state.game_over = True
                    st.session_state.winner = "user"
                elif board.is_stalemate() or board.is_insufficient_material():
                    st.session_state.game_over = True
                    st.session_state.winner = None
                else:
                    st.session_state.user_turn = False
                st.rerun()
            else:
                st.error("Invalid move! Try again.")
        except Exception:
            st.error("Invalid move format. Use standard square names like 'e2' and 'e4'.")
else:
    # AI turn – add a short delay to simulate thinking
    with st.spinner("AI is thinking..."):
        time.sleep(0.5)
        move = ai_move(board, st.session_state.difficulty)
        if move:
            explanation = explain_move(board, move, player="AI")
            board.push(move)
            st.session_state.last_ai_move = move
            st.session_state.last_ai_explanation = explanation
            st.session_state.move_history.append(("ai", move, explanation))
            # Check win/draw
            if board.is_checkmate():
                st.session_state.game_over = True
                st.session_state.winner = "ai"
            elif board.is_stalemate() or board.is_insufficient_material():
                st.session_state.game_over = True
                st.session_state.winner = None
            else:
                st.session_state.user_turn = True
        else:
            st.session_state.game_over = True
            st.session_state.winner = None
    st.rerun()

# ----------------------------------------------------------------------
# Footer
# ----------------------------------------------------------------------
st.divider()
st.markdown("<div class='footer'>Made with ♟️ by GlobalInternet.py – Made in Haiti 🇭🇹</div>", unsafe_allow_html=True)
