

import os
import json
import re
import time
import hashlib
from dotenv import load_dotenv
import streamlit as st
from google import genai
from datetime import datetime 

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

QUESTIONS_PER_TECH = 4
DATA_FILENAME = "candidate_screenings.json"
KEEP_HISTORY = 10
REQUEST_RETRIES = 3
RETRY_DELAY = 1

EXIT_KEYWORDS = {"exit", "quit", "bye", "goodbye", "stop", "end", "cancel", "terminate", "finish"}


def ask_gemini(prompt, history=None, system_prompt="", retries=REQUEST_RETRIES):
    if client is None:
        return ""
    for attempt in range(1, retries + 1):
        try:
            short_hist = (history or [])[-2:]
            messages_text = "\n".join([f"{m['role'].capitalize()}: {m['text']}" for m in short_hist])
            full_prompt = f"{system_prompt}\n{messages_text}\nUser: {prompt}\nAssistant:"
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=full_prompt
            )
            if not response:
                return ""
            if hasattr(response, "text") and response.text:
                return response.text.strip()
            try:
                return response.candidates[0].content.strip()
            except Exception:
                return str(response).strip()
        except Exception as e:
            print(f"AI Model Error (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                time.sleep(RETRY_DELAY)
    return ""


SYSTEM_PROMPT_TEMPLATE = """
You are TalentScout's Hiring Assistant, a professional AI for tech screening.
Follow the user's stage strictly and ask one question at a time.
Stage: {stage}
Current tech: {current_tech}
Difficulty: {difficulty}
Question number: {question_num}
"""


def fallback_questions_for(tech, difficulty):
    return {
        "beginner": [
            f"Explain a basic concept in {tech}.",
            f"Describe a small project you built with {tech}.",
            f"What challenges did you face while learning {tech}?",
            f"How does {tech} handle a common task?"
        ],
        "intermediate": [
            f"Describe a complex {tech} project.",
            f"What best practices do you follow with {tech}?",
            f"How do you debug problems in {tech}?",
            f"What advanced {tech} features have you used?"
        ],
        "advanced": [
            f"How do you optimize {tech} for performance?",
            f"Describe your experience scaling apps with {tech}.",
            f"What design patterns do you use in {tech}?",
            f"How do you stay updated with {tech} changes?"
        ]
    }[difficulty]

def generate_questions_for(tech, difficulty, num_questions):
    prompt = f"Generate exactly {num_questions} practical technical interview questions for {tech} at {difficulty} level. Use numbered list."
    sys = SYSTEM_PROMPT_TEMPLATE.format(stage="tech_questions", current_tech=tech, difficulty=difficulty, question_num=0)
    response = ask_gemini(prompt, history=st.session_state.get("chat_history", []), system_prompt=sys)
    questions = []
    if response:
        for line in [l.strip() for l in response.splitlines() if l.strip()]:
            m = re.match(r'^\s*\d+[\.\)]\s*(.+)$', line)
            if m:
                questions.append(m.group(1).strip())
            elif line.endswith("?"):
                questions.append(line)
        if len(questions) >= num_questions:
            return questions[:num_questions]
    fb = fallback_questions_for(tech, difficulty)
    while len(fb) < num_questions:
        fb += fb
    return fb[:num_questions]


def save_candidate_data():
    try:
        data = st.session_state["candidate_info"].copy()
        for key in ["name", "email", "phone"]:
            if key in data and data[key]:
                data[f"{key}_hash"] = hashlib.sha256(str(data[key]).encode()).hexdigest()
                del data[key]
        data["answers"] = st.session_state["answers"]
        data["completion_status"] = "completed" if st.session_state["chat_ended"] else "partial"
        data["timestamp"] = datetime.now().isoformat() 
        try:
            with open(DATA_FILENAME, "r") as f:
                existing = json.load(f)
        except FileNotFoundError:
            existing = []
        existing.append(data)
        with open(DATA_FILENAME, "w") as f:
            json.dump(existing, f, indent=2)
    except Exception as e:
        print("Error saving data:", e)


st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="assets/conversation.png", layout="centered")
col1, col2 = st.columns([0.1, 0.9])  

with col1:
    st.image("assets/follow-up.png", width=50)  

with col2:
    st.title("TalentScout Hiring Assistant")


if "initialized" not in st.session_state:
    st.session_state.update({
        "initialized": True,
        "chat_history": [],
        "chat_ended": False,
        "candidate_info": {},
        "stage": "greet",
        "tech_stack_list": [],
        "current_tech": "",
        "tech_index": 0,
        "question_num": 0,
        "questions": [],
        "answers": []
    })

