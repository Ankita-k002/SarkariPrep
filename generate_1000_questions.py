import os
import sys
import json
import time
import requests
import argparse
import database

# Check if Gemini API key is provided
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable is not set.")
    print("Please run the script as follows:")
    print("  Windows PowerShell:")
    print('    $env:GEMINI_API_KEY="your-api-key-here"; python generate_1000_questions.py')
    print("  Linux/macOS Bash:")
    print('    export GEMINI_API_KEY="your-api-key-here"; python generate_1000_questions.py')
    sys.exit(1)

# Ensure database tables exist
print("Initializing database connection...")
database.init_db()

# List of 50 distinct current affairs topics to generate 20 questions each (Total 1000 questions)
# Focusing on significant events, developments, and policies in India and globally from 2025 and 2026.
TOPICS = [
    "Indian Economy, Union Budget 2025-26, and Economic Survey findings",
    "Indian Economy, Union Budget 2026-27, and key monetary policy revisions",
    "Reserve Bank of India (RBI) circulars, banking regulations, digital lending guidelines from 2025",
    "SEBI, stock market regulations, IPO reforms, and financial sector news from 2025-2026",
    "Science & Technology developments in India, indigenous initiatives, and semiconductor missions in 2025",
    "Space Exploration, ISRO missions (Gaganyaan, Chandrayaan developments, Aditya-L1 results) in 2025-2026",
    "Ecology, Climate Change summits (COP30, COP29), and India's renewable energy goals in 2025-2026",
    "Ecology, forest conservation, wildlife protection acts, and new national parks/sanctuaries in 2025",
    "Government Schemes, Pradhan Mantri schemes, and social welfare programs launched or updated in 2025",
    "Government Schemes, rural development initiatives, and agricultural subsidies in 2025-2026",
    "National Bills, Acts passed by Indian Parliament, and constitutional amendments in 2025-2026",
    "International Relations, G20 Summits (2024-2026), and India's role in global forums",
    "International Relations, BRICS expansion, and bilateral agreements signed by India in 2025",
    "Sports, ICC T20 World Cup 2024, ICC Champions Trophy 2025, and major cricket tournament results",
    "Sports, Paris Olympic Games 2024 highlights, Commonwealth Games developments, and Indian medalists",
    "Awards & Honors, Bharat Ratna, Padma Awards, and national sports awards in 2025-2026",
    "Awards & Honors, Nobel Prizes, Oscar winners, and international literary prizes in 2025-2026",
    "Defense, joint military exercises of India (Army, Navy, Air Force) with other nations in 2025",
    "Defense procurement, indigenous defense production (DRDO, HAL), and missile test flights in 2025-2026",
    "Important Days, national/international themes, and global observances in 2025-2026",
    "Reports, international indices (Human Development Index, Hunger Index, Happiness Index) and India's rank in 2025",
    "Reports, national rankings, clean city surveys (Swachh Survekshan), and NITI Aayog indices in 2025-2026",
    "National News, supreme court judgments, and landmark judicial rulings in 2025-2026",
    "National News, state-level legislation (e.g. Uniform Civil Code, local reservations) in 2025-2026",
    "Infrastructure developments, highway projects (Bharatmala, Bullet Train progress), and port developments in 2025",
    "Art, Culture, newly recognized UNESCO heritage sites, and GI tags awarded to products in 2025-2026",
    "Appointments, key national positions (CJI, Chief Election Commissioner, Cabinet Secretary) in 2025-2026",
    "Appointments, international positions (UN heads, IMF/World Bank leadership, foreign presidents) in 2025-2026",
    "E-governance initiatives, digital India upgrades, AI regulation guidelines in India in 2025",
    "Agriculture, MSP announcements, agricultural technology (Agritech) breakthroughs in 2025-2026",
    "Energy sector, green hydrogen mission progress, solar power park commissions in India in 2025",
    "Education sector reforms, implementation of NEP, and new higher education regulations in 2025-2026",
    "Health sector developments, national digital health mission progress, vaccine distributions in 2025-2026",
    "Disaster management, major cyclones, earthquakes, and flood relief operations in India in 2025-2026",
    "Summit meetings, QUAD summits, SCO summits, and ASEAN-India meetings in 2025-2026",
    "Bilateral trades, free trade agreements (FTAs) negotiated by India in 2025-2026",
    "Geographical indications (GI tags) awarded to handicrafts, agricultural items, and food in 2025",
    "State-level schemes, social benefits, and economic milestones of Indian states in 2025-2026",
    "Cybersecurity developments, major global cyber threats, and Indian digital protection frameworks in 2025",
    "Startup ecosystem in India, unicorn milestones, and venture capital regulations in 2025-2026",
    "Blue Economy initiatives, deep ocean mission, and coastal zone management developments in 2025-2026",
    "Tribal welfare, national commissions, and cultural festivals of tribal communities in 2025-2026",
    "Tourism development, PRASHAD scheme progress, and spiritual heritage sites development in 2025",
    "Environment, carbon credit markets framework, and net zero emission milestones in India in 2025-2026",
    "Monetary Policy, repo rate changes, inflation rates, and GDP projections of India in 2025-2026",
    "Bilateral defense deals, defense technology transfers, and naval acquisitions in 2025-2026",
    "Major demographic studies, census updates, and health indices of Indian states in 2025-2026",
    "Space Startups, private satellite launches, and commercial activities of NSIL/IN-SPACe in 2025-2026",
    "Historical monuments renovations, archaeological findings, and museum inaugurations in India in 2025-2026",
    "International financial institutions, loans approved to India by ADB, NDB, and World Bank in 2025-2026"
]

