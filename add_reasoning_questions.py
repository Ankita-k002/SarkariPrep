import os
import sys
import json
import time
import sqlite3
import requests

# 15 high-quality, pre-defined reasoning questions to seed immediately
PREDEFINED_REASONING = [
    {
        "category": "General",
        "subject": "Reasoning",
        "question_text": "If 'Light' is related to 'Blind' in the same way as 'Speech' is related to:",
        "option_a": "Deaf",
        "option_b": "Dumb",
        "option_c": "Silent",
        "option_d": "Vocal",
        "correct_option": "B",
        "explanation": "Blindness is the inability to see light. Similarly, dumbness is the inability to produce speech. Thus, speech is related to dumb."
    },
    {
        "category": "SSC",
        "subject": "Reasoning",
        "question_text": "Find the missing number in the following number series: 3, 5, 9, 17, 33, ?",
        "option_a": "48",
        "option_b": "55",
        "option_c": "65",
        "option_d": "68",
        "correct_option": "C",
        "explanation": "The pattern of the series is: each term is (previous term * 2) - 1. (3*2)-1=5; (5*2)-1=9; (9*2)-1=17; (17*2)-1=33; (33*2)-1=65. Hence, the missing number is 65."
    },
    {
        "category": "Banking",
        "subject": "Reasoning",
        "question_text": "In a certain code language, if 'COMPUTER' is written as 'RFUVQNPC', how is 'MEDICINE' written in that code?",
        "option_a": "EOJDJEFM",
        "option_b": "EOJDEJFM",
        "option_c": "MFEJDJOE",
        "option_d": "MFEDJJOE",
        "correct_option": "A",
        "explanation": "The pattern is: the first and last letters of the word swap positions. The remaining letters are shifted forward by 1 (+1) and written in reverse order. So, 'MEDICINE' becomes M -> E (swap first/last), then E(+1)=F, D(+1)=E, I(+1)=J, C(+1)=D, I(+1)=J, N(+1)=O. Reversing FEJDJ O gives EOJDJEF (and M at the end). Result: EOJDJEFM."
    },
    {
        "category": "UPSC",
        "subject": "Reasoning",
        "question_text": "Pointing to a photograph, Vipul said, 'She is the daughter of my grandfather's only son.' How is the girl in the photograph related to Vipul?",
        "option_a": "Sister",
        "option_b": "Niece",
        "option_c": "Cousin",
        "option_d": "Mother",
        "correct_option": "A",
        "explanation": "Vipul's grandfather's only son is Vipul's father. The daughter of Vipul's father is Vipul's sister. Hence, the girl is Vipul's sister."
    },
    {
        "category": "State PSC",
        "subject": "Reasoning",
        "question_text": "A man walks 5 km toward South, then turns right and walks 3 km. He then turns left and walks 5 km. In which direction is he now from the starting point?",
        "option_a": "South",
        "option_b": "South-West",
        "option_c": "South-East",
        "option_d": "West",
        "correct_option": "B",
        "explanation": "Starting at origin (0,0): walk 5 km South -> (0, -5). Turn right (facing West) and walk 3 km -> (-3, -5). Turn left (facing South) and walk 5 km -> (-3, -10). The coordinate (-3, -10) lies in the South-West quadrant relative to the origin."
    },
    {
        "category": "UPSC",
        "subject": "Reasoning",
        "question_text": "Consider the following statements and choose the correct conclusion:\nStatements:\n1. All cups are books.\n2. All books are shirts.\nConclusions:\nI. All cups are shirts.\nII. Some shirts are cups.",
        "option_a": "Only conclusion I follows",
        "option_b": "Only conclusion II follows",
        "option_c": "Neither I nor II follows",
        "option_d": "Both I and II follow",
        "correct_option": "D",
        "explanation": "Since all cups are books and all books are shirts, all cups must be shirts (Conclusion I follows). Since all cups are shirts, some shirts are cups (Conclusion II follows). Thus, both conclusions follow."
    },
    {
        "category": "SSC",
        "subject": "Reasoning",
        "question_text": "Find the next term in the letter series: BDF, HJL, NPR, ?",
        "option_a": "QSU",
        "option_b": "TVX",
        "option_c": "SUW",
        "option_d": "UWY",
        "correct_option": "B",
        "explanation": "Each term consists of consecutive letters with one skipped (B_D_F, H_J_L, N_P_R). The gap between terms is also skipping one letter (F_H, L_N, R_T). The next starting letter is T, followed by V, and X. Result: TVX."
    },
    {
        "category": "General",
        "subject": "Reasoning",
        "question_text": "Choose the word pair that matches the relationship: 'Calendar : Date :: Dictionary : ?'",
        "option_a": "Book",
        "option_b": "Words",
        "option_c": "Language",
        "option_d": "Library",
        "correct_option": "B",
        "explanation": "A calendar is used to look up dates. A dictionary is used to look up words."
    },
    {
        "category": "Railways",
        "subject": "Reasoning",
        "question_text": "If '+' means '-', '-' means '*', '*' means '/' and '/' means '+', then what is the value of: 15 - 3 + 10 / 5 * 5?",
        "option_a": "36",
        "option_b": "45",
        "option_c": "30",
        "option_d": "25",
        "correct_option": "A",
        "explanation": "Replacing operations: 15 * 3 - 10 + 5 / 5. According to BODMAS rules: division first -> 5/5 = 1. Then multiplication -> 15*3 = 45. The expression becomes 45 - 10 + 1 = 36."
    },
    {
        "category": "SSC",
        "subject": "Reasoning",
        "question_text": "Choose the word which is least like the other words in the group: Wheat, Barley, Rice, Mustard.",
        "option_a": "Wheat",
        "option_b": "Barley",
        "option_c": "Rice",
        "option_d": "Mustard",
        "correct_option": "D",
        "explanation": "Wheat, barley, and rice are foodgrain crops (cereals), whereas mustard is an oilseed crop."
    },
    {
        "category": "SSC",
        "subject": "Reasoning",
        "question_text": "If in a code language 'ROAD' is written as 'URDG', how is 'SWAN' written in that code?",
        "option_a": "VXDQ",
        "option_b": "VZDQ",
        "option_c": "VZCP",
        "option_d": "UXDQ",
        "correct_option": "B",
        "explanation": "The code shifts each letter forward by 3 (+3): R (+3) = U; O (+3) = R; A (+3) = D; D (+3) = G. Applying this to SWAN: S (+3) = V; W (+3) = Z; A (+3) = D; N (+3) = Q. Result: VZDQ."
    },
    {
        "category": "Railways",
        "subject": "Reasoning",
        "question_text": "Find the next term in the series: 2, 6, 12, 20, 30, 42, ?",
        "option_a": "52",
        "option_b": "54",
        "option_c": "56",
        "option_d": "60",
        "correct_option": "C",
        "explanation": "The differences between consecutive terms are increasing consecutive even numbers: 6-2=4; 12-6=6; 20-12=8; 30-20=10; 42-30=12. The next difference is 14. 42 + 14 = 56."
    },
    {
        "category": "General",
        "subject": "Reasoning",
        "question_text": "Raju faces North and walks 10 km. He turns right and walks 10 km, then turns left and walks 5 km. Which direction is he facing now?",
        "option_a": "North",
        "option_b": "South",
        "option_c": "East",
        "option_d": "West",
        "correct_option": "A",
        "explanation": "Start facing North: walks 10 km North (facing North). Turn right: facing East, walks 10 km. Turn left: facing North, walks 5 km. He is facing North."
    },
    {
        "category": "State PSC",
        "subject": "Reasoning",
        "question_text": "The sum of ages of 5 children born at the intervals of 3 years each is 50 years. What is the age of the youngest child?",
        "option_a": "4 years",
        "option_b": "8 years",
        "option_c": "10 years",
        "option_d": "12 years",
        "correct_option": "A",
        "explanation": "Let the age of the youngest child be x. The ages of the 5 children are x, x+3, x+6, x+9, x+12. Their sum is 5x + 30 = 50. 5x = 20 => x = 4. The youngest child is 4 years old."
    },
    {
        "category": "General",
        "subject": "Reasoning",
        "question_text": "In a row of trees, one tree is 7th from either end of the row. How many trees are there in the row?",
        "option_a": "11",
        "option_b": "12",
        "option_c": "13",
        "option_d": "14",
        "correct_option": "C",
        "explanation": "Number of trees = (Position from left) + (Position from right) - 1 = 7 + 7 - 1 = 13."
    }
]

