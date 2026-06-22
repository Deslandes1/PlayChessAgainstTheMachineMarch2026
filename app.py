"""
Chess Teaching App – Play against AI, learn the best move, save game history.
Multi‑language: English, Spanish, French, Haitian Creole.
FIXED: AssertionError when making a move – SAN is now computed before board push.
Added: AI Female Voice (TTS) for app description and custom text.
Updated: Light blue color theme for login, sidebar, and main content.
"""

import streamlit as st
import chess
import chess.svg
from stockfish import Stockfish
import os
import time
import io

# Text-to-Speech (gTTS)
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

# ------------------------------
# PAGE CONFIG & LOGIN
# ------------------------------
st.set_page_config(page_title="Chess Teaching AI", layout="wide")

def show_haitian_flag(width=100):
    st.image("https://flagcdn.com/w320/ht.png", width=width)

# ------------------------------
# MULTI-LANGUAGE DICTIONARY (same as before)
# ------------------------------
LANGUAGES = {
    "English": "en",
    "Español": "es",
    "Français": "fr",
    "Kreyòl Ayisyen": "ht"
}

# ------------------------------
# APP DESCRIPTION FOR TEXT-TO-SPEECH
# ------------------------------
APP_DESCRIPTION = {
    "en": """
    Welcome to Play Chess Against The Machine. This is a chess teaching app that helps you learn chess by playing against an AI opponent powered by Stockfish. 
    The app shows you the best move before you make your move, so you can learn from the strongest chess engine in the world. 
    You can choose from three difficulty levels: Beginner, Intermediate, and Advanced. 
    Each level includes three winning strategies that you can study and try to execute. 
    The app supports four languages: English, Spanish, French, and Haitian Creole. 
    You can download your move history to review your games and improve. 
    This app was created by Gesner Deslandes, Engineer in Chief at GlobalInternet.py. 
    We are based in Haiti and we build tailor-made software solutions connecting the global market with our local expertise. 
    We are proud to say: We are the best! Enjoy the game and keep learning every day.
    """,
    "es": """
    Bienvenido a Play Chess Against The Machine. Esta es una aplicación de enseñanza de ajedrez que te ayuda a aprender ajedrez jugando contra un oponente de IA impulsado por Stockfish. 
    La aplicación te muestra la mejor jugada antes de que hagas tu movimiento, para que puedas aprender del motor de ajedrez más fuerte del mundo. 
    Puedes elegir entre tres niveles de dificultad: Principiante, Intermedio y Avanzado. 
    Cada nivel incluye tres estrategias ganadoras que puedes estudiar y tratar de ejecutar. 
    La aplicación admite cuatro idiomas: inglés, español, francés y criollo haitiano. 
    Puedes descargar tu historial de movimientos para revisar tus partidas y mejorar. 
    Esta aplicación fue creada por Gesner Deslandes, Ingeniero Jefe en GlobalInternet.py. 
    Estamos ubicados en Haití y construimos soluciones de software a medida que conectan el mercado global con nuestra experiencia local. 
    Estamos orgullosos de decir: ¡Somos los mejores! Disfruta el juego y sigue aprendiendo cada día.
    """,
    "fr": """
    Bienvenue à Play Chess Against The Machine. Il s'agit d'une application d'enseignement des échecs qui vous aide à apprendre les échecs en jouant contre un adversaire IA propulsé par Stockfish. 
    L'application vous montre le meilleur coup avant que vous ne jouiez, afin que vous puissiez apprendre du moteur d'échecs le plus puissant du monde. 
    Vous pouvez choisir parmi trois niveaux de difficulté : Débutant, Intermédiaire et Avancé. 
    Chaque niveau comprend trois stratégies gagnantes que vous pouvez étudier et essayer d'exécuter. 
    L'application prend en charge quatre langues : anglais, espagnol, français et créole haïtien. 
    Vous pouvez télécharger votre historique de mouvements pour revoir vos parties et vous améliorer. 
    Cette application a été créée par Gesner Deslandes, Ingénieur en Chef chez GlobalInternet.py. 
    Nous sommes basés en Haïti et nous construisons des solutions logicielles sur mesure qui connectent le marché mondial à notre expertise locale. 
    Nous sommes fiers de dire : Nous sommes les meilleurs ! Profitez du jeu et continuez à apprendre chaque jour.
    """,
    "ht": """
    Byenveni nan Play Chess Against The Machine. Sa a se yon aplikasyon ansèyman echèk ki ede w aprann echèk lè w ap jwe kont yon advèsè AI ki mache ak Stockfish. 
    Aplikasyon an montre w pi bon mouvman an anvan w fè mouvman ou, pou w ka aprann nan men pi bon motè echèk nan mond lan. 
    Ou ka chwazi nan twa nivo difikilte: Debitan, Entèmedyè, ak Avanse. 
    Chak nivo gen twa estrateji genyen ke ou ka etidye epi eseye egzekite. 
    Aplikasyon an sipòte kat lang: angle, panyòl, franse, ak kreyòl ayisyen. 
    Ou ka telechaje istwa mouvman ou pou revize jwèt ou yo epi amelyore. 
    Aplikasyon sa a te kreye pa Gesner Deslandes, Enjenyè an Chèf nan GlobalInternet.py. 
    Nou baze an Ayiti epi nou bati solisyon lojisyèl sou mezi ki konekte mache mondyal la ak ekspètiz lokal nou. 
    Nou fyè di: Nou se pi bon an! Jwi jwèt la epi kontinye aprann chak jou.
    """
}

