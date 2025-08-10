import streamlit as st
import os
from dotenv import load_dotenv
from google import genai

# ---- Load environment variables ----
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---- Gemini LLM function ----
def ask_gemini(prompt, history=None):
    messages = "\n".join(
        [f"{msg['role'].capitalize()}: {msg['text']}" for msg in history]
    )
    full_prompt = f"{messages}\nUser: {prompt}\nAssistant:"
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=full_prompt
    )
    return response.text

# ---- Page Setup ----
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="assets/conversation.png", layout="centered")
col1, col2 = st.columns([0.12, 0.88])  

with col1:
    st.image("assets/follow-up.png", width=50)

with col2:
    st.markdown("## TalentScout Hiring Assistant")

st.markdown(
    """
    Welcome! I’ll help you with the initial screening process.
    Please provide your basic details and we’ll start with some tailored questions.
    """
)

# ---- Candidate Info Form ----
st.header("Candidate Information")
with st.form("candidate_form"):
    full_name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    experience = st.number_input("Years of Experience", min_value=0, step=1)
    desired_position = st.text_input("Desired Position(s)")
    location = st.text_input("Current Location")
    tech_stack = st.text_area("Tech Stack (comma-separated, e.g., Python, Django, PostgreSQL)")

    submitted = st.form_submit_button("Submit")

if submitted:
    st.success(f"Thank you, {full_name}! Your details have been recorded.")
    st.session_state["candidate_info"] = {
        "name": full_name,
        "email": email,
        "phone": phone,
        "experience": experience,
        "position": desired_position,
        "location": location,
        "tech_stack": tech_stack
    }

# ---- Chatbot Section with Exit Logic ----
st.header("Chat with Hiring Assistant")

# Session state initialization
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "chat_ended" not in st.session_state:
    st.session_state["chat_ended"] = False

EXIT_KEYWORDS = {"exit", "quit", "bye", "goodbye", "stop", "end"}

# If chat has ended
if st.session_state["chat_ended"]:
    st.info("The chat has ended. Click **Start new chat** to begin again.")
    if st.button("Start new chat"):
        st.session_state["chat_history"] = []
        st.session_state["chat_ended"] = False
        st.rerun()
else:
    # Chat input form (auto-clears after send)
    with st.form("chat_form", clear_on_submit=True):
        chat_text = st.text_input("You:", key="chat_input_form")
        chat_submitted = st.form_submit_button("Send")

    if chat_submitted:
        text = chat_text.strip()
        if text:
            # Append user message
            st.session_state["chat_history"].append({"role": "user", "text": text})

            # Exit condition
            if text.lower() in EXIT_KEYWORDS:
                farewell_msg = "Thank you for chatting! Goodbye and good luck with your job search."
                st.session_state["chat_history"].append({"role": "assistant", "text": farewell_msg})
                st.session_state["chat_ended"] = True
            else:
                # LLM reply
                bot_reply = ask_gemini(text, st.session_state["chat_history"])
                if not bot_reply or bot_reply.strip() == "":
                    bot_reply = "I'm not sure about that. Could you clarify?"
                st.session_state["chat_history"].append({"role": "assistant", "text": bot_reply})

# Display chat history
for chat in st.session_state["chat_history"]:
    if chat["role"] == "user":
        st.markdown(f"**You:** {chat['text']}")
    else:
        st.markdown(f"**Bot:** {chat['text']}")

# ---- Footer ----
st.markdown("---")
st.caption("TalentScout Hiring Assistant © 2025")