if not st.session_state["chat_history"] and st.session_state["stage"] == "greet":
    st.session_state["chat_history"].append({"role": "assistant", "text": "Hello! I'm your TalentScout Hiring Assistant. What's your full name?"})
    st.session_state["stage"] = "ask_name"

for chat in st.session_state["chat_history"]:
    with st.chat_message(chat["role"]):
        st.markdown(chat["text"])

with st.sidebar:
    st.header("Interview Progress")
    if st.session_state["stage"] == "tech_questions":
        total_techs = max(1, len(st.session_state["tech_stack_list"]))
        current_tech_idx = st.session_state["tech_index"] + 1
        total_questions = QUESTIONS_PER_TECH
        q_num = min(st.session_state["question_num"], total_questions)
        st.write(f"Tech {current_tech_idx} of {total_techs}")
        st.write(f"Current tech: **{st.session_state.get('current_tech','-')}**")
        st.write(f"Question {q_num} of {total_questions}")
        overall_progress = ((current_tech_idx - 1) * total_questions + q_num) / (total_techs * total_questions)
        st.progress(overall_progress)
    else:
        st.write("Not yet in technical questions")

    st.markdown("---")
    st.write("Settings")
    st.write(f"Questions per tech: **{QUESTIONS_PER_TECH}**")

    st.markdown("---")
    st.markdown("###  HR Dashboard (Admin Only)")

    hr_password = st.text_input("Enter admin password", type="password")
    

    if hr_password == st.secrets.get("HR_PASSWORD", ""):
        import pandas as pd

        if os.path.exists(DATA_FILENAME):
            try:
                with open(DATA_FILENAME, "r") as f:
                    candidates = json.load(f)

                if candidates:
                    df = pd.DataFrame(candidates)

                    # Filter by tech stack
                    all_techs = sorted({
                        t.strip()
                        for c in df["candidate_info"]
                        if isinstance(c, dict)
                        for t in c.get("tech_stack", "").split(",")
                        if t.strip()
                        })
                    selected_tech = st.selectbox("Filter by Tech", ["All"] + list(all_techs))
                    if selected_tech != "All":
                        df = df[df["candidate_info"].apply(
                            lambda x: selected_tech.lower() in x.get("tech_stack", "").lower()
                        )]

                    # Completion stats
                    completed = sum(df["completion_status"] == "completed")
                    partial = sum(df["completion_status"] == "partial")
                    st.write(f" Completed: {completed}")
                    st.write(f" Partial: {partial}")

                    # Show data
                    st.dataframe(df[["completion_status", "timestamp"]])

                    # Download CSV
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="candidates.csv",
                        mime="text/csv",
                    )
                else:
                    st.info("No candidates recorded yet.")
            except Exception as e:
                st.error(f"Error loading data: {e}")
        else:
            st.info("No candidates recorded yet.")

    elif hr_password:
        st.error("Incorrect password.")

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", key="user_input")
    submitted = st.form_submit_button("Send", type="primary")

def safe_add_bot(msg):
    st.session_state["chat_history"].append({"role": "assistant", "text": msg})

def safe_add_user(msg):
    st.session_state["chat_history"].append({"role": "user", "text": msg})

