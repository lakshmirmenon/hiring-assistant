# TalentScout Hiring Assistant

An AI-powered hiring assistant chatbot built for **TalentScout**, a fictional recruitment agency specializing in technology placements.  
The chatbot screens candidates, collects essential information, and generates tailored technical interview questions based on their declared tech stack.

Project Overview
The TalentScout Hiring Assistant is an intelligent chatbot built using **Streamlit** and **Google Gemini API**.  
It guides candidates through a structured screening process, asks technical questions based on their experience and tech stack, and stores anonymized responses for HR review via an admin dashboard.

Features
- **Greeting & Introduction** — Welcomes the candidate and explains the interview process.
- **Information Gathering** — Collects:
  - Full Name
  - Email Address
  - Phone Number
  - Years of Experience
  - Desired Position(s)
  - Current Location
  - Tech Stack
- **Tech-Specific Questions** — Generates 3–5 practical interview questions per technology.
- **Difficulty Adaptation** — Adjusts questions based on years of experience.
- **Context-Aware Conversation** — Maintains flow and remembers previous answers.
- **Fallback Mechanism** — Uses predefined questions if AI is unavailable.
- **Exit Keywords** — Allows candidates to end the interview gracefully.
- **HR Dashboard** — Password-protected view for reviewing & exporting anonymized candidate data.
- **Data Privacy** — Stores hashed personal information and timestamps for tracking.

Installation

1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/talentscout-hiring-assistant.git
cd talentscout-hiring-assistant
```

2. Create a virtual environment & install dependencies
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

3. Set up environment variables
Create a `.env` file in the root folder:
```env
GEMINI_API_KEY=your_google_gemini_api_key
```

4. Configure Streamlit Secrets
Create `.streamlit/secrets.toml` (excluded from Git) and add:
```toml
HR_PASSWORD = "your_admin_password"
```

5. Run the app
```bash
streamlit run app.py
```

---

Usage Guide

Candidate Flow
1. The chatbot greets the candidate and explains the process.
2. Candidate enters details step-by-step.
3. Chatbot generates tailored technical questions per tech stack.
4. Candidate answers; chatbot continues until all questions are complete.
5. Candidate can type **exit** or similar keywords to end early.
6. Chat ends with a thank-you message.

HR Dashboard
1. Enter the admin password in the sidebar.
2. View candidate data with completion status and timestamp.
3. Filter results by tech stack.
4. Download candidate data as CSV.

---

Prompt Design

System Prompt Template:
```
You are TalentScout's Hiring Assistant, a professional AI for tech screening.
Follow the user's stage strictly and ask one question at a time.
Stage: {stage}
Current tech: {current_tech}
Difficulty: {difficulty}
Question number: {question_num}
```
- Ensures the AI stays on-topic.
- Dynamically injects candidate details & context.
- Produces exactly the desired number of practical interview questions.

**Fallback Questions:**
- Predefined beginner, intermediate, and advanced questions.
- Activated if AI returns no or insufficient questions.
- Ensures uninterrupted flow even if the AI API fails.

**Difficulty Selection:**
- `< 2 years` → Beginner questions.
- `2–5 years` → Intermediate questions.
- `> 5 years` → Advanced questions.

---

Data Privacy
- **Name, email, and phone** are **SHA-256 hashed** before saving.
- Data stored locally in `candidate_screenings.json`.
- Admin password securely stored in `.streamlit/secrets.toml`.
- `.streamlit/secrets.toml` is in `.gitignore` to avoid accidental commits.

---

Project Structure
```
├── streamlit_app.py                    # Main Streamlit application
├── candidate_screenings.json # Stored candidate data (local)
├── .env                       # Environment variables (ignored in Git)
├── .streamlit/secrets.toml   # HR admin password (ignored in Git)
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation
```

---

Demo
- **Local Demo**: Run `streamlit run streamlit_app.py`
- (Optional) Loom Video: [Add link here]
- (Optional) Deployment: [Add live app link here]

---

Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/)
- **AI Model**: [Google Gemini API](https://ai.google.dev/)
- **Backend Logic**: Python
- **Data Handling**: JSON, Pandas
- **Security**: Hashlib for sensitive fields

---

Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Handling missing AI responses | Implemented fallback questions |
| Maintaining conversation context | Used `st.session_state` to store stage, history, and answers |
| Data privacy for PII | Applied SHA-256 hashing before storage |
| Preventing crashes from missing keys in HR dashboard | Added `isinstance(c, dict)` checks |

---

License
This project is for **educational and demonstration purposes** as part of the AI/ML Intern assignment.

---