def generate_ai_batch(api_key, count=10):
    """Call OpenRouter to generate a batch of unique reasoning MCQs using google/gemini-2.5-flash."""
    prompt = (
        f"Generate exactly {count} highly relevant, unique multiple choice questions (MCQs) on the subject: 'Reasoning' "
        f"(Logical Reasoning, Analytical Reasoning, Syllogisms, Blood Relations, Number Series, Coding-Decoding, or Direction Sense) "
        f"for Indian government competitive exams (UPSC, SSC, Banking, Railways, or State PSC).\n\n"
        f"CRITICAL REQUIREMENTS:\n"
        f"1. The 'question_text' must contain ONLY the direct question. Do not prefix or start the question with any exam references like 'Regarding UPSC CSAT:', 'For Banking exam:', or similar context phrases.\n"
        f"2. Categorize each question into the most appropriate exam category: 'UPSC', 'SSC', 'Banking', 'Railways', 'State PSC', or 'General' based on its complexity and nature.\n"
        f"3. Keep the 'explanation' concise (under 80 words) and direct. Do not write lengthy debates or meta-analyses.\n"
        f"4. You MUST respond ONLY with a valid JSON object containing a 'questions' key which is a list of exactly {count} objects. Do not include any introductory or concluding text, only the JSON block.\n\n"
        f"JSON schema:\n"
        f"{{\n"
        f"  \"questions\": [\n"
        f"    {{\n"
        f"      \"category\": \"one of the 6 categories listed above\",\n"
        f"      \"question_text\": \"The direct question text here\",\n"
        f"      \"option_a\": \"Text for option A\",\n"
        f"      \"option_b\": \"Text for option B\",\n"
        f"      \"option_c\": \"Text for option C\",\n"
        f"      \"option_d\": \"Text for option D\",\n"
        f"      \"correct_option\": \"A\" or \"B\" or \"C\" or \"D\",\n"
        f"      \"explanation\": \"Step-by-step reasoning logic under 80 words. Do not use unescaped double quotes inside this string.\"\n"
        f"    }}\n"
        f"  ]\n"
        f"}}"
    )

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://study-helper-gamma-sage.vercel.app",
        "X-Title": "SarkariPrep"
    }
    payload = {
        "model": "openrouter/free",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "max_tokens": 2500
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            print(f"  OpenRouter API returned error {response.status_code}: {response.text}")
            return []

        res_json = response.json()
        text = res_json['choices'][0]['message']['content'].strip()

        # Clean markdown wrappers if returned
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        data = json.loads(text, strict=False)
        questions_list = []
        if isinstance(data, dict):
            if "questions" in data and isinstance(data["questions"], list):
                questions_list = data["questions"]
            else:
                for k, v in data.items():
                    if isinstance(v, list):
                        questions_list = v
                        break
        elif isinstance(data, list):
            questions_list = data

        valid = []
        for item in questions_list:
            required = ["category", "question_text", "option_a", "option_b", "option_c", "option_d", "correct_option", "explanation"]
            if all(k in item for k in required):
                item["correct_option"] = item["correct_option"].strip().upper()
                if item["correct_option"] in ["A", "B", "C", "D"]:
                    valid.append(item)
        return valid
    except Exception as e:
        print(f"  API call failed: {e}")
        return []

def main():
    connections = []

    # 1. Connect to SQLite
    try:
        sqlite_conn = sqlite3.connect("study_helper.db")
        connections.append(("SQLite (Local)", sqlite_conn))
    except Exception as e:
        print(f"Warning: Could not connect to SQLite: {e}")

    # 2. Connect to Postgres
    postgres_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if postgres_url:
        try:
            import psycopg2
            from database import PostgresConnectionWrapper
            pg_conn = psycopg2.connect(postgres_url, sslmode='require', connection_factory=PostgresConnectionWrapper)
            connections.append(("PostgreSQL (Cloud)", pg_conn))
        except Exception as e:
            print(f"Warning: Could not connect to PostgreSQL: {e}")

    print(f"Connected databases: {[name for name, _ in connections]}")

    # Step A: Seed the 15 predefined reasoning questions first
    inserted_predef = 0
    for q in PREDEFINED_REASONING:
        for db_name, conn in connections:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM questions WHERE question_text = ?",
                    (q["question_text"],)
                )
                if cursor.fetchone():
                    continue

                cursor.execute('''
                INSERT INTO questions 
                (category, subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, is_ai_generated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                ''', (
                    q["category"],
                    "Reasoning",
                    q["question_text"],
                    q["option_a"],
                    q["option_b"],
                    q["option_c"],
                    q["option_d"],
                    q["correct_option"],
                    q["explanation"]
                ))
                inserted_predef += 1
            except Exception as e:
                print(f"Error seeding predefined in {db_name}: {e}")

    for db_name, conn in connections:
        conn.commit()

    print(f"Seeded {inserted_predef} predefined Reasoning questions.")

    # Step B: Check current total and generate more if Gemini API key is available
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Notice: GEMINI_API_KEY environment variable is not set.")
        print("To generate up to 100 questions automatically, please run:")
        print("  $env:GEMINI_API_KEY=\"your-api-key-here\"; python add_reasoning_questions.py")
        sys.exit(0)

    # Let's count how many reasoning questions we currently have in SQLite (local primary)
    primary_conn = sqlite3.connect("study_helper.db")
    cursor = primary_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM questions WHERE subject = 'Reasoning'")
    current_count = cursor.fetchone()[0]
    primary_conn.close()

    print(f"Current Reasoning question count: {current_count}")
    target_count = 100
    
    if current_count >= target_count:
        print(f"Reasoning section already has {current_count} questions (target is 100). Done!")
        return

    needed = target_count - current_count
    print(f"Generating and seeding remaining {needed} Reasoning questions using Gemini...")

    generated_total = 0
    while current_count < target_count:
        batch_size = min(2, target_count - current_count)
        print(f"Requesting {batch_size} questions from Gemini...")
        questions = generate_ai_batch(api_key, batch_size)
        if not questions:
            print("  Failed to get batch. Retrying in 10 seconds...")
            time.sleep(10)
            continue

        inserted_in_batch = 0
        for q in questions:
            for db_name, conn in connections:
                try:
                    cursor = conn.cursor()
                    cursor.execute('''
                    INSERT INTO questions 
                    (category, subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, is_ai_generated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    ''', (
                        q["category"],
                        "Reasoning",
                        q["question_text"],
                        q["option_a"],
                        q["option_b"],
                        q["option_c"],
                        q["option_d"],
                        q["correct_option"],
                        q["explanation"]
                    ))
                    inserted_in_batch += 1
                except Exception as e:
                    pass

        for db_name, conn in connections:
            conn.commit()

        current_count += len(questions)
        generated_total += len(questions)
        print(f"  Successfully added {len(questions)} questions. Current total: {current_count}/100")
        
        # Rate limit safety delay
        time.sleep(8)

    # Close all connections
    for db_name, conn in connections:
        conn.close()

    print(f"\nCompleted! Generated and seeded {generated_total} new reasoning questions. Total count is now 100.")

if __name__ == "__main__":
    main()