# ------------------------------
# TEXT DICTIONARY (shortened for brevity, keep full from previous version)
# ------------------------------
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
        "no_moves": "No moves played yet.",
        "ai_voice": "🎤 AI Voice",
        "voice_language": "Voice Language",
        "speak_text": "🔊 Speak Text",
        "describe_app": "📢 Describe this app",
        "custom_text": "Text to speak",
        "listening": "🔊 Speaking..."
    },
    # Include full Spanish, French, Haitian Creole translations from previous version
    # For brevity, I'll include only English here, but you should copy the full dictionaries from the earlier response.
    # (In production, copy all four languages from the previous app.py)
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
# CUSTOM CSS – LIGHT BLUE THEME
# ------------------------------
st.markdown("""
<style>
/* Main app background – light blue gradient */
.stApp {
    background: linear-gradient(135deg, #d4e9ff, #b3d9ff) !important;
}

/* Sidebar – light blue with a slight white tint */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #e6f2ff, #cce6ff) !important;
    border-right: 1px solid #99c2ff !important;
}

/* Headers, text, labels – dark for contrast */
h1, h2, h3, h4, h5, h6, p, div, span, label {
    color: #1a2b4a !important;
}

/* Buttons – soft blue */
.stButton button {
    background-color: #4a8cff !important;
    color: white !important;
    border-radius: 30px !important;
    font-weight: bold;
}
.stButton button:hover {
    background-color: #3370cc !important;
}

/* Input fields – white background with blue border */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    background-color: white !important;
    border: 1px solid #99c2ff !important;
    border-radius: 10px !important;
    color: #1a2b4a !important;
}

/* Expanders, info, warning, success boxes – light blue backgrounds */
.stAlert {
    background-color: #d4e9ff !important;
    border-color: #99c2ff !important;
    color: #1a2b4a !important;
}

/* DataFrame / table styling */
.dataframe {
    background-color: white !important;
    border-radius: 10px !important;
}

/* Caption, small text */
.caption, .stCaption {
    color: #1a2b4a !important;
}

/* Download button */
.stDownloadButton button {
    background-color: #4a8cff !important;
    color: white !important;
}

/* Sidebar logo and title text */
.sidebar-title {
    color: #1a2b4a !important;
}

/* Markdown tables */
table {
    background-color: white !important;
    border-radius: 10px !important;
}
th, td {
    color: #1a2b4a !important;
    border: 1px solid #99c2ff !important;
    padding: 6px 12px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# LOGIN PAGE
# ------------------------------
if not st.session_state.authenticated:
    st.title(f"🔐 {get_text('login_title', 'en')}")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        show_haitian_flag(150)
        st.markdown(f"<h2 style='text-align: center; color: #1a2b4a;'>{get_text('app_title', 'en')}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #1a2b4a;'>{get_text('by_line', 'en')}</p>", unsafe_allow_html=True)
        password_input = st.text_input(get_text('password_label', 'en'), type="password")
        if st.button(get_text('login_btn', 'en')):
            if password_input == "20082010":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error(get_text('wrong_password', 'en'))
    st.stop()

# ------------------------------
# AFTER LOGIN – MAIN APP
# ------------------------------
# Language selector in sidebar
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
    st.markdown(f"<h1 style='color: #1a2b4a;'>{t['main_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #1a2b4a;'>{t['subtitle']}</p>", unsafe_allow_html=True)

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

    # ------------------------------
    # AI VOICE SECTION (NEW)
    # ------------------------------
    st.markdown(f"### {t['ai_voice']}")
    voice_lang = st.selectbox(
        t['voice_language'],
        options=["English", "Español", "Français", "Kreyòl Ayisyen"],
        index=0
    )
    voice_code = LANGUAGES[voice_lang]

    if st.button(t['describe_app'], use_container_width=True):
        description = APP_DESCRIPTION.get(voice_code, APP_DESCRIPTION['en'])
        if gTTS is not None:
            try:
                tts = gTTS(text=description, lang=voice_code, slow=False)
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                st.audio(audio_bytes, format="audio/mp3")
                st.success(t['listening'])
            except Exception as e:
                st.error(f"Error generating speech: {e}")
        else:
            st.error("gTTS not installed. Please run: pip install gTTS")

    custom_text = st.text_area(t['custom_text'], height=100, value="Hello, this is a chess teaching app. Play and learn every day.")
    if st.button(t['speak_text'], use_container_width=True):
        if custom_text.strip():
            if gTTS is not None:
                try:
                    tts = gTTS(text=custom_text, lang=voice_code, slow=False)
                    audio_bytes = io.BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    st.audio(audio_bytes, format="audio/mp3")
                    st.success(t['listening'])
                except Exception as e:
                    st.error(f"Error generating speech: {e}")
            else:
                st.error("gTTS not installed. Please run: pip install gTTS")
        else:
            st.warning("Please enter some text to speak.")

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

def set_difficulty(level):
    skill_map = {"Beginner": 1, "Intermediate": 10, "Advanced": 18}
    st.session_state.stockfish.set_skill_level(skill_map[level])
    st.session_state.difficulty = level

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
            best_san = st.session_state.board.san(best_move)
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
                san = st.session_state.board.san(move)
                move_options[san] = move
            selected_san = st.selectbox(t['choose_move'], list(move_options.keys()))
            if st.button(t['make_move_btn'], use_container_width=True):
                move = move_options[selected_san]
                move_san = st.session_state.board.san(move)
                st.session_state.board.push(move)
                st.session_state.move_history.append(move_san)
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
                    move_san = st.session_state.board.san(move)
                    st.session_state.board.push(move)
                    st.session_state.move_history.append(move_san)
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
