import streamlit as st
import requests
import uuid

# ============================================
# CONFIG - Yahan apna n8n webhook URL dalein
# ============================================
N8N_WEBHOOK_URL = "https://murshad123456.app.n8n.cloud/webhook/weather-chat"

st.set_page_config(page_title="Weather Chatbot", page_icon="🌤️", layout="centered")

# ============================================
# Session state setup
# ============================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_id" not in st.session_state:
    # Har user/session ke liye unique id (n8n memory feature ke liye kaam aayegi)
    st.session_state.user_id = str(uuid.uuid4())

st.title("🌤️ Weather Chatbot")
st.caption("Apne shehar ka mausam poochein — Roman Urdu ya English mein")

# ============================================
# Purane messages dikhana
# ============================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ============================================
# Naya message input
# ============================================
user_input = st.chat_input("Jaise: 'Karachi ka weather batao'")

if user_input:
    # User ka message chat mein dikhao aur save karo
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # n8n webhook ko call karo
    with st.chat_message("assistant"):
        with st.spinner("Mausam check kar raha hoon..."):
            try:
                response = requests.post(
                    N8N_WEBHOOK_URL,
                    json={
                        "message": user_input,
                        "user_id": st.session_state.user_id
                    },
                    timeout=15
                )

                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply", "Maaf kijiye, jawab nahi mil saka.")
                else:
                    reply = f"Server error aaya (status {response.status_code}). Dobara koshish karein."

            except requests.exceptions.Timeout:
                reply = "Request timeout ho gayi. Server slow ho sakta hai, dobara koshish karein."
            except requests.exceptions.ConnectionError:
                reply = "n8n server se connect nahi ho saka. Webhook URL check karein."
            except Exception as e:
                reply = f"Ek error aaya: {str(e)}"

            st.markdown(reply)

    # Bot ka jawab save karo
    st.session_state.messages.append({"role": "assistant", "content": reply})

# ============================================
# Sidebar - extra options
# ============================================
with st.sidebar:
    st.header("Options")
    if st.button("🗑️ Chat Clear Karein"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption(f"Session ID: `{st.session_state.user_id[:8]}...`")
