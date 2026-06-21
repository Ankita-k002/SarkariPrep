# AI Prompts

This directory houses operational prompts used by the system or developers to instruct AI systems.

---

## 🧠 Question Generation Prompt
The core prompt instruction for generating exam questions using Gemini:
* Located in: `generate_ai_question` inside [[app.py]]
* Purpose: Directs Gemini to produce 1 preface-free MCQ JSON object.

## 💾 Bulk Questions Generator Prompt
The prompt used for initial DB population:
* Located in: `generate_batch` inside [[generate_1000_questions.py]]
* Purpose: Instructs Gemini to yield a batch array of exactly 10 questions.

---
## 🔗 Related Links
* [[Project Overview]]
* [[docs/templates/AI Prompt Template|AI Prompt Template]]
