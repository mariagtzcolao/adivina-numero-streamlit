import random
import csv
from datetime import datetime
import os

import streamlit as st

CSV_FILE = "partidas.csv"

# ----------------------------
# Dificultades
# ----------------------------
DIFFICULTIES = {
    "Fácil (1-100, 7 intentos)": {"range_max": 100, "max_attempts": 7, "label": "FACIL"},
    "Medio (1-500, 6 intentos)": {"range_max": 500, "max_attempts": 6, "label": "MEDIO"},
    "Difícil (1-1000, 5 intentos)": {"range_max": 1000, "max_attempts": 5, "label": "DIFICIL"},
}


# ----------------------------
# Guardar registro en CSV
# ----------------------------
def save_to_csv(alias: str, result: str, attempts_used: int, max_attempts: int, range_max: int, difficulty_label: str):
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "fecha_utc", "alias", "resultado", "intentos_usados",
                "max_intentos", "rango_max", "dificultad"
            ])

        writer.writerow([
            datetime.utcnow().isoformat(),
            alias,
            result,
            attempts_used,
            max_attempts,
            range_max,
            difficulty_label
        ])


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
st.title("Adivina el número (web)")
st.write("Elige dificultad y juega.")

alias = st.text_input("Tu alias (opcional)", value="Anónimo").strip()
if not alias:
    alias = "Anónimo"

difficulty_choice = st.selectbox(
    "Dificultad",
    list(DIFFICULTIES.keys()),
    index=1  # por defecto "Medio"
)

col1, col2 = st.columns(2)
with col1:
    start = st.button("Empezar / Reiniciar")
with col2:
    st.write("")  # espacio

chosen = DIFFICULTIES[difficulty_choice]

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

    # Guardar una sola vez
    if not st.session_state.result_saved:
        attempts_used = max_attempts - st.session_state.attempts_left

        last = st.session_state.history[-1] if st.session_state.history else ""
        result = "WIN" if "✅" in last else "LOSE"

        try:
            save_to_csv(
                alias=alias,
                result=result,
                attempts_used=attempts_used,
                max_attempts=max_attempts,
                range_max=range_max,
                difficulty_label=st.session_state.difficulty_label
            )
            st.success("Partida guardada en partidas.csv 👍")
        except Exception as e:
            st.error("No pude guardar la partida en CSV.")
            st.caption(str(e))

        st.session_state.result_saved = True

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
            st.session_state.history.append(
                f"❌ Te quedaste sin intentos. El número era {st.session_state.secret}."
            )
            st.session_state.game_over = True

        st.rerun()

st.divider()
st.subheader("Historial")
for line in st.session_state.history:
    st.write("- " + line)

