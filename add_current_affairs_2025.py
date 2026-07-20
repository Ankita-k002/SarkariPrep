import os
import sqlite3

CURRENT_AFFAIRS_2025_2026 = [
    {
        "category": "UPSC",
        "subject": "Current Affairs",
        "question_text": "Who was sworn in as the 51st Chief Justice of India (CJI) in November 2024, succeeding Justice D.Y. Chandrachud?",
        "option_a": "Justice Sanjiv Khanna",
        "option_b": "Justice B.R. Gavai",
        "option_c": "Justice Surya Kant",
        "option_d": "Justice Hrishikesh Roy",
        "correct_option": "A",
        "explanation": "Justice Sanjiv Khanna took oath as the 51st Chief Justice of India on November 11, 2024, following the retirement of Justice D.Y. Chandrachud."
    },
    {
        "category": "UPSC",
        "subject": "Current Affairs",
        "question_text": "What is the primary target of the 'PM-Surya Ghar: Muft Bijli Yojana' launched by the Government of India?",
        "option_a": "Provide free rooftop solar panels to 1 crore households and up to 300 units of free electricity monthly.",
        "option_b": "Subsidize solar pump installation for 50 lakh farmers.",
        "option_c": "Build solar-powered charging stations across all national highways.",
        "option_d": "Provide 100% solar lighting in all government school buildings.",
        "correct_option": "A",
        "explanation": "PM-Surya Ghar: Muft Bijli Yojana aims to install rooftop solar panels in 1 crore households across India, providing up to 300 units of free electricity every month and enabling households to sell excess power back to the grid."
    },
    {
        "category": "SSC",
        "subject": "Current Affairs",
        "question_text": "Which nation hosted the 19th G20 Summit in November 2024 in Rio de Janeiro?",
        "option_a": "India",
        "option_b": "Brazil",
        "option_c": "South Africa",
        "option_d": "Indonesia",
        "correct_option": "B",
        "explanation": "Brazil hosted the 19th G20 Summit in Rio de Janeiro on November 18-19, 2024, under the presidency of President Luiz Inácio Lula da Silva, focusing on social inclusion and fighting hunger."
    },
    {
        "category": "Banking",
        "subject": "Current Affairs",
        "question_text": "Which Indian city hosted the 14th edition of the India International Textile Expo (PM MITRA Park) launch initiative?",
        "option_a": "Surat, Gujarat",
        "option_b": "Navsari, Gujarat",
        "option_c": "Tirupur, Tamil Nadu",
        "option_d": "Ludhiana, Punjab",
        "correct_option": "B",
        "explanation": "PM MITRA (Mega Integrated Textile Region and Apparel) Parks are being established across 7 states, including Navsari in Gujarat and Virudhunagar in Tamil Nadu, to make India a global textile hub."
    },
    {
        "category": "Railways",
        "subject": "Current Affairs",
        "question_text": "What is the name of the NASA-ISRO synthetic aperture radar satellite mission designed to map global changes in Earth's land and ice surfaces?",
        "option_a": "NISAR",
        "option_b": "TRISHNA",
        "option_c": "EOS-08",
        "option_d": "INSAT-3DS",
        "correct_option": "A",
        "explanation": "NISAR (NASA-ISRO Synthetic Aperture Radar) is a joint mission between NASA and ISRO to monitor ecosystem structures, ice sheet collapse, and natural hazards like earthquakes and tsunamis using dual-frequency radar."
    },
    {
        "category": "General",
        "subject": "Current Affairs",
        "question_text": "Which country won the ICC Men's T20 World Cup 2024 held in the West Indies and USA?",
        "option_a": "South Africa",
        "option_b": "India",
        "option_c": "Australia",
        "option_d": "England",
        "correct_option": "B",
        "explanation": "India won the ICC Men's T20 World Cup 2024 by defeating South Africa by 7 runs in a thrilling final at Kensington Oval in Bridgetown, Barbados, on June 29, 2024."
    },
    {
        "category": "General",
        "subject": "Current Affairs",
        "question_text": "Who won the Gold Medal for India in Men's Javelin Throw at the Paris 2024 Paralympic Games with a world-record distance?",
        "option_a": "Sumit Antil",
        "option_b": "Devendra Jhajharia",
        "option_c": "Nishad Kumar",
        "option_d": "Praveen Kumar",
        "correct_option": "A",
        "explanation": "Sumit Antil won the Gold medal in the Men's Javelin Throw F64 event at the Paris 2024 Paralympic Games, breaking his own Paralympic record with a throw of 70.59 meters."
    }
]

def seed_2025_current_affairs():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "study_helper.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    added = 0
    for q in CURRENT_AFFAIRS_2025_2026:
        cursor.execute("SELECT 1 FROM questions WHERE question_text = ?", (q["question_text"],))
        if cursor.fetchone():
            continue
        cursor.execute('''
        INSERT INTO questions 
        (category, subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, is_ai_generated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (
            q["category"],
            q["subject"],
            q["question_text"],
            q["option_a"],
            q["option_b"],
            q["option_c"],
            q["option_d"],
            q["correct_option"],
            q["explanation"]
        ))
        added += 1

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Added {added} fresh 2025/2026 Current Affairs questions.")

if __name__ == "__main__":
    seed_2025_current_affairs()
