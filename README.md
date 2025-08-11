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


