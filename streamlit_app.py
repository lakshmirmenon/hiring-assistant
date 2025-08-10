import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
import json
import hashlib
import re


load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask_gemini(prompt, history=None, system_prompt=""):
    try:
        messages = "\n".join([f"{msg['role'].capitalize()}: {msg['text']}" for msg in history[-5:]]) if history else ""
        full_prompt = f"{system_prompt}\n{messages}\nUser: {prompt}\nAssistant:"
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=full_prompt
        )
        return response.text.strip() if response and response.text else ""
    except Exception as e:
        print(f"AI Model Error: {e}")
        return ""


def get_fallback_response(stage, user_input):
    fallback_responses = {
        "ask_name": "Could you please tell me your full name?",
        "ask_email": "Please provide a valid email (e.g., you@example.com).",
        "ask_phone": "Please share your phone number (min 10 digits).",
        "ask_experience": "Please share your professional experience in years (e.g., 2.5).",
        "ask_position": "What job position are you applying for?",
        "ask_location": "What's your current city and country?",
        "ask_tech_stack": "List your tech stack separated by commas (e.g., Python, React, MySQL).",
        "confirm_tech_stack": "Confirm with 'Yes' or provide the correct list.",
        "tech_questions": "Please answer the current technical question."
    }
    return fallback_responses.get(stage, "Let's continue with the screening process.")


