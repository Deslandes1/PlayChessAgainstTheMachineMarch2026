"""
Chess Teaching App – Play against AI, learn the best move, save game history.
Multi‑language: English, Spanish, French, Haitian Creole.
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

# ------------------------------
# MULTI-LANGUAGE DICTIONARY
# ------------------------------
LANGUAGES = {
    "English": "en",
    "Español": "es",
    "Français": "fr",
    "Kreyòl Ayisyen": "ht"
}

TEXTS = {
    "en": {
        "login_title": "Login Required",
        "app_title": "Chess Teaching AI",
        "by_line": "by GlobalInternet.py",
        "password_label": "Enter password to play",
        "login_btn": "Login",
        "wrong_password": "Incorrect password. Access denied.",
        "main_title": "♟️ Chess Teaching AI",
        "subtitle": "Learn the best move from Stockfish, then play against it",
        "sidebar_company": "GlobalInternet.py",
        "sidebar_tutor": "Smart Chess Tutor",
        "founder": "Founder & Developer",
        "name": "Gesner Deslandes",
        "whatsapp": "WhatsApp",
        "email": "Email",
        "website": "Website",
        "price_label": "Price",
        "price_value": "$149 USD (lifetime license)",
        "copyright": "All Rights Reserved",
        "logout_btn": "Logout",
        "piece_reference": "♟️ Piece Reference",
        "piece_table": """
        | Piece | Symbol | Letter |
        |-------|--------|--------|
        | King | ♔ | K |
        | Queen | ♕ | Q |
        | Rook | ♖ | R |
        | Bishop | ♗ | B |
        | Knight | ♘ | N |
        | Pawn | ♙ | (no letter) |
        """,
        "piece_caption": "In notation, 'N' stands for Knight (because 'K' is King).",
        "notation_expander": "📖 How to read chess moves (e.g., Nh3)",
        "notation_text": """
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
        """,
        "difficulty_label": "🎮 Chess Game Level:",
        "beginner": "Beginner",
        "intermediate": "Intermediate",
        "advanced": "Advanced",
        "strategies_title": "🧠 Three winning moves/strategies for this level",
        "strategies": {
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
        },
        "ai_teaching": "🎓 AI Teaching",
        "best_move_suggestion": "💡 **Best move suggestion:** {}",
        "ai_thinking_turn": "AI is thinking... (Black's turn)",
        "your_move": "🎯 Your Move",
        "choose_move": "Choose a move:",
        "make_move_btn": "▶️ Make Move",
        "no_legal_moves": "No legal moves! Game over.",
        "game_finished": "Game finished. Start a new game below.",
        "ai_thinking_wait": "AI is thinking... Please wait.",
        "save_game": "📥 Save Game",
        "download_btn": "Download Move History",
        "new_game_btn": "🔄 New Game",
        "checkmate_white_wins": "🏆 Checkmate! White (You) wins!",
        "checkmate_black_wins": "🏆 Checkmate! Black (AI) wins.",
        "stalemate": "♟️ Stalemate! Game drawn.",
        "insufficient_material": "♟️ Insufficient material – drawn.",
        "your_king_check": "⚠️ Your king is in CHECK! Defend it.",
        "ai_king_check": "⚠️ AI's king is in CHECK!",
        "your_turn": "Your turn – choose a move from the dropdown.",
        "ai_turn": "AI is thinking – it will move shortly.",
        "game_over_balloons": "Game Over! Click 'New Game' to play again.",
        "how_to_learn": "📘 **How to learn:** The AI shows the best move suggestion above. You can pick that move or any other legal move. After your move, the AI will play its best response. Download your move history anytime.",
        "report_header": "Game Moves:",
        "no_moves": "No moves played yet."
    },
    "es": {
        "login_title": "Inicio de sesión requerido",
        "app_title": "Enseñanza de Ajedrez IA",
        "by_line": "por GlobalInternet.py",
        "password_label": "Ingrese la contraseña para jugar",
        "login_btn": "Iniciar sesión",
        "wrong_password": "Contraseña incorrecta. Acceso denegado.",
        "main_title": "♟️ Enseñanza de Ajedrez IA",
        "subtitle": "Aprende la mejor jugada de Stockfish, luego juega contra él",
        "sidebar_company": "GlobalInternet.py",
        "sidebar_tutor": "Tutor inteligente de ajedrez",
        "founder": "Fundador y Desarrollador",
        "name": "Gesner Deslandes",
        "whatsapp": "WhatsApp",
        "email": "Correo",
        "website": "Sitio web",
        "price_label": "Precio",
        "price_value": "$149 USD (licencia de por vida)",
        "copyright": "Todos los derechos reservados",
        "logout_btn": "Cerrar sesión",
        "piece_reference": "♟️ Referencia de piezas",
        "piece_table": """
        | Pieza | Símbolo | Letra |
        |-------|---------|-------|
        | Rey | ♔ | K |
        | Reina | ♕ | Q |
        | Torre | ♖ | R |
        | Alfil | ♗ | B |
        | Caballo | ♘ | N |
        | Peón | ♙ | (sin letra) |
        """,
        "piece_caption": "En notación, 'N' representa al caballo (porque 'K' es el rey).",
        "notation_expander": "📖 Cómo leer movimientos de ajedrez (ej. Nh3)",
        "notation_text": """
        **Letras de piezas:**
        - **K** = Rey
        - **Q** = Reina
        - **R** = Torre
        - **B** = Alfil
        - **N** = Caballo (porque K ya es Rey)
        - (sin letra para peones, ej. `e4` significa peón a e4)
        
        **Coordenadas:** Cada casilla tiene una letra (a-h) para columna y un número (1-8) para fila.
        - `Nh3` = Caballo se mueve a h3
        - `Bxf7` = Alfil captura en f7
        - `O-O` = enroque corto, `O-O-O` = enroque largo
        - `+` = jaque, `#` = jaque mate.
        """,
        "difficulty_label": "🎮 Nivel de ajedrez:",
        "beginner": "Principiante",
        "intermediate": "Intermedio",
        "advanced": "Avanzado",
        "strategies_title": "🧠 Tres movimientos/estrategias ganadoras para este nivel",
        "strategies": {
            "Beginner": [
                "1. **Mate del tonto (2 movimientos):** 1. f3 e5 2. g4?? Qh4# – Las negras dan mate en dos. Aprende a ver reyes desprotegidos.",
                "2. **Mate del pastor (4 movimientos):** 1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6?? 4. Qxf7# – Ataca la casilla f7 temprano.",
                "3. **Defensa contra mate de cuatro movimientos:** Como blancas, juega 1. e4, 2. Bc4, 3. Qf3, 4. Qxf7# si las negras no defienden f7."
            ],
            "Intermediate": [
                "1. **Ataque Fried Liver (Giro italiano):** 1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 4. Ng5 d5 5. exd5 Nxd5?? 6. Nxf7! ganando la dama.",
                "2. **Gambito de dama aceptado:** 1. d4 d5 2. c4 dxc4 3. e3 – desarrolla rápido y recupera el peón con piezas activas.",
                "3. **Defensa India de Rey:** Como negras, juega 1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 – sólida y contraatacante."
            ],
            "Advanced": [
                "1. **Ataque Yugoslavo (Dragón siciliano):** 1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 g6 6. Be3 Bg7 7. f3 – ataque agresivo en el flanco de rey.",
                "2. **Ataque Marshall (Ruy López):** 1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 O-O 8. c3 d5 – juego táctico agudo.",
                "3. **Variante Winawer (Defensa francesa):** 1. e4 e6 2. d4 d5 3. Nc3 Bb4 4. e5 c5 5. a3 Bxc3+ 6. bxc3 – estructura de peones desequilibrada."
            ]
        },
        "ai_teaching": "🎓 Enseñanza IA",
        "best_move_suggestion": "💡 **Mejor movimiento sugerido:** {}",
        "ai_thinking_turn": "La IA está pensando... (turno de negras)",
        "your_move": "🎯 Tu movimiento",
        "choose_move": "Elige un movimiento:",
        "make_move_btn": "▶️ Hacer movimiento",
        "no_legal_moves": "¡No hay movimientos legales! Juego terminado.",
        "game_finished": "Juego terminado. Comienza uno nuevo abajo.",
        "ai_thinking_wait": "La IA está pensando... Espera.",
        "save_game": "📥 Guardar partida",
        "download_btn": "Descargar historial de movimientos",
        "new_game_btn": "🔄 Nueva partida",
        "checkmate_white_wins": "🏆 ¡Jaque mate! ¡Blancas (tú) ganan!",
        "checkmate_black_wins": "🏆 ¡Jaque mate! Negras (IA) ganan.",
        "stalemate": "♟️ Ahogado. Partida tablas.",
        "insufficient_material": "♟️ Material insuficiente – tablas.",
        "your_king_check": "⚠️ ¡Tu rey está en JAQUE! Defiéndelo.",
        "ai_king_check": "⚠️ ¡El rey de la IA está en JAQUE!",
        "your_turn": "Tu turno – elige un movimiento del menú desplegable.",
        "ai_turn": "La IA está pensando – se moverá pronto.",
        "game_over_balloons": "¡Juego terminado! Haz clic en 'Nueva partida' para jugar de nuevo.",
        "how_to_learn": "📘 **Cómo aprender:** La IA muestra la mejor jugada sugerida arriba. Puedes elegir esa jugada o cualquier otra legal. Después de tu movimiento, la IA jugará su mejor respuesta. Descarga tu historial de movimientos en cualquier momento.",
        "report_header": "Movimientos de la partida:",
        "no_moves": "Aún no se han jugado movimientos."
    },
    "fr": {
        "login_title": "Connexion requise",
        "app_title": "Enseignement des échecs IA",
        "by_line": "par GlobalInternet.py",
        "password_label": "Entrez le mot de passe pour jouer",
        "login_btn": "Se connecter",
        "wrong_password": "Mot de passe incorrect. Accès refusé.",
        "main_title": "♟️ Enseignement des échecs IA",
        "subtitle": "Apprenez le meilleur coup de Stockfish, puis jouez contre lui",
        "sidebar_company": "GlobalInternet.py",
        "sidebar_tutor": "Tuteur d'échecs intelligent",
        "founder": "Fondateur et développeur",
        "name": "Gesner Deslandes",
        "whatsapp": "WhatsApp",
        "email": "Email",
        "website": "Site web",
        "price_label": "Prix",
        "price_value": "149 $ USD (licence à vie)",
        "copyright": "Tous droits réservés",
        "logout_btn": "Déconnexion",
        "piece_reference": "♟️ Référence des pièces",
        "piece_table": """
        | Pièce | Symbole | Lettre |
        |-------|---------|--------|
        | Roi | ♔ | K |
        | Dame | ♕ | Q |
        | Tour | ♖ | R |
        | Fou | ♗ | B |
        | Cavalier | ♘ | N |
        | Pion | ♙ | (pas de lettre) |
        """,
        "piece_caption": "Dans la notation, 'N' représente le cavalier (parce que 'K' est le roi).",
        "notation_expander": "📖 Comment lire les coups d'échecs (ex. Nh3)",
        "notation_text": """
        **Lettres des pièces :**
        - **K** = Roi
        - **Q** = Dame
        - **R** = Tour
        - **B** = Fou
        - **N** = Cavalier (car K est déjà roi)
        - (pas de lettre pour les pions, ex. `e4` signifie pion en e4)
        
        **Coordonnées :** Chaque case a une lettre (a-h) pour la colonne et un chiffre (1-8) pour la rangée.
        - `Nh3` = Cavalier se déplace en h3
        - `Bxf7` = Fou capture en f7
        - `O-O` = petit roque, `O-O-O` = grand roque
        - `+` = échec, `#` = échec et mat.
        """,
        "difficulty_label": "🎮 Niveau d'échecs :",
        "beginner": "Débutant",
        "intermediate": "Intermédiaire",
        "advanced": "Avancé",
        "strategies_title": "🧠 Trois coups/stratégies gagnants pour ce niveau",
        "strategies": {
            "Beginner": [
                "1. **Mat du fou (2 coups) :** 1. f3 e5 2. g4?? Dxh4# – Les noirs donnent mat en deux coups. Apprenez à repérer les rois non protégés.",
                "2. **Mat du berger (4 coups) :** 1. e4 e5 2. Dh5 Cc6 3. Fc4 Cf6?? 4. Dxf7# – Attaquez la case f7 tôt.",
                "3. **Défense contre le mat en quatre coups :** Avec les blancs, jouez 1. e4, 2. Fc4, 3. Df3, 4. Dxf7# si les noirs ne défendent pas f7."
            ],
            "Intermediate": [
                "1. **Attaque Fried Liver (Giuoco piano) :** 1. e4 e5 2. Cf3 Cc6 3. Fc4 Cf6 4. Cg5 d5 5. exd5 Cxd5?? 6. Cxf7! gagnant la dame.",
                "2. **Gambit dame accepté :** 1. d4 d5 2. c4 dxc4 3. e3 – développez rapidement et récupérez le pion avec des pièces actives.",
                "3. **Défense est-indienne :** Avec les noirs, jouez 1. d4 Cf6 2. c4 g6 3. Cc3 Fg7 4. e4 d6 – solide et contre-attaquant."
            ],
            "Advanced": [
                "1. **Attaque yougoslave (Dragon sicilien) :** 1. e4 c5 2. Cf3 d6 3. d4 cxd4 4. Cxd4 Cf6 5. Cc3 g6 6. Fe3 Fg7 7. f3 – attaque agressive côté roi.",
                "2. **Attaque Marshall (Ruy Lopez) :** 1. e4 e5 2. Cf3 Cc6 3. Fb5 a6 4. Fa4 Cf6 5. O-O Fe7 6. Te1 b5 7. Fb3 O-O 8. c3 d5 – jeu tactique aigu.",
                "3. **Variante Winawer (Défense française) :** 1. e4 e6 2. d4 d5 3. Cc3 Fb4 4. e5 c5 5. a3 Fxc3+ 6. bxc3 – structure de pions déséquilibrée."
            ]
        },
        "ai_teaching": "🎓 Enseignement IA",
        "best_move_suggestion": "💡 **Meilleur coup suggéré :** {}",
        "ai_thinking_turn": "L'IA réfléchit... (tour des noirs)",
        "your_move": "🎯 Votre coup",
        "choose_move": "Choisissez un coup :",
        "make_move_btn": "▶️ Jouer le coup",
        "no_legal_moves": "Aucun coup légal ! Partie terminée.",
        "game_finished": "Partie terminée. Commencez-en une nouvelle ci-dessous.",
        "ai_thinking_wait": "L'IA réfléchit... Veuillez patienter.",
        "save_game": "📥 Sauvegarder la partie",
        "download_btn": "Télécharger l'historique des coups",
        "new_game_btn": "🔄 Nouvelle partie",
        "checkmate_white_wins": "🏆 Échec et mat ! Les blancs (vous) gagnent !",
        "checkmate_black_wins": "🏆 Échec et mat ! Les noirs (IA) gagnent.",
        "stalemate": "♟️ Pat ! Partie nulle.",
        "insufficient_material": "♟️ Matériel insuffisant – nulle.",
        "your_king_check": "⚠️ Votre roi est en ÉCHEC ! Défendez-le.",
        "ai_king_check": "⚠️ Le roi de l'IA est en ÉCHEC !",
        "your_turn": "Votre tour – choisissez un coup dans la liste déroulante.",
        "ai_turn": "L'IA réfléchit – elle va bientôt jouer.",
        "game_over_balloons": "Partie terminée ! Cliquez sur 'Nouvelle partie' pour rejouer.",
        "how_to_learn": "📘 **Comment apprendre :** L'IA montre le meilleur coup suggéré ci-dessus. Vous pouvez choisir ce coup ou tout autre coup légal. Après votre coup, l'IA jouera sa meilleure réponse. Téléchargez votre historique à tout moment.",
        "report_header": "Coups de la partie :",
        "no_moves": "Aucun coup joué pour l'instant."
    },
    "ht": {
        "login_title": "Nesesite koneksyon",
        "app_title": "Ansèyman Echèk AI",
        "by_line": "pa GlobalInternet.py",
        "password_label": "Antre modpas pou jwe",
        "login_btn": "Konekte",
        "wrong_password": "Modpas pa bon. Aksè refize.",
        "main_title": "♟️ Ansèyman Echèk AI",
        "subtitle": "Aprann pi bon mouvman an nan men Stockfish, apre jwe kont li",
        "sidebar_company": "GlobalInternet.py",
        "sidebar_tutor": "Titè echèk entèlijan",
        "founder": "Fondatè ak Devlopè",
        "name": "Gesner Deslandes",
        "whatsapp": "WhatsApp",
        "email": "Imèl",
        "website": "Sitwèb",
        "price_label": "Pri",
        "price_value": "149 $ USD (lisans tout lavi)",
        "copyright": "Tout dwa rezève",
        "logout_btn": "Dekonekte",
        "piece_reference": "♟️ Referans pyès",
        "piece_table": """
        | Pyès | Senbòl | Lèt |
        |-------|--------|------|
        | Wa | ♔ | K |
        | Rèn | ♕ | Q |
        | Chat | ♖ | R |
        | Fou | ♗ | B |
        | Kavalyé | ♘ | N |
        | Pyon | ♙ | (pa gen lèt) |
        """,
        "piece_caption": "Nan notasyon, 'N' vle di kavalyé (piske 'K' se wa).",
        "notation_expander": "📖 Kijan li mouvman echèk (egzanp Nh3)",
        "notation_text": """
        **Lèt pyès yo:**
        - **K** = Wa
        - **Q** = Rèn
        - **R** = Chat
        - **B** = Fou
        - **N** = Kavalyé (piske K deja itilize pou Wa)
        - (pa gen lèt pou pyon, eg. `e4` vle di pyon ale e4)
        
        **Kowòdone:** Chak kare gen yon lèt (a-h) pou kolòn ak yon nimewo (1-8) pou ranje.
        - `Nh3` = Kavalyé ale sou kare h3
        - `Bxf7` = Fou pran sou f7
        - `O-O` = ti roke, `O-O-O` = gwo roke
        - `+` = echèk, `#` = echèk e mat.
        """,
        "difficulty_label": "🎮 Nivo jwèt echèk:",
        "beginner": "Debitan",
        "intermediate": "Entèmedyè",
        "advanced": "Avanse",
        "strategies_title": "🧠 Twa mouvman/strateji pou genyen nan nivo sa a",
        "strategies": {
            "Beginner": [
                "1. **Mat moun sòt (2 mouvman):** 1. f3 e5 2. g4?? Qh4# – Nwa yo bay mat an de mouvman. Aprann wè wa ki pa pwoteje.",
                "2. **Mat bèje (4 mouvman):** 1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6?? 4. Qxf7# – Atake kare f7 byen bonè.",
                "3. **Defans kont mat kat mouvman:** Kòm Blan, jwe 1. e4, 2. Bc4, 3. Qf3, 4. Qxf7# si Nwa pa defann f7."
            ],
            "Intermediate": [
                "1. **Atak Fried Liver (Jwèt Italyen):** 1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 4. Ng5 d5 5. exd5 Nxd5?? 6. Nxf7! genyen rèn nan.",
                "2. **Gambit Rèn aksepte:** 1. d4 d5 2. c4 dxc4 3. e3 – devlope vit epi reprann pyon an ak pyès aktif.",
                "3. **Defans Endyen Wa:** Kòm Nwa, jwe 1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 – solid ak kont-atak."
            ],
            "Advanced": [
                "1. **Atak Yougoslav (Dragon Sicilyen):** 1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 g6 6. Be3 Bg7 7. f3 – atak agresif sou bò wa.",
                "2. **Atak Marshall (Ruy Lopez):** 1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 O-O 8. c3 d5 – jwèt taktik byen file.",
                "3. **Varyant Winawer (Defans Franse):** 1. e4 e6 2. d4 d5 3. Nc3 Bb4 4. e5 c5 5. a3 Bxc3+ 6. bxc3 – estrikti pyon dezekilibre."
            ]
        },
        "ai_teaching": "🎓 Ansèyman AI",
        "best_move_suggestion": "💡 **Pi bon mouvman sijere:** {}",
        "ai_thinking_turn": "AI ap panse... (tou Nwa)",
        "your_move": "🎯 Mouvman ou",
        "choose_move": "Chwazi yon mouvman:",
        "make_move_btn": "▶️ Fè mouvman",
        "no_legal_moves": "Pa gen mouvman legal! Jwèt fini.",
        "game_finished": "Jwèt fini. Kòmanse yon nouvo anba a.",
        "ai_thinking_wait": "AI ap panse... Tanpri tann.",
        "save_game": "📥 Sove jwèt",
        "download_btn": "Telechaje istwa mouvman yo",
        "new_game_btn": "🔄 Nouvo jwèt",
        "checkmate_white_wins": "🏆 Echèk e mat! Blan (ou) genyen!",
        "checkmate_black_wins": "🏆 Echèk e mat! Nwa (AI) genyen.",
        "stalemate": "♟️ Pat! Jwèt egal.",
        "insufficient_material": "♟️ Materyel ensifizan – egalite.",
        "your_king_check": "⚠️ Wa ou nan ECHÈK! Defann li.",
        "ai_king_check": "⚠️ Wa AI a nan ECHÈK!",
        "your_turn": "Tou ou – chwazi yon mouvman nan lis la.",
        "ai_turn": "AI ap panse – li pral jwe talè.",
        "game_over_balloons": "Jwèt fini! Klike sou 'Nouvo jwèt' pou jwe ankò.",
        "how_to_learn": "📘 **Kijan pou aprann:** AI montre pi bon mouvman sijere anlè a. Ou ka chwazi mouvman sa a oswa nenpòt lòt mouvman legal. Apre mouvman ou, AI ap jwe pi bon repons li. Telechaje istwa mouvman ou nenpòt lè.",
        "report_header": "Mouvman jwèt yo:",
        "no_moves": "Pa gen mouvman jwe ankò."
    }
}

def get_text(key, lang, **kwargs):
    text = TEXTS[lang].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

# ------------------------------
# LANGUAGE SELECTION & SESSION STATE
# ------------------------------
if "language" not in st.session_state:
    st.session_state.language = "en"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ------------------------------
# LOGIN PAGE
# ------------------------------
if not st.session_state.authenticated:
    st.title(f"🔐 {get_text('login_title', 'en')}")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        show_haitian_flag(150)
        st.markdown(f"<h2 style='text-align: center;'>{get_text('app_title', 'en')}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{get_text('by_line', 'en')}</p>", unsafe_allow_html=True)
        password_input = st.text_input(get_text('password_label', 'en'), type="password")
        if st.button(get_text('login_btn', 'en')):
            if password_input == "20082010":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error(get_text('wrong_password', 'en'))
    st.stop()

# ------------------------------
# MAIN APP (after login)
# ------------------------------
# Language selector in sidebar (after login)
lang = st.sidebar.selectbox(
    "🌐 Language / Langue / Idioma / Lang",
    options=list(LANGUAGES.keys()),
    index=list(LANGUAGES.values()).index(st.session_state.language)
)
st.session_state.language = LANGUAGES[lang]
t = TEXTS[st.session_state.language]

# Display main title and flag
col_flag, col_title = st.columns([1, 3])
with col_flag:
    show_haitian_flag(120)
with col_title:
    st.markdown(f"<h1>{t['main_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"*{t['subtitle']}*")

# ------------------------------
# SIDEBAR CONTENT
# ------------------------------
with st.sidebar:
    st.markdown(f"## 🇭🇹 {t['sidebar_company']}")
    show_haitian_flag(80)
    st.markdown(f"### {t['sidebar_tutor']}")
    st.markdown("---")
    st.markdown(f"**{t['founder']}:**")
    st.markdown(t['name'])
    st.markdown(f"📞 **{t['whatsapp']}:** [509 4738-5663](https://wa.me/50947385663)")
    st.markdown(f"📧 **{t['email']}:** deslandes78@gmail.com")
    st.markdown(f"🌐 **{t['website']}:** [www.globalinternet.py](https://www.globalinternet.py)")
    st.markdown("---")
    st.markdown(f"### {t['price_label']}")
    st.markdown(f"**{t['price_value']}**")
    st.markdown("---")
    st.markdown(f"### {t['piece_reference']}")
    st.markdown(t['piece_table'])
    st.caption(t['piece_caption'])
    st.markdown("---")
    st.markdown(f"### © 2025 GlobalInternet.py")
    st.markdown(t['copyright'])
    st.markdown("---")
    if st.button(t['logout_btn'], use_container_width=True):
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
        st.session_state.stockfish.set_skill_level(10)
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
        return t['no_moves']
    history_str = f"{t['report_header']}\n"
    for i, move in enumerate(st.session_state.move_history):
        if i % 2 == 0:
            history_str += f"{i//2 + 1}. {move} "
        else:
            history_str += f"{move}\n"
    if len(st.session_state.move_history) % 2 == 1:
        history_str += "..."
    return history_str

def set_difficulty(level):
    skill_map = {"Beginner": 1, "Intermediate": 10, "Advanced": 18}
    st.session_state.stockfish.set_skill_level(skill_map[level])
    st.session_state.difficulty = level

# ------------------------------
# MOVE NOTATION EXPANDER
# ------------------------------
with st.expander(t['notation_expander']):
    st.markdown(t['notation_text'])

# ------------------------------
# DIFFICULTY SELECTOR
# ------------------------------
difficulty = st.radio(
    t['difficulty_label'],
    [t['beginner'], t['intermediate'], t['advanced']],
    index=[t['beginner'], t['intermediate'], t['advanced']].index(t[st.session_state.difficulty.lower()]),
    horizontal=True
)
# Map display name back to internal key
diff_map = {t['beginner']: "Beginner", t['intermediate']: "Intermediate", t['advanced']: "Advanced"}
selected_diff = diff_map[difficulty]
if selected_diff != st.session_state.difficulty:
    set_difficulty(selected_diff)
    st.rerun()

# ------------------------------
# WINNING STRATEGIES
# ------------------------------
st.markdown(f"### {t['strategies_title']}")
strategies_list = t['strategies'][st.session_state.difficulty]
for i, strat in enumerate(strategies_list, 1):
    st.markdown(f"{i}. {strat}")
st.markdown("---")

# ------------------------------
# GAME BOARD AND CONTROLS
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
    st.markdown(f"### {t['ai_teaching']}")
    if not st.session_state.game_over and st.session_state.board.turn == chess.WHITE:
        best_move = get_best_move()
        if best_move:
            best_san = get_move_san(best_move)
            st.info(t['best_move_suggestion'].format(best_san))
            st.caption("This is the strongest move according to Stockfish. You can choose it or any other legal move.")
        else:
            st.warning("No best move found.")
    else:
        st.info(t['ai_thinking_turn'])

    st.markdown("---")
    st.markdown(f"### {t['your_move']}")
    if not st.session_state.game_over and st.session_state.board.turn == chess.WHITE and not st.session_state.ai_thinking:
        legal_moves = list(st.session_state.board.legal_moves)
        if legal_moves:
            move_options = {}
            for move in legal_moves:
                san = get_move_san(move)
                move_options[san] = move
            selected_san = st.selectbox(t['choose_move'], list(move_options.keys()))
            if st.button(t['make_move_btn'], use_container_width=True):
                move = move_options[selected_san]
                st.session_state.board.push(move)
                update_move_history(move)
                st.session_state.last_move = move
                st.rerun()
        else:
            st.error(t['no_legal_moves'])
            st.session_state.game_over = True
    elif st.session_state.game_over:
        st.info(t['game_finished'])
    else:
        st.info(t['ai_thinking_wait'])

    st.markdown("---")
    st.markdown(f"### {t['save_game']}")
    history_text = save_game_history()
    st.download_button(
        label=t['download_btn'],
        data=history_text,
        file_name=f"chess_game_{time.strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.markdown("---")
    if st.button(t['new_game_btn'], use_container_width=True):
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
            st.success(t['checkmate_black_wins'])
        else:
            st.success(t['checkmate_white_wins'])
    elif st.session_state.board.is_stalemate():
        st.session_state.game_over = True
        st.info(t['stalemate'])
    elif st.session_state.board.is_insufficient_material():
        st.session_state.game_over = True
        st.info(t['insufficient_material'])

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
            st.warning(t['your_king_check'])
        else:
            st.warning(t['ai_king_check'])
    else:
        if st.session_state.board.turn == chess.WHITE:
            st.info(t['your_turn'])
        else:
            st.info(t['ai_turn'])
else:
    st.balloons()
    st.markdown(f"### {t['game_over_balloons']}")

st.markdown("---")
st.markdown(t['how_to_learn'])
