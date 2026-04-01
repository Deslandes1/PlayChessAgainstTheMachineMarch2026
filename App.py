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
# Helper functions
# ----------------------------------------------------------------------
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
# Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("♟️ Game Controls")
    difficulty = st.selectbox(
        "AI Difficulty",
        ["easy", "medium", "hard"],
        index=["easy","medium","hard"].index(st.session_state.difficulty)
    )
    if difficulty != st.session_state.difficulty:
        st.session_state.difficulty = difficulty

    if st.button("🔄 New Game"):
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

    st.divider()
    st.header("📊 Move Dashboard")
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

# ----------------------------------------------------------------------
# Main area: Display board and move input
# ----------------------------------------------------------------------
st.title("♟️ Play Chess Against the Machine")
st.markdown("Select a piece and then a destination square from the dropdowns below. The dashboard on the left explains each move. Learn by winning!")

# Display chessboard as SVG
board = st.session_state.board
board_svg = chess.svg.board(board=board, size=400)
st.image(board_svg, use_column_width=True)

# If game over, stop showing move controls
if st.session_state.game_over:
    st.stop()

# Input for user move (only if user's turn)
if st.session_state.user_turn:
    # List all square names
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

st.divider()
st.markdown("Made with ♟️ by GlobalInternet.py – Made in Haiti 🇭🇹")
