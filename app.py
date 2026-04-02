import streamlit as st
import chess
import chess.svg
import random
import time
from datetime import datetime

# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Play Chess Against the Machine",
    page_icon="♟️",
    layout="wide"
)

# ----------------------------------------------------------------------
# Custom CSS
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
    .fullscreen-btn {
        background-color: #2c2e3a;
        color: white;
        padding: 6px 12px;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
        border: none;
        width: 100%;
    }
    .fullscreen-btn:hover {
        background-color: #ff7b2c;
    }
    .balloon {
        position: fixed;
        bottom: -100px;
        animation: floatUp 5s ease-in forwards;
        pointer-events: none;
        z-index: 1000;
        font-size: 40px;
    }
    @keyframes floatUp {
        0% { bottom: -100px; opacity: 1; }
        100% { bottom: 120%; opacity: 0; }
    }
    .celebration-text {
        position: fixed;
        top: 30%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0,0,0,0.8);
        color: gold;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        z-index: 1001;
        font-size: 24px;
        font-weight: bold;
        white-space: nowrap;
        animation: fadeOut 5s forwards;
        pointer-events: none;
    }
    @keyframes fadeOut {
        0% { opacity: 1; }
        80% { opacity: 1; }
        100% { opacity: 0; display: none; }
    }
    @media (max-width: 768px) {
        .row-widget.stSelectbox, .stTextArea, .stButton {
            width: 100%;
        }
        .stImage {
            text-align: center;
        }
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Initialize session state (all keys at once)
# ----------------------------------------------------------------------
def init_session_state():
    defaults = {
        "board": chess.Board(),
        "move_history": [],
        "game_over": False,
        "winner": None,
        "difficulty": "easy",
        "last_user_move": None,
        "last_ai_move": None,
        "last_user_explanation": None,
        "last_ai_explanation": None,
        "user_turn": True,
        "lang": "en",
        "password_correct": False,
        "demo_mode": False,
        "celebration_triggered": False,
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

init_session_state()

# ----------------------------------------------------------------------
# Translations – full dictionary
# ----------------------------------------------------------------------
translations = {
    "en": {
        "app_title": "♟️ Play Chess Against the Machine ♟️",
        "app_subtitle": "Learn by understanding every move",
        "sidebar_company": "GlobalInternet.py",
        "sidebar_owner": "Owner: Gesner Deslandes",
        "game_controls": "♟️ Game Controls",
        "ai_difficulty": "AI Difficulty",
        "easy": "easy",
        "medium": "medium",
        "hard": "hard",
        "restart": "🔄 Restart",
        "logout": "🚪 Logout",
        "download_report": "📥 Download Report",
        "move_dashboard": "📊 Move Dashboard",
        "your_last_move": "Your last move",
        "ai_last_move": "AI's last move",
        "no_move": "No move yet.",
        "game_status": "Game Status",
        "game_in_progress": "Game in progress. It's your turn.",
        "ai_thinking": "AI is thinking...",
        "you_won": "🎉 You won! Great job!",
        "ai_won": "AI won. Try again!",
        "stalemate": "Stalemate.",
        "pricing_title": "💰 Pricing",
        "price_tag": "One‑time purchase: $20 USD",
        "price_desc": "Includes lifetime access and free updates.",
        "contact_title": "📞 Contact & Payment",
        "contact_email": "deslndes78@gmail.com",
        "contact_phone": "(509) 4738-5663 via Prisme Transfer",
        "license_title": "📜 License",
        "license_text": "**All Rights Reserved** – Copyright © 2026 GlobalInternet.py\nThis software is for personal use only. Redistribution or resale without permission is prohibited.",
        "made_in_haiti": "🇭🇹 Made in Haiti 🇭🇹",
        "made_by": "by <strong>GlobalInternet.py</strong><br>Python Developer: Gesner Deslandes",
        "move_heading": "♟️ Make your move",
        "move_instruction": "Select a piece and then a destination square from the dropdowns below. The dashboard on the left explains each move.",
        "from_square": "From square",
        "to_square": "To square",
        "make_move": "Make Move",
        "fullscreen": "⛶ FULLSCREEN",
        "score": "Score (White advantage)",
        "demo_mode": "Demo Mode (show winning strategies)",
        "demo_easy": "Easy – Fork",
        "demo_medium": "Medium – Pin",
        "demo_hard": "Hard – Discovered Check",
        "demo_move": "Move {}: {} → {}",
        "demo_explanation": "This is a winning tactic.",
        "congratulations": "Congratulations! You won!",
        "owner_name": "Gesner Deslandes",
        "company_name": "GlobalInternet.py",
        "piece_names": {
            "pawn": "pawn", "knight": "knight", "bishop": "bishop",
            "rook": "rook", "queen": "queen", "king": "king"
        },
        "move_explanation": "{player} moved the {piece} from {from_sq} to {to_sq}.",
        "capture": " That captured the opponent's {captured}!",
        "central": " This moves the piece to a central square, giving you more control.",
        "knight_central": " Knights are often better on central squares.",
        "pawn_advance": " Advancing the pawn to the 4th rank is a good developing move.",
        "check": " This move puts the opponent in check!",
        "invalid_move_no_piece": "No piece at the from square.",
        "invalid_move_wrong_piece": "That's not your piece. You are playing white.",
        "invalid_move_illegal": "Illegal move. Try a different move.",
        "invalid_move_format": "Invalid move format. Use standard square names like 'e2' and 'e4'."
    },
    "fr": {
        "app_title": "♟️ Jouez aux échecs contre la machine ♟️",
        "app_subtitle": "Apprenez en comprenant chaque coup",
        "sidebar_company": "GlobalInternet.py",
        "sidebar_owner": "Propriétaire : Gesner Deslandes",
        "game_controls": "♟️ Commandes du jeu",
        "ai_difficulty": "Difficulté IA",
        "easy": "facile",
        "medium": "moyen",
        "hard": "difficile",
        "restart": "🔄 Redémarrer",
        "logout": "🚪 Déconnexion",
        "download_report": "📥 Télécharger le rapport",
        "move_dashboard": "📊 Tableau de bord",
        "your_last_move": "Votre dernier coup",
        "ai_last_move": "Dernier coup de l'IA",
        "no_move": "Pas encore de coup.",
        "game_status": "État de la partie",
        "game_in_progress": "Partie en cours. C'est à vous de jouer.",
        "ai_thinking": "L'IA réfléchit...",
        "you_won": "🎉 Vous avez gagné ! Bravo !",
        "ai_won": "L'IA a gagné. Réessayez !",
        "stalemate": "Pat.",
        "pricing_title": "💰 Tarif",
        "price_tag": "Achat unique : 20 USD",
        "price_desc": "Accès à vie et mises à jour gratuites incluses.",
        "contact_title": "📞 Contact & Paiement",
        "contact_email": "deslndes78@gmail.com",
        "contact_phone": "(509) 4738-5663 via Prisme Transfer",
        "license_title": "📜 Licence",
        "license_text": "**Tous droits réservés** – Copyright © 2026 GlobalInternet.py\nCe logiciel est pour usage personnel uniquement. Redistribution ou revente interdite sans autorisation.",
        "made_in_haiti": "🇭🇹 Fabriqué en Haïti 🇭🇹",
        "made_by": "par <strong>GlobalInternet.py</strong><br>Développeur Python : Gesner Deslandes",
        "move_heading": "♟️ Faites votre coup",
        "move_instruction": "Sélectionnez une pièce puis une case de destination dans les listes déroulantes ci-dessous. Le tableau de bord à gauche explique chaque coup.",
        "from_square": "Case de départ",
        "to_square": "Case d'arrivée",
        "make_move": "Jouer",
        "fullscreen": "⛶ PLEIN ÉCRAN",
        "score": "Score (Avantage blanc)",
        "demo_mode": "Mode démo (afficher les stratégies gagnantes)",
        "demo_easy": "Facile – Fourchette",
        "demo_medium": "Moyen – Clouage",
        "demo_hard": "Difficile – Échec à la découverte",
        "demo_move": "Coup {} : {} → {}",
        "demo_explanation": "C'est une tactique gagnante.",
        "congratulations": "Félicitations ! Vous avez gagné !",
        "owner_name": "Gesner Deslandes",
        "company_name": "GlobalInternet.py",
        "piece_names": {
            "pawn": "pion", "knight": "cavalier", "bishop": "fou",
            "rook": "tour", "queen": "dame", "king": "roi"
        },
        "move_explanation": "{player} a déplacé {piece} de {from_sq} vers {to_sq}.",
        "capture": " Cela a capturé le {captured} adverse !",
        "central": " Ce coup place la pièce au centre, vous donnant plus de contrôle.",
        "knight_central": " Les cavaliers sont souvent plus efficaces sur les cases centrales.",
        "pawn_advance": " Avancer le pion à la 4e rangée est un bon coup de développement.",
        "check": " Ce coup met l'adversaire en échec !",
        "invalid_move_no_piece": "Aucune pièce sur la case de départ.",
        "invalid_move_wrong_piece": "Ce n'est pas votre pièce. Vous jouez les blancs.",
        "invalid_move_illegal": "Coup illégal. Essayez un autre coup.",
        "invalid_move_format": "Format de coup invalide. Utilisez des noms standard comme 'e2', 'e4'."
    },
    "es": {
        "app_title": "♟️ Juega al ajedrez contra la máquina ♟️",
        "app_subtitle": "Aprende comprendiendo cada movimiento",
        "sidebar_company": "GlobalInternet.py",
        "sidebar_owner": "Propietario: Gesner Deslandes",
        "game_controls": "♟️ Controles del juego",
        "ai_difficulty": "Dificultad IA",
        "easy": "fácil",
        "medium": "medio",
        "hard": "difícil",
        "restart": "🔄 Reiniciar",
        "logout": "🚪 Cerrar sesión",
        "download_report": "📥 Descargar informe",
        "move_dashboard": "📊 Panel de movimientos",
        "your_last_move": "Tu último movimiento",
        "ai_last_move": "Último movimiento de la IA",
        "no_move": "Aún no hay movimientos.",
        "game_status": "Estado de la partida",
        "game_in_progress": "Partida en curso. Es tu turno.",
        "ai_thinking": "La IA está pensando...",
        "you_won": "🎉 ¡Has ganado! ¡Bien hecho!",
        "ai_won": "La IA ha ganado. ¡Inténtalo de nuevo!",
        "stalemate": "Ahogado.",
        "pricing_title": "💰 Precio",
        "price_tag": "Compra única: 20 USD",
        "price_desc": "Acceso de por vida y actualizaciones gratuitas incluidas.",
        "contact_title": "📞 Contacto y pago",
        "contact_email": "deslndes78@gmail.com",
        "contact_phone": "(509) 4738-5663 vía Prisme Transfer",
        "license_title": "📜 Licencia",
        "license_text": "**Todos los derechos reservados** – Copyright © 2026 GlobalInternet.py\nEste software es solo para uso personal. Se prohíbe la redistribución o reventa sin permiso.",
        "made_in_haiti": "🇭🇹 Hecho en Haití 🇭🇹",
        "made_by": "por <strong>GlobalInternet.py</strong><br>Desarrollador Python: Gesner Deslandes",
        "move_heading": "♟️ Haz tu movimiento",
        "move_instruction": "Selecciona una pieza y luego una casilla de destino en los menús desplegables. El panel de la izquierda explica cada movimiento.",
        "from_square": "Casilla de origen",
        "to_square": "Casilla de destino",
        "make_move": "Mover",
        "fullscreen": "⛶ PANTALLA COMPLETA",
        "score": "Puntuación (Ventaja blancas)",
        "demo_mode": "Modo demo (mostrar estrategias ganadoras)",
        "demo_easy": "Fácil – Horquilla",
        "demo_medium": "Medio – Clavada",
        "demo_hard": "Difícil – Jaque descubierto",
        "demo_move": "Movimiento {}: {} → {}",
        "demo_explanation": "Esta es una táctica ganadora.",
        "congratulations": "¡Felicitaciones! ¡Ganaste!",
        "owner_name": "Gesner Deslandes",
        "company_name": "GlobalInternet.py",
        "piece_names": {
            "pawn": "peón", "knight": "caballo", "bishop": "alfil",
            "rook": "torre", "queen": "reina", "king": "rey"
        },
        "move_explanation": "{player} movió {piece} de {from_sq} a {to_sq}.",
        "capture": " ¡Eso capturó el {captured} contrario!",
        "central": " Esto mueve la pieza a una casilla central, dándote más control.",
        "knight_central": " Los caballos suelen ser mejores en casillas centrales.",
        "pawn_advance": " Avanzar el peón a la 4ª fila es un buen movimiento de desarrollo.",
        "check": " ¡Este movimiento pone al oponente en jaque!",
        "invalid_move_no_piece": "No hay pieza en la casilla de origen.",
        "invalid_move_wrong_piece": "Esa no es tu pieza. Tú juegas con las blancas.",
        "invalid_move_illegal": "Movimiento ilegal. Intenta otro.",
        "invalid_move_format": "Formato de movimiento inválido. Usa nombres estándar como 'e2', 'e4'."
    },
    "ht": {
        "app_title": "♟️ Jwe Echèk Kont Machin nan ♟️",
        "app_subtitle": "Aprann lè w konprann chak mouvman",
        "sidebar_company": "GlobalInternet.py",
        "sidebar_owner": "Pwopriyetè: Gesner Deslandes",
        "game_controls": "♟️ Kontwòl jwèt",
        "ai_difficulty": "Difikilte AI",
        "easy": "fasil",
        "medium": "mwayen",
        "hard": "difisil",
        "restart": "🔄 Kòmanse ankò",
        "logout": "🚪 Dekonekte",
        "download_report": "📥 Telechaje rapò",
        "move_dashboard": "📊 Tablodbò mouvman",
        "your_last_move": "Dènye mouvman ou",
        "ai_last_move": "Dènye mouvman AI",
        "no_move": "Pa gen mouvman ankò.",
        "game_status": "Eta jwèt la",
        "game_in_progress": "Jwèt la ap mache. Se tou pa ou.",
        "ai_thinking": "AI ap reflechi...",
        "you_won": "🎉 Ou genyen! Félicitasyon!",
        "ai_won": "AI genyen. Eseye ankò!",
        "stalemate": "Pat.",
        "pricing_title": "💰 Pri",
        "price_tag": "Acha inik: $20 USD",
        "price_desc": "Gen aksè tout lavi ak mizajou gratis.",
        "contact_title": "📞 Kontak ak Peman",
        "contact_email": "deslndes78@gmail.com",
        "contact_phone": "(509) 4738-5663 via Prisme Transfer",
        "license_title": "📜 Lisans",
        "license_text": "**Tout dwa rezève** – Copyright © 2026 GlobalInternet.py\nLojisyèl sa a se pou itilizasyon pèsonèl sèlman. Redistribisyon oswa revant san pèmisyon entèdi.",
        "made_in_haiti": "🇭🇹 Fèt an Ayiti 🇭🇹",
        "made_by": "pa <strong>GlobalInternet.py</strong><br>Developè Python: Gesner Deslandes",
        "move_heading": "♟️ Fè mouvman ou",
        "move_instruction": "Chwazi yon pyès epi yon kare destinasyon nan lis ki anba a. Tablodbò a sou bò gòch eksplike chak mouvman.",
        "from_square": "Kare depa",
        "to_square": "Kare destinasyon",
        "make_move": "Jwe",
        "fullscreen": "⛶ EKRAN KONPLÈ",
        "score": "Nòt (Avantaj blan)",
        "demo_mode": "Mòd demo (montre estrateji pou genyen)",
        "demo_easy": "Fasil – Fouchèt",
        "demo_medium": "Mwayen – Klou",
        "demo_hard": "Difisil – Echèk dekouvri",
        "demo_move": "Mouvman {}: {} → {}",
        "demo_explanation": "Sa a se yon taktik pou genyen.",
        "congratulations": "Felisitasyon! Ou genyen!",
        "owner_name": "Gesner Deslandes",
        "company_name": "GlobalInternet.py",
        "piece_names": {
            "pawn": "pyon", "knight": "chwal", "bishop": "fou",
            "rook": "to", "queen": "dàm", "king": "wa"
        },
        "move_explanation": "{player} deplase {piece} soti {from_sq} ale {to_sq}.",
        "capture": " Sa pran {captured} advèsè a!",
        "central": " Sa deplase pyès la nan yon kare santral, ba w plis kontwòl.",
        "knight_central": " Chwal yo souvan pi bon nan kare santral yo.",
        "pawn_advance": " Avanse pyon an nan 4yèm ranje se yon bon mouvman devlopman.",
        "check": " Mouvman sa a mete advèsè a nan echèk!",
        "invalid_move_no_piece": "Pa gen pyès nan kare depa a.",
        "invalid_move_wrong_piece": "Se pa pyès ou. Ou ap jwe blan.",
        "invalid_move_illegal": "Mouvman ilegal. Eseye yon lòt mouvman.",
        "invalid_move_format": "Fòma mouvman pa bon. Itilize non estanda tankou 'e2', 'e4'."
    }
}

# ----------------------------------------------------------------------
# Helper functions (unchanged)
# ----------------------------------------------------------------------
def check_password():
    """Returns True if password is correct."""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if not st.session_state.get("password_correct", False):
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
    st.session_state["password_correct"] = False
    keys_to_clear = ["board", "move_history", "game_over", "winner", "difficulty",
                     "last_user_move", "last_ai_move", "last_user_explanation",
                     "last_ai_explanation", "user_turn", "celebration_triggered"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def piece_name(piece, lang):
    t = translations[lang]
    if piece is None:
        return "piece"
    names = {chess.PAWN: "pawn", chess.KNIGHT: "knight", chess.BISHOP: "bishop",
             chess.ROOK: "rook", chess.QUEEN: "queen", chess.KING: "king"}
    eng_name = names[piece.piece_type]
    return t["piece_names"].get(eng_name, eng_name)

def explain_move(board, move, player, lang):
    t = translations[lang]
    piece = board.piece_at(move.from_square)
    captured = board.piece_at(move.to_square)
    piece_str = piece_name(piece, lang) if piece else t["piece_names"]["pawn"]
    from_sq = chess.square_name(move.from_square)
    to_sq = chess.square_name(move.to_square)
    explanation = t["move_explanation"].format(player=player, piece=piece_str, from_sq=from_sq, to_sq=to_sq)
    if captured:
        captured_name = piece_name(captured, lang)
        explanation += t["capture"].format(captured=captured_name)
    else:
        to_sq = move.to_square
        if chess.square_rank(to_sq) in [3,4] and chess.square_file(to_sq) in [3,4]:
            explanation += t["central"]
        elif piece and piece.piece_type == chess.KNIGHT and chess.square_rank(to_sq) in [2,3,4,5]:
            explanation += t["knight_central"]
        elif piece and piece.piece_type == chess.PAWN and chess.square_rank(to_sq) == 4:
            explanation += t["pawn_advance"]
    board_copy = board.copy()
    board_copy.push(move)
    if board_copy.is_check():
        explanation += t["check"]
    return explanation

def ai_move(board, difficulty="easy"):
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
    else:
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

def compute_score(board):
    values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
    score = 0
    for piece_type, value in values.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board.pieces(piece_type, chess.BLACK)) * value
    return score

def generate_report(board, move_history, score, lang):
    t = translations[lang]
    report_lines = []
    report_lines.append(f"♟️ {t['app_title']} ♟️")
    report_lines.append(f"{t['app_subtitle']}\n")
    report_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Language: {lang}")
    report_lines.append(f"Difficulty: {t[st.session_state.difficulty]}")
    report_lines.append(f"Current score ({t['score']}): {score}\n")
    report_lines.append(f"FEN: {board.fen()}\n")
    report_lines.append("Move history with explanations:")
    for i, (player, move, explanation) in enumerate(move_history, 1):
        move_num = (i + 1) // 2 if player == "user" else i // 2
        turn = f"{move_num}. " if player == "user" else "..."
        report_lines.append(f"{turn}{player.upper()}: {chess.square_name(move.from_square)}→{chess.square_name(move.to_square)}")
        report_lines.append(f"   {explanation}")
    if not move_history:
        report_lines.append("No moves have been played yet.")
    report_lines.append("\n— Report generated by Play Chess Against the Machine —")
    return "\n".join(report_lines)

def get_demo_moves(difficulty, lang):
    t = translations[lang]
    if difficulty == "easy":
        return [
            ("e2", "e4", t["demo_move"].format(1, "e2", "e4") + " " + t["demo_explanation"]),
            ("d1", "h5", t["demo_move"].format(2, "d1", "h5") + " " + t["demo_explanation"]),
            ("f1", "c4", t["demo_move"].format(3, "f1", "c4") + " " + t["demo_explanation"]),
        ]
    elif difficulty == "medium":
        return [
            ("e2", "e4", t["demo_move"].format(1, "e2", "e4") + " " + t["demo_explanation"]),
            ("d1", "f3", t["demo_move"].format(2, "d1", "f3") + " " + t["demo_explanation"]),
            ("f1", "c4", t["demo_move"].format(3, "f1", "c4") + " " + t["demo_explanation"]),
        ]
    else:
        return [
            ("e2", "e4", t["demo_move"].format(1, "e2", "e4") + " " + t["demo_explanation"]),
            ("g1", "f3", t["demo_move"].format(2, "g1", "f3") + " " + t["demo_explanation"]),
            ("f1", "c4", t["demo_move"].format(3, "f1", "c4") + " " + t["demo_explanation"]),
        ]

# ----------------------------------------------------------------------
# Language selector
# ----------------------------------------------------------------------
lang_options = {
    "en": "🇺🇸 English",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "ht": "🇭🇹 Kreyòl"
}
selected_lang = st.sidebar.selectbox(
    "🌐 Language",
    options=list(lang_options.keys()),
    format_func=lambda x: lang_options[x],
    index=list(lang_options.keys()).index(st.session_state.lang)
)
if selected_lang != st.session_state.lang:
    st.session_state.lang = selected_lang
    st.session_state.last_user_move = None
    st.session_state.last_ai_move = None
    st.session_state.last_user_explanation = None
    st.session_state.last_ai_explanation = None
    st.rerun()

lang = st.session_state.lang
t = translations[lang]

# ----------------------------------------------------------------------
# Sidebar with branding, game controls, move dashboard, and logout
# ----------------------------------------------------------------------
with st.sidebar:
    col_flag, col_name = st.columns([1, 3])
    with col_flag:
        st.image("https://flagcdn.com/w320/ht.png", width=60)
    with col_name:
        st.markdown(f"### **{t['sidebar_company']}**")
        st.markdown(f"*{t['sidebar_owner']}*")
    
    st.divider()
    
    st.markdown(f"## {t['game_controls']}")
    difficulty = st.selectbox(
        t['ai_difficulty'],
        ["easy", "medium", "hard"],
        index=["easy","medium","hard"].index(st.session_state.difficulty),
        format_func=lambda x: t[x]
    )
    if difficulty != st.session_state.difficulty:
        st.session_state.difficulty = difficulty

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t['restart'], use_container_width=True):
            st.session_state.board = chess.Board()
            st.session_state.move_history = []
            st.session_state.game_over = False
            st.session_state.winner = None
            st.session_state.last_user_move = None
            st.session_state.last_ai_move = None
            st.session_state.last_user_explanation = None
            st.session_state.last_ai_explanation = None
            st.session_state.user_turn = True
            st.session_state.celebration_triggered = False
            st.rerun()
    with col2:
        if st.button(t['logout'], use_container_width=True):
            logout()

    demo_mode = st.checkbox(t['demo_mode'], value=st.session_state.demo_mode)
    if demo_mode != st.session_state.demo_mode:
        st.session_state.demo_mode = demo_mode
        st.rerun()
    
    report_text = generate_report(st.session_state.board, st.session_state.move_history, compute_score(st.session_state.board), lang)
    st.download_button(
        label=t['download_report'],
        data=report_text,
        file_name=f"chess_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.markdown("""
    <button class="fullscreen-btn" onclick="(window.parent.document.documentElement || document.documentElement).requestFullscreen();">⛶ FULLSCREEN</button>
    """, unsafe_allow_html=True)

    st.divider()
    
    st.markdown(f"## {t['move_dashboard']}")
    st.subheader(t['your_last_move'])
    if st.session_state.last_user_move:
        st.write(f"Move: {chess.square_name(st.session_state.last_user_move.from_square)} → {chess.square_name(st.session_state.last_user_move.to_square)}")
        st.write(st.session_state.last_user_explanation)
    else:
        st.write(t['no_move'])
    st.subheader(t['ai_last_move'])
    if st.session_state.last_ai_move:
        st.write(f"Move: {chess.square_name(st.session_state.last_ai_move.from_square)} → {chess.square_name(st.session_state.last_ai_move.to_square)}")
        st.write(st.session_state.last_ai_explanation)
    else:
        st.write(t['no_move'])

    st.divider()
    
    st.subheader(t['game_status'])
    if st.session_state.game_over:
        if st.session_state.winner == "user":
            st.success(t['you_won'])
        elif st.session_state.winner == "ai":
            st.error(t['ai_won'])
        else:
            st.info(t['stalemate'])
    else:
        st.info(t['game_in_progress'] if st.session_state.user_turn else t['ai_thinking'])
    
    score = compute_score(st.session_state.board)
    st.divider()
    st.markdown(f"## {t['score']}")
    # Fix empty label: add a hidden label with label_visibility="collapsed"
    st.metric(label="Score", value=score, delta=score if score != 0 else None, label_visibility="collapsed")
    
    st.divider()
    
    st.markdown(f"## {t['pricing_title']}")
    st.markdown(f"""
    <div class="price-tag">{t['price_tag']}</div>
    <div style="margin-top: 10px;">{t['price_desc']}</div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"## {t['contact_title']}")
    st.markdown(f"""
    **📧 {t['contact_email']}**  
    **📱 {t['contact_phone']}**  
    *Send payment and we'll activate your access.*
    """)
    
    st.divider()
    
    st.markdown(f"## {t['license_title']}")
    st.markdown(t['license_text'])
    
    st.divider()
    
    st.markdown(f"""
    <div style="text-align: center; margin-top: 20px;">
        <p>{t['made_in_haiti']}</p>
        <p><small>{t['made_by']}</small></p>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Demo mode display
# ----------------------------------------------------------------------
if st.session_state.demo_mode:
    st.markdown("---")
    st.markdown("### 🧠 Winning Strategies (Demo)")
    cols = st.columns(3)
    for i, diff in enumerate(["easy", "medium", "hard"]):
        with cols[i]:
            with st.expander(t[f"demo_{diff}"]):
                moves = get_demo_moves(diff, lang)
                for move in moves:
                    st.write(move[2])
    st.markdown("---")

# ----------------------------------------------------------------------
# Main area: header with flag, title, and chessboard
# ----------------------------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.image("https://flagcdn.com/w320/ht.png", width=100)
with col2:
    st.markdown(f"<h1 style='text-align: center; font-size: 3rem;'>{t['app_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'><em>{t['app_subtitle']}</em></p>", unsafe_allow_html=True)
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
# Game interface
# ----------------------------------------------------------------------
st.markdown(f"## {t['move_heading']}")
st.markdown(t['move_instruction'])

# Display chessboard as SVG
board = st.session_state.board
board_svg = chess.svg.board(board=board, size=400)
st.image(board_svg, width=400)

if st.session_state.game_over:
    # Victory celebration (only if user won and not yet triggered)
    if st.session_state.winner == "user" and not st.session_state.celebration_triggered:
        st.session_state.celebration_triggered = True
        balloon_html = f"""
        <div id="celebration-container" style="position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:9999;">
            <div class="celebration-text">
                {t['company_name']}<br>
                {t['owner_name']}<br>
                {t['congratulations']}
            </div>
        </div>
        <script>
            const container = document.getElementById('celebration-container');
            for(let i = 0; i < 50; i++) {{
                const balloon = document.createElement('div');
                balloon.className = 'balloon';
                balloon.style.left = Math.random() * window.innerWidth + 'px';
                balloon.style.animationDelay = Math.random() * 3 + 's';
                balloon.innerHTML = '🎈';
                container.appendChild(balloon);
            }}
            setTimeout(() => {{
                if(container) container.remove();
            }}, 5000);
        </script>
        """
        st.components.v1.html(balloon_html, height=0)
    st.stop()

# User move
if st.session_state.user_turn:
    squares = [chess.square_name(i) for i in range(64)]
    with st.form("move_form"):
        from_sq = st.selectbox(t['from_square'], squares, index=0)
        to_sq = st.selectbox(t['to_square'], squares, index=0)
        submitted = st.form_submit_button(t['make_move'])
    if submitted:
        try:
            if len(from_sq) != 2 or len(to_sq) != 2:
                st.error(t['invalid_move_format'])
            else:
                move = chess.Move.from_uci(from_sq + to_sq)
                piece = board.piece_at(move.from_square)
                if piece is None:
                    st.error(t['invalid_move_no_piece'])
                elif piece.color != chess.WHITE:
                    st.error(t['invalid_move_wrong_piece'])
                elif move not in board.legal_moves:
                    st.error(t['invalid_move_illegal'])
                else:
                    explanation = explain_move(board, move, "You", lang)
                    board.push(move)
                    st.session_state.last_user_move = move
                    st.session_state.last_user_explanation = explanation
                    st.session_state.move_history.append(("user", move, explanation))
                    if board.is_checkmate():
                        st.session_state.game_over = True
                        st.session_state.winner = "user"
                    elif board.is_stalemate() or board.is_insufficient_material():
                        st.session_state.game_over = True
                        st.session_state.winner = None
                    else:
                        st.session_state.user_turn = False
                    st.rerun()
        except Exception:
            st.error(t['invalid_move_format'])
else:
    with st.spinner(t['ai_thinking']):
        time.sleep(0.5)
        move = ai_move(board, st.session_state.difficulty)
        if move:
            explanation = explain_move(board, move, "AI", lang)
            board.push(move)
            st.session_state.last_ai_move = move
            st.session_state.last_ai_explanation = explanation
            st.session_state.move_history.append(("ai", move, explanation))
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
st.markdown(f"<div class='footer'>Made with ♟️ by GlobalInternet.py – {t['made_in_haiti']}</div>", unsafe_allow_html=True)
