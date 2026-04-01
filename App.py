import streamlit as st
import chess
import chess.pgn
import random
import time
from streamlit_chessboard import chessboard

# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Play Chess Against the Machine",
    page_icon="♟️",
    layout="wide"
)

# ----------------------------------------------------------------------
# Helper functions for move explanations
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

def piece_symbol(piece):
    """Return Unicode symbol for piece."""
    symbols = {
        chess.PAWN: "♟",
        chess.KNIGHT: "♞",
        chess.BISHOP: "♝",
        chess.ROOK: "♜",
        chess.QUEEN: "♛",
        chess.KING: "♚"
    }
    return symbols[piece.piece_type]

def explain_move(board, move, player="You"):
    """Generate a simple explanation for a move."""
    # Check if move is a capture
    captured = board.piece_at(move.to_square)
    piece = board.piece_at(move.from_square)
    piece_name_str = piece_name(piece) if piece else "piece"
    
    explanation = f"{player} moved the {piece_name_str} from {chess.square_name(move.from_square)} to {chess.square_name(move.to_square)}."
    
    if captured:
        explanation += f" That captured the opponent's {piece_name(captured)}!"
    else:
        # Simple central square encouragement
        to_sq = move.to_square
        if chess.square_rank(to_sq) in [3,4] and chess.square_file(to_sq) in [3,4]:
            explanation += " This moves the piece to a central square, giving you more control."
        elif piece and piece.piece_type == chess.KNIGHT and chess.square_rank(to_sq) in [2,3,4,5]:
            explanation += " Knights are often better on central squares."
        elif piece and piece.piece_type == chess.PAWN and chess.square_rank(to_sq) == 4:
            explanation += " Advancing the pawn to the 4th rank is a good developing move."
    
    # Check if the move puts the opponent in check
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
        # Random legal move
        return random.choice(legal_moves)
    elif difficulty == "medium":
        # Slight preference for captures
        captures = [m for m in legal_moves if board.is_capture(m)]
        if captures and random.random() < 0.5:
            return random.choice(captures)
        else:
            return random.choice(legal_moves)
    else:  # hard – simple evaluation based on piece values
        # Very simple – choose move that maximizes captured piece value (if any)
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
    st.session_state.move_history = []  # list of (move, explanation)
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.difficulty = "easy"
    st.session_state.last_user_move = None
    st.session_state.last_ai_move = None
    st.session_state.last_user_explanation = None
    st.session_state.last_ai_explanation = None
    st.session_state.user_turn = True  # White (user) starts

# ----------------------------------------------------------------------
# Sidebar with game controls and dashboard
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("♟️ Game Controls")
    difficulty = st.selectbox("AI Difficulty", ["easy", "medium", "hard"], index=["easy","medium","hard"].index(st.session_state.difficulty))
    if difficulty != st.session_state.difficulty:
        st.session_state.difficulty = difficulty
        # Optionally reset game when difficulty changes? Keep current game.
    
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
# Main area: chessboard and move explanations
# ----------------------------------------------------------------------
st.title("♟️ Play Chess Against the Machine")
st.markdown("Move pieces by clicking a piece and then the destination square. The dashboard on the left will explain each move. Learn by winning!")

# Display the board using streamlit-chessboard
# We need to handle move input. The chessboard component returns a move string when a move is made.
# We'll use a placeholder and rerun on move.
board_state = st.session_state.board.fen()
# Create the chessboard component
board_component = chessboard(board_state, key="chessboard")

# Check if a move was made by the user
if board_component is not None and isinstance(board_component, str):
    # Component returns UCI string of the move if a move was made
    move_uci = board_component
    # Validate move
    if move_uci and len(move_uci) == 4:
        move = chess.Move.from_uci(move_uci)
        if st.session_state.user_turn and move in st.session_state.board.legal_moves:
            # Apply user move
            board = st.session_state.board
            explanation = explain_move(board, move, player="You")
            board.push(move)
            st.session_state.last_user_move = move
            st.session_state.last_user_explanation = explanation
            st.session_state.move_history.append(("user", move, explanation))
            
            # Check for win/draw after user move
            if board.is_checkmate():
                st.session_state.game_over = True
                st.session_state.winner = "user"
            elif board.is_stalemate() or board.is_insufficient_material():
                st.session_state.game_over = True
                st.session_state.winner = None
            else:
                st.session_state.user_turn = False
                # AI move (will be handled after rerun)
        else:
            st.warning("Invalid move! Try again.")
    
    # Trigger rerun to update board and AI move
    st.rerun()

# AI move (if it's AI's turn and game not over)
if not st.session_state.user_turn and not st.session_state.game_over:
    # Artificial delay to simulate thinking
    with st.spinner("AI is thinking..."):
        time.sleep(0.5)
        board = st.session_state.board
        move = ai_move(board, st.session_state.difficulty)
        if move:
            explanation = explain_move(board, move, player="AI")
            board.push(move)
            st.session_state.last_ai_move = move
            st.session_state.last_ai_explanation = explanation
            st.session_state.move_history.append(("ai", move, explanation))
            
            # Check win/draw after AI move
            if board.is_checkmate():
                st.session_state.game_over = True
                st.session_state.winner = "ai"
            elif board.is_stalemate() or board.is_insufficient_material():
                st.session_state.game_over = True
                st.session_state.winner = None
            else:
                st.session_state.user_turn = True
        else:
            # No legal moves – game over (should have been caught above)
            st.session_state.game_over = True
            st.session_state.winner = None
    
    # Rerun to update board
    st.rerun()

# ----------------------------------------------------------------------
# Footer
# ----------------------------------------------------------------------
st.divider()
st.markdown("Made with ♟️ by GlobalInternet.py – Made in Haiti 🇭🇹")
