import random
from datetime import datetime

import streamlit as st
from supabase import create_client

# ----------------------------
# Supabase
# ----------------------------
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

def save_game_result(alias: str, result: str, attempts_used: int, max_attempts: int, range_max: int, difficulty: str):
    supabase = get_supabase()
    supabase.table("game_runs").insert({
        "played_at": datetime.utcnow().isoformat(),
        "alias": alias,
        "result": result,
        "attempts_used": attempts_used,
        "max_attempts": max_attempts,
        "secret_range_max": range_max,
        "difficulty": difficulty,
    }).execute()


# ----------------------------
# Dificultades
# ----------------------------
DIFFICULTIES = {
    "Fácil (1-100, 7 intentos)": {"range_max": 100, "max_attempts": 7, "label": "FACIL"},
    "Medio (1-500, 6 intentos)": {"range_max": 500, "max_attempts": 6, "label": "MEDIO"},
    "Difícil (1-1000, 5 intentos)": {"range_max": 1000, "max_attempts": 5, "label": "DIFICIL"},
}


# ----------------------------
# Estado del juego
# ----------------------------
def reset_game(range_max: int, max_attempts: int, difficulty_label: str):
    st.session_state.range_max = range_max
    st.session_state.max_attempts = max_attempts
    st.session_state.difficulty_label = difficulty_label

    st.session_state.secret = random.randint(1, range_max)
    st.session_state.attempts_left = max_attempts
    st.session_state.history = []
    st.session_state.game_over = False
    st.session_state.result_saved = False


# ----------------------------
# UI
# ----------------------------
st.title("Adivina el número")

if parsed.hostname:
    try:
        ip = socket.gethostbyname(parsed.hostname)
        st.write("DNS OK -> IP:", ip)
    except Exception as e:
        st.write("DNS FAIL ->", repr(e))
st.write("Elige dificultad y juega.")

alias = st.text_input("Tu alias (opcional)", value="Anónimo").strip()
if not alias:
    alias = "Anónimo"

difficulty_choice = st.selectbox("Dificultad", list(DIFFICULTIES.keys()), index=1)
chosen = DIFFICULTIES[difficulty_choice]

col1, col2 = st.columns(2)
with col1:
    start = st.button("Empezar / Reiniciar")

# Inicializar estado si no existe (primera vez)
if "secret" not in st.session_state:
    reset_game(chosen["range_max"], chosen["max_attempts"], chosen["label"])

# Si pulsa empezar, reinicia con la dificultad seleccionada
if start:
    reset_game(chosen["range_max"], chosen["max_attempts"], chosen["label"])
    st.rerun()

st.divider()

range_max = st.session_state.range_max
max_attempts = st.session_state.max_attempts
st.write(f"Rango: **1 - {range_max}** | Intentos: **{st.session_state.attempts_left} / {max_attempts}**")

if st.session_state.game_over:
    st.subheader("Partida terminada ✅")

    if not st.session_state.result_saved:
        attempts_used = max_attempts - st.session_state.attempts_left
        last = st.session_state.history[-1] if st.session_state.history else ""
        result = "WIN" if "✅" in last else "LOSE"

        try:
            save_game_result(
                alias=alias,
                result=result,
                attempts_used=attempts_used,
                max_attempts=max_attempts,
                range_max=range_max,
                difficulty=st.session_state.difficulty_label,
            )
            st.success("Partida guardada ✅")
        except Exception as e:
            st.error("No pude guardar la partida en Supabase.")
            st.caption(str(e))

        st.session_state.result_saved = True

    if st.button("Jugar otra vez"):
        reset_game(range_max, max_attempts, st.session_state.difficulty_label)
        st.rerun()

else:
    guess = st.number_input("Tu número", min_value=1, max_value=range_max, step=1)

    if st.button("Probar"):
        st.session_state.attempts_left -= 1

        if guess == st.session_state.secret:
            st.session_state.history.append(f"✅ Acertaste: {guess}")
            st.session_state.game_over = True
        elif guess < st.session_state.secret:
            st.session_state.history.append(f"⬆️ {guess} es bajo")
        else:
            st.session_state.history.append(f"⬇️ {guess} es alto")

        if st.session_state.attempts_left == 0 and not st.session_state.game_over:
            st.session_state.history.append(f"❌ Te quedaste sin intentos. El número era {st.session_state.secret}.")
            st.session_state.game_over = True

        st.rerun()

st.divider()
st.subheader("Historial")
for line in st.session_state.history:
    st.write("- " + line)





