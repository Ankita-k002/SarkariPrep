import os
import sys
import sqlite3

# Define the Geography questions to insert
GEO_QUESTIONS = [
    {
        "category": "UPSC",
        "subject": "Geography",
        "question_text": "Which of the following passes connects Srinagar to Leh?",
        "option_a": "Zoji La",
        "option_b": "Nathu La",
        "option_c": "Shipki La",
        "option_d": "Bara-lacha La",
        "correct_option": "A",
        "explanation": "Zoji La is a high mountain pass in the Indian union territory of Ladakh, connecting Srinagar with Leh in the western Himalayas."
    },
    {
        "category": "State PSC",
        "subject": "Geography",
        "question_text": "In which state is the Loktak Lake, famous for its floating islands called 'Phumdis', located?",
        "option_a": "Assam",
        "option_b": "Manipur",
        "option_c": "Mizoram",
        "option_d": "Tripura",
        "correct_option": "B",
        "explanation": "Loktak Lake is the largest freshwater lake in Northeast India, located in Manipur. It is famous for the phumdis (mass of vegetation and soil) floating over it. Keibul Lamjao National Park, the world's only floating national park, sits on one of these phumdis."
    },
    {
        "category": "UPSC",
        "subject": "Geography",
        "question_text": "The river Brahmaputra, when it enters India in Arunachal Pradesh, is known by which of the following names?",
        "option_a": "Dihang",
        "option_b": "Dibang",
        "option_c": "Lohit",
        "option_d": "Subansiri",
        "correct_option": "A",
        "explanation": "The Brahmaputra River originates in Tibet as the Yarlung Tsangpo. It enters India near Gelling in Arunachal Pradesh, where it is known as the Dihang (or Siang) river, before being joined by the Lohit and Dibang rivers in Assam to become the Brahmaputra."
    },
    {
        "category": "SSC",
        "subject": "Geography",
        "question_text": "Which longitude is designated as the Standard Meridian of India, passing through Mirzapur in Uttar Pradesh?",
        "option_a": "82°30' E",
        "option_b": "84°30' E",
        "option_c": "80°30' E",
        "option_d": "88°30' E",
        "correct_option": "A",
        "explanation": "The longitude of 82°30' E is designated as the Standard Meridian of India. The local time at this meridian is taken as the Indian Standard Time (IST) for the whole country, which is 5.5 hours ahead of Greenwich Mean Time (GMT)."
    },
    {
        "category": "General",
        "subject": "Geography",
        "question_text": "Which of the following Indian states has the longest coastline?",
        "option_a": "Tamil Nadu",
        "option_b": "Maharashtra",
        "option_c": "Gujarat",
        "option_d": "Andhra Pradesh",
        "correct_option": "C",
        "explanation": "Gujarat has the longest coastline in India, stretching about 1,600 km, followed by Andhra Pradesh (~974 km) and Tamil Nadu (~906 km)."
    },
    {
        "category": "UPSC",
        "subject": "Geography",
        "question_text": "The Duncan Passage is a strait in the Indian Ocean that separates which of the following island groups?",
        "option_a": "Rutland Island (South Andaman) and Little Andaman",
        "option_b": "Car Nicobar and Great Nicobar",
        "option_c": "Minicoy and Amindivi Islands",
        "option_d": "South Andaman and North Andaman",
        "correct_option": "A",
        "explanation": "The Duncan Passage is a strait in the Indian Ocean. It is about 48 km wide and separates Rutland Island (part of South Andaman) to the north and Little Andaman to the south."
    },
    {
        "category": "Railways",
        "subject": "Geography",
        "question_text": "Which of the following rivers was historically referred to as the 'Sorrow of Bengal' due to frequent devastating floods?",
        "option_a": "Kosi River",
        "option_b": "Damodar River",
        "option_c": "Hooghly River",
        "option_d": "Mahanadi River",
        "correct_option": "B",
        "explanation": "The Damodar River was known as the 'Sorrow of Bengal' due to its ravaging floods in the plains of Bengal. The construction of the Damodar Valley Corporation (DVC) reservoirs later controlled the floods."
    },
    {
        "category": "State PSC",
        "subject": "Geography",
        "question_text": "Which of the following soil types, rich in iron oxide and potash, is best suited for cashew nut, tea, and coffee cultivation in India?",
        "option_a": "Laterite Soil",
        "option_b": "Alluvial Soil",
        "option_c": "Red Soil",
        "option_d": "Arid Soil",
        "correct_option": "A",
        "explanation": "Laterite soils develop in areas with high temperature and heavy rainfall. They are highly leached but, when properly manured, are excellent for growing tea, coffee, and cashew nuts."
    },
    {
        "category": "SSC",
        "subject": "Geography",
        "question_text": "Which channel or strait separates the Andaman Islands from the Nicobar Islands in the Bay of Bengal?",
        "option_a": "Eight Degree Channel",
        "option_b": "Nine Degree Channel",
        "option_c": "Ten Degree Channel",
        "option_d": "Palk Strait",
        "correct_option": "C",
        "explanation": "The Ten Degree Channel separates the Andaman Islands from the Nicobar Islands in the Bay of Bengal. It lies on the 10-degree N latitude line."
    },
    {
        "category": "General",
        "subject": "Geography",
        "question_text": "The Majuli island, recognized as the largest river island in the world, is formed by which river system in Assam?",
        "option_a": "Ganga",
        "option_b": "Brahmaputra",
        "option_c": "Barak",
        "option_d": "Indus",
        "correct_option": "B",
        "explanation": "Majuli is a large river island in the Brahmaputra River, Assam. It is the first island to be made a district in India and is recognized by Guinness World Records as the world's largest river island."
    }
]

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
    
    inserted_count = 0
    for q in GEO_QUESTIONS:
        for db_name, conn in connections:
            try:
                cursor = conn.cursor()
                # Check if question already exists to prevent duplicate seeding
                cursor.execute(
                    "SELECT 1 FROM questions WHERE question_text = ?",
                    (q["question_text"],)
                )
                if cursor.fetchone():
                    continue
                
                # SQLite / Postgres param syntax mapping handled inside wrapper for Postgres
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
                inserted_count += 1
            except Exception as e:
                print(f"Error inserting question into {db_name}: {e}")
                
    for db_name, conn in connections:
        try:
            conn.commit()
            conn.close()
        except Exception as e:
            pass
            
    print(f"Successfully seeded {inserted_count} premium Geography questions into connected databases.")

if __name__ == "__main__":
    main()