def generate_batch(topic, topic_idx, total_topics, sub_idx):
    prompt = (
        f"Generate exactly 10 highly relevant, unique multiple choice questions (MCQs) for Indian government competitive exams "
        f"on the Current Affairs topic: '{topic}' (Part {sub_idx} of 2).\n"
        f"The questions should focus on significant, factual developments and events from 2025 and 2026.\n\n"
        f"CRITICAL REQUIREMENTS:\n"
        f"1. The 'question_text' must contain ONLY the direct question. Do not prefix or start the question with any exam references like 'Regarding UPSC:', 'For Banking exam:', or similar context phrases.\n"
        f"2. Categorize each question into the most appropriate exam category: 'UPSC', 'SSC', 'Banking', 'Railways', 'State PSC', or 'General' based on its complexity and nature.\n"
        f"3. You MUST respond ONLY with a valid JSON array of exactly 10 objects. Do not include any introductory or concluding text, only the JSON block.\n\n"
        f"JSON schema:\n"
        f"[\n"
        f"  {{\n"
        f"    \"category\": \"one of the 6 categories listed above\",\n"
        f"    \"question_text\": \"The direct question text here\",\n"
        f"    \"option_a\": \"Text for option A\",\n"
        f"    \"option_b\": \"Text for option B\",\n"
        f"    \"option_c\": \"Text for option C\",\n"
        f"    \"option_d\": \"Text for option D\",\n"
        f"    \"correct_option\": \"A\" or \"B\" or \"C\" or \"D\",\n"
        f"    \"explanation\": \"Provide a thorough explanation explaining the background context and why the chosen option is correct.\"\n"
        f"  }}\n"
        f"]"
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    print(f"[{topic_idx}/{total_topics}] (Part {sub_idx}/2) Requesting 10 questions for: {topic}...")
    sys.stdout.flush() # Force flush to make sure it writes to log immediately
    
    # Retry logic
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 429:
                print("  Rate limit reached (429). Sleeping 30 seconds to reset quota...")
                sys.stdout.flush()
                time.sleep(30)
                continue
            if response.status_code != 200:
                print(f"  API returned error {response.status_code}: {response.text}. Retrying...")
                sys.stdout.flush()
                time.sleep(5)
                continue
                
            res_json = response.json()
            text = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # Clean markdown wrappers if returned
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            data = json.loads(text)
            if not isinstance(data, list):
                raise ValueError("Response is not a JSON list")
                
            # Basic validation
            valid_questions = []
            for item in data:
                required = ["category", "question_text", "option_a", "option_b", "option_c", "option_d", "correct_option", "explanation"]
                if all(k in item for k in required):
                    # Clean correct option
                    item["correct_option"] = item["correct_option"].strip().upper()
                    if item["correct_option"] in ["A", "B", "C", "D"]:
                        valid_questions.append(item)
            
            return valid_questions
            
        except Exception as e:
            print(f"  Attempt {attempt+1} failed with error: {e}")
            sys.stdout.flush()
            time.sleep(5)
            
    print(f"  Failed to generate batch for topic after 3 attempts.")
    sys.stdout.flush()
    return []

def main():
    parser = argparse.ArgumentParser(description="Generate Current Affairs questions using Gemini API.")
    parser.add_argument("--start", type=int, default=1, help="Topic index to start from (1-50)")
    parser.add_argument("--limit", type=int, default=0, help="Number of topics to process in this run (0 for all)")
    parser.add_argument("--delay", type=float, default=10.0, help="Delay in seconds between API calls (default: 10.0)")
    args = parser.parse_args()

    total_topics = len(TOPICS)
    start_idx = max(1, min(args.start, total_topics))
    limit_topics = args.limit if args.limit > 0 else (total_topics - start_idx + 1)
    end_idx = min(start_idx + limit_topics - 1, total_topics)
    
    print(f"Starting generation of current affairs questions.")
    print(f"Processing topics {start_idx} to {end_idx} (out of {total_topics} total topics).")
    print(f"Target Database: {'PostgreSQL (Neon)' if database.IS_POSTGRES else 'SQLite (Local)'}")
    sys.stdout.flush()
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    total_inserted = 0
    
    # Slice the topics to process
    topics_to_process = list(enumerate(TOPICS, 1))[start_idx - 1 : end_idx]
    
    for topic_idx, topic in topics_to_process:
        for sub_idx in [1, 2]:
            questions = generate_batch(topic, topic_idx, total_topics, sub_idx)
            if not questions:
                continue
                
            inserted_in_batch = 0
            for q in questions:
                try:
                    # We save all these under subject = 'Current Affairs'
                    cursor.execute('''
                    INSERT INTO questions 
                    (category, subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, is_ai_generated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    ''', (
                        q["category"],
                        "Current Affairs",
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
                    # In case of duplicate or format error
                    pass
                    
            conn.commit()
            total_inserted += inserted_in_batch
            print(f"  (Part {sub_idx}/2) Successfully inserted {inserted_in_batch} questions. (Total so far: {total_inserted})")
            sys.stdout.flush()
            
            # Respect Gemini API rate limit: wait before the next call
            time.sleep(args.delay)
        
    conn.close()
    print("\n============================================")
    print(f"Generation complete! Inserted {total_inserted} new questions into the database.")
    print("============================================")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