if submitted and user_input.strip():
    text = user_input.strip()
    safe_add_user(text)

    if any(k in text.lower() for k in EXIT_KEYWORDS):
        safe_add_bot("Thank you for your time. You may continue later anytime. 👋")
        st.session_state["chat_ended"] = True
        save_candidate_data()
        st.rerun()

    stage = st.session_state["stage"]
    bot_reply = None

    if stage == "ask_name":
        st.session_state["candidate_info"]["name"] = text
        st.session_state["stage"] = "ask_email"
        bot_reply = f"Nice to meet you, {text.split()[0]}! Please provide your email."

    elif stage == "ask_email":
        if re.match(r'^[^@]+@[^@]+\.[^@]+$', text):
            st.session_state["candidate_info"]["email"] = text
            st.session_state["stage"] = "ask_phone"
            bot_reply = "Please provide your phone number."
        else:
            bot_reply = "Please provide a valid email."

    elif stage == "ask_phone":
        cleaned = ''.join(filter(str.isdigit, text))
        if len(cleaned) >= 10:
            st.session_state["candidate_info"]["phone"] = text
            st.session_state["stage"] = "ask_experience"
            bot_reply = "How many years of experience do you have? (e.g., 2.5)"
        else:
            bot_reply = "Please share your phone number (min 10 digits)."

    elif stage == "ask_experience":
        numbers = re.findall(r'[\d.]+', text)
        if numbers:
            years = float(numbers[0])
            st.session_state["candidate_info"]["experience"] = years
            st.session_state["stage"] = "ask_position"
            bot_reply = f"{years} years noted. What position are you applying for?"
        else:
            bot_reply = "Please share your professional experience in years."

    elif stage == "ask_position":
        st.session_state["candidate_info"]["position"] = text
        st.session_state["stage"] = "ask_location"
        bot_reply = "What's your current location?"

    elif stage == "ask_location":
        st.session_state["candidate_info"]["location"] = text
        st.session_state["stage"] = "ask_tech_stack"
        bot_reply = "List your tech stack separated by commas."

    elif stage == "ask_tech_stack":
        techs = [t.strip() for t in text.split(",") if t.strip()]
        if techs:
            st.session_state["candidate_info"]["tech_stack"] = ", ".join(techs)
            st.session_state["stage"] = "confirm_tech_stack"
            bot_reply = "Here's what I got:\n• " + "\n• ".join(techs) + "\n\nIs this correct? (Yes/No)"
        else:
            bot_reply = "Please list at least one tech."

    elif stage == "confirm_tech_stack":
        if text.lower() in ["yes", "y", "correct"]:
            stack = [t.strip() for t in st.session_state["candidate_info"]["tech_stack"].split(",") if t.strip()]
            st.session_state["tech_stack_list"] = stack
            st.session_state["current_tech"] = stack[0] if stack else ""
            st.session_state["stage"] = "tech_questions"
            st.session_state["tech_index"] = 0
            st.session_state["questions"] = []
            st.session_state["question_num"] = 0
        elif text.lower() in ["no", "n", "incorrect"]:
            st.session_state["stage"] = "ask_corrected_tech_stack"
            bot_reply = "Okay, please provide the corrected tech stack."
        else:
            bot_reply = "Please answer Yes or No."
    elif stage == "ask_corrected_tech_stack":
        techs = [t.strip() for t in text.split(",") if t.strip()]
        if techs:
            st.session_state["candidate_info"]["tech_stack"] = ", ".join(techs)
            st.session_state["stage"] = "confirm_tech_stack"
            bot_reply = "Here's what I got now:\n• " + "\n• ".join(techs) + "\n\nIs this correct? (Yes/No)"
        else:
            bot_reply = "Please list at least one tech."



    if st.session_state["stage"] == "tech_questions":
        def handle_tech_questions_flow(user_text):
            exp = st.session_state["candidate_info"].get("experience", 0)
            difficulty = "beginner" if exp < 2 else "intermediate" if exp < 5 else "advanced"
            current_tech = st.session_state["current_tech"]

            if st.session_state["question_num"] > 0 and user_text.strip():
                prev_q = st.session_state["questions"][st.session_state["question_num"] - 1]
                st.session_state["answers"].append({"tech": current_tech, "question": prev_q, "answer": user_text})

            if not st.session_state["questions"]:
                st.session_state["questions"] = generate_questions_for(current_tech, difficulty, QUESTIONS_PER_TECH)
                st.session_state["question_num"] = 0

            if st.session_state["question_num"] < len(st.session_state["questions"]):
                q_text = st.session_state["questions"][st.session_state["question_num"]]
                st.session_state["question_num"] += 1
                return f"**Question {st.session_state['question_num']} of {len(st.session_state['questions'])} for {current_tech}:**\n{q_text}"
            else:
                if st.session_state["tech_index"] + 1 < len(st.session_state["tech_stack_list"]):
                    completed = st.session_state["current_tech"]
                    st.session_state["tech_index"] += 1
                    st.session_state["current_tech"] = st.session_state["tech_stack_list"][st.session_state["tech_index"]]
                    st.session_state["questions"] = []
                    st.session_state["question_num"] = 0
                    return f" Done with {completed}! Now moving to **{st.session_state['current_tech']}**."
                else:
                    st.session_state["chat_ended"] = True
                    save_candidate_data()
                    return " You've completed the technical screening! We'll be in touch soon."

        bot_reply = handle_tech_questions_flow(text)

    if bot_reply is None:
        bot_reply = "Sorry, I didn't understand that. Let's continue."

    safe_add_bot(bot_reply)
    st.session_state["chat_history"] = st.session_state["chat_history"][-KEEP_HISTORY:]
    st.rerun()

if st.session_state["chat_ended"]:
    st.success("🎉 Screening completed! Thank you.")
    st.subheader("Interview Summary (non-sensitive)")
    info = st.session_state["candidate_info"].copy()
    st.json({
        "experience_years": info.get("experience"),
        "position": info.get("position"),
        "location": info.get("location"),
        "tech_stack": info.get("tech_stack")
    })
    st.subheader("Answers (first 5 shown)")
    st.write(st.session_state["answers"][:5])
    st.markdown("---")
    if st.button("Start New Chat"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
