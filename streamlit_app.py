import streamlit as st


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

st.header("Chat with Hiring Assistant")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

user_input = st.text_input("You:", key="user_input")
if st.button("Send"):
    if user_input.strip():
        
        st.session_state["chat_history"].append({"role": "user", "text": user_input})

        
        bot_reply = f"(Bot) You said: {user_input}"
        st.session_state["chat_history"].append({"role": "bot", "text": bot_reply})


for chat in st.session_state["chat_history"]:
    if chat["role"] == "user":
        st.markdown(f"**You:** {chat['text']}")
    else:
        st.markdown(f"**Bot:** {chat['text']}")


st.markdown("---")
st.caption("TalentScout Hiring Assistant © 2025")