def save_candidate_data():
    try:
        data = st.session_state["candidate_info"].copy()
        for key in ["name", "email", "phone"]:
            if key in data:
                data[f"{key}_hash"] = hashlib.sha256(data[key].encode()).hexdigest()
                del data[key]
        data["answers"] = st.session_state["answers"]
        data["completion_status"] = "completed" if st.session_state["chat_ended"] else "partial"

        filename = "candidate_screenings.json"
        try:
            with open(filename, "r") as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            existing_data = []

        existing_data.append(data)
        with open(filename, "w") as f:
            json.dump(existing_data, f, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")


def handle_tech_questions(user_text):
    experience_years = st.session_state["candidate_info"].get("experience", 0)
    difficulty = "beginner" if experience_years < 2 else "intermediate" if experience_years < 5 else "advanced"

    if st.session_state["questions"] and st.session_state["question_num"] > 0:
        prev_q = st.session_state["questions"][st.session_state["question_num"] - 1]
        st.session_state["answers"].append({
            "tech": st.session_state["current_tech"],
            "question": prev_q,
            "answer": user_text
        })

    
    if not st.session_state["questions"]:
        current_tech = st.session_state["current_tech"]
        prompt = f"Generate exactly 4 practical technical interview questions for {current_tech} at {difficulty} level."
        response = ask_gemini(prompt)
        lines = [l.strip() for l in response.split("\n") if l.strip()]
        questions = []
        for line in lines:
            if any(line.startswith(f"{i}.") for i in range(1, 6)):
                q = line.split(".", 1)[1].strip()
                if q:
                    questions.append(q)
        if len(questions) < 4:
            fallback_questions = {
                "beginner": [
                    f"What attracted you to learning {current_tech}?",
                    f"Explain a basic concept in {current_tech}.",
                    f"Describe a small project you built with {current_tech}.",
                    f"What challenges did you face while learning {current_tech}?"
                ],
                "intermediate": [
                    f"Describe a complex {current_tech} project.",
                    f"Best practices you follow with {current_tech}?",
                    f"How do you debug problems in {current_tech}?",
                    f"What advanced {current_tech} features have you used?"
                ],
                "advanced": [
                    f"Steps to optimize {current_tech} for performance?",
                    f"Experience scaling apps with {current_tech}?",
                    f"Design patterns you use in {current_tech}?",
                    f"How do you keep up with {current_tech} updates?"
                ]
            }
            questions = fallback_questions[difficulty]
        st.session_state["questions"] = questions[:4]
        st.session_state["question_num"] = 0

    
    if st.session_state["question_num"] < len(st.session_state["questions"]):
        q_num = st.session_state["question_num"] + 1
        bot_reply = f"**Question {q_num} of 4 for {st.session_state['current_tech']}:**\n\n{st.session_state['questions'][st.session_state['question_num']]}"
        st.session_state["question_num"] += 1
        return bot_reply
    else:
        
        if st.session_state["tech_index"] + 1 < len(st.session_state["tech_stack_list"]):
            st.session_state["tech_index"] += 1
            st.session_state["current_tech"] = st.session_state["tech_stack_list"][st.session_state["tech_index"]]
            st.session_state["questions"] = []
            st.session_state["question_num"] = 0
            return f"✅ Done with {st.session_state['tech_stack_list'][st.session_state['tech_index']-1]}!\n\nNext: **{st.session_state['current_tech']}**"
        else:
            st.session_state["chat_ended"] = True
            save_candidate_data()
            return "🎉 You've completed the technical screening! We'll be in touch soon."


st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🎯", layout="centered")
st.title("🎯 TalentScout Hiring Assistant")

if "chat_history" not in st.session_state:
    st.session_state.update({
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

EXIT_KEYWORDS = {"exit", "quit", "bye", "goodbye", "stop", "end", "cancel", "terminate", "finish"}


if st.session_state["chat_ended"]:
    st.success("🎉 Screening completed! Thank you.")
    if st.button("Start New Chat"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
else:
    if not st.session_state["chat_history"] and st.session_state["stage"] == "greet":
        greeting = "Hello! I'm your TalentScout Hiring Assistant. Let's start with your full name."
        st.session_state["chat_history"].append({"role": "assistant", "text": greeting})
        st.session_state["stage"] = "ask_name"

    for chat in st.session_state["chat_history"]:
        with st.chat_message(chat["role"]):
            st.markdown(chat["text"])

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("You:", key="user_input")
        submitted = st.form_submit_button("Send", type="primary")

    if submitted and user_input.strip():
        text = user_input.strip()
        st.session_state["chat_history"].append({"role": "user", "text": text})

        if any(k in text.lower() for k in EXIT_KEYWORDS):
            st.session_state["chat_history"].append({"role": "assistant",
                "text": "Thank you for your time. You may continue later anytime. 👋"})
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
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', text):
                st.session_state["candidate_info"]["email"] = text
                st.session_state["stage"] = "ask_phone"
                bot_reply = "Please provide your phone number."
            else:
                bot_reply = get_fallback_response(stage, text)

        elif stage == "ask_phone":
            cleaned = ''.join(filter(str.isdigit, text))
            if len(cleaned) >= 10:
                st.session_state["candidate_info"]["phone"] = text
                st.session_state["stage"] = "ask_experience"
                bot_reply = "How many years of experience do you have?"
            else:
                bot_reply = get_fallback_response(stage, text)

        elif stage == "ask_experience":
            numbers = re.findall(r'[\d.]+', text)
            if numbers:
                years = float(numbers[0])
                st.session_state["candidate_info"]["experience"] = years
                st.session_state["stage"] = "ask_position"
                bot_reply = f"{years} years noted. What position are you applying for?"
            else:
                bot_reply = get_fallback_response(stage, text)

        elif stage == "ask_position":
            st.session_state["candidate_info"]["position"] = text
            st.session_state["stage"] = "ask_location"
            bot_reply = "What's your current location?"

        elif stage == "ask_location":
            st.session_state["candidate_info"]["location"] = text
            st.session_state["stage"] = "ask_tech_stack"
            bot_reply = "List your tech stack, separated by commas."

        elif stage == "ask_tech_stack":
            techs = [t.strip() for t in text.split(",") if t.strip()]
            if techs:
                st.session_state["candidate_info"]["tech_stack"] = ", ".join(techs)
                st.session_state["stage"] = "confirm_tech_stack"
                bot_reply = f"Here's what I got:\n• " + "\n• ".join(techs) + "\n\nIs this correct?"
            else:
                bot_reply = get_fallback_response(stage, text)

        elif stage == "confirm_tech_stack":
            if text.lower() in ["yes", "y", "correct"]:
                st.session_state["tech_stack_list"] = [
                    t.strip() for t in st.session_state["candidate_info"]["tech_stack"].split(",")
                ]
                st.session_state["current_tech"] = st.session_state["tech_stack_list"][0]
                st.session_state["stage"] = "tech_questions"
                bot_reply = handle_tech_questions("") 
            else:
                bot_reply = "Please provide the corrected tech stack."

        elif stage == "tech_questions":
            bot_reply = handle_tech_questions(text)

        else:
            bot_reply = get_fallback_response(stage, text)

        st.session_state["chat_history"].append({"role": "assistant", "text": bot_reply})
        st.rerun()
