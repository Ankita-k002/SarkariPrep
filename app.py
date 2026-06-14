import os
import json
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import database

app = Flask(__name__)
# Secure session key configuration: uses environment variable in production, falls back to dev key locally
app.secret_key = os.environ.get("SECRET_KEY", "sarkariprep_secure_session_key_2026")

# Ensure database is initialized
database.init_db()

# Main page route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sw.js')
def serve_sw():
    return app.send_static_file('sw.js')

@app.route('/manifest.json')
def serve_manifest():
    return app.send_static_file('manifest.json')

# --- AUTH API ENDPOINTS ---

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    password = data.get('password', '')
    
    if not name or not password:
        return jsonify({"success": False, "message": "Name and password are required."}), 400
        
    result = database.register_user(name, password)
    if result["success"]:
        session["user_id"] = result["user_id"]
        session["username"] = result["name"]
        return jsonify({"success": True, "message": "Signup successful!"})
    else:
        return jsonify({"success": False, "message": result["message"]}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    password = data.get('password', '')
    
    if not name or not password:
        return jsonify({"success": False, "message": "Name and password are required."}), 400
        
    result = database.authenticate_user(name, password)
    if result["success"]:
        session["user_id"] = result["user"]["id"]
        session["username"] = result["user"]["name"]
        return jsonify({
            "success": True, 
            "message": "Login successful!",
            "user": result["user"]
        })
    else:
        return jsonify({"success": False, "message": result["message"]}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route('/api/auth/me', methods=['GET'])
def me():
    if "user_id" not in session:
        return jsonify({"authenticated": False}), 200
        
    stats = database.get_user_stats(session["user_id"])
    if not stats:
        session.clear()
        return jsonify({"authenticated": False}), 200
        
    return jsonify({
        "authenticated": True,
        "user": {
            "id": session["user_id"],
            "name": session["username"],
            "streak": stats["streak"]
        }
    })

# --- QUIZ & QUESTION API ENDPOINTS ---

@app.route('/api/quiz/question', methods=['GET'])
def get_question():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    user_id = session["user_id"]
    category = request.args.get('category', 'General')
    subject = request.args.get('subject', '')
    
    # Fetch from seeded database directly
    question = database.get_random_question(category, subject, user_id)
    
    if not question:
        # If no questions match the filter, try fetching any general question
        question = database.get_random_question("General", None, user_id)
        
    if not question:
        return jsonify({"success": False, "message": "No questions available in the database."}), 404
        
    # Mask correct answer on the frontend request to prevent cheating!
    frontend_question = {
        "id": question["id"],
        "category": question["category"],
        "subject": question["subject"],
        "question_text": question["question_text"],
        "option_a": question["option_a"],
        "option_b": question["option_b"],
        "option_c": question["option_c"],
        "option_d": question["option_d"],
        "is_ai_generated": question["is_ai_generated"],
        "is_bookmarked": question["is_bookmarked"]
    }
    
    return jsonify({"success": True, "question": frontend_question})

@app.route('/api/quiz/submit', methods=['POST'])
def submit_answer():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    user_id = session["user_id"]
    data = request.get_json() or {}
    question_id = data.get('question_id')
    selected_option = data.get('selected_option', '').strip().upper()
    
    if not question_id or selected_option not in ['A', 'B', 'C', 'D']:
        return jsonify({"success": False, "message": "Invalid answer format."}), 400
        
    # Fetch correct answer from DB
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT correct_option, explanation FROM questions WHERE id = ?",
        (question_id,)
    )
    q = cursor.fetchone()
    conn.close()
    
    if not q:
        return jsonify({"success": False, "message": "Question not found."}), 404
        
    correct_option = q["correct_option"]
    explanation = q["explanation"]
    is_correct = 1 if selected_option == correct_option else 0
    
    # Save attempt and update streak
    database.record_attempt(user_id, question_id, selected_option, is_correct)
    
    return jsonify({
        "success": True,
        "is_correct": is_correct == 1,
        "correct_option": correct_option,
        "explanation": explanation
    })

@app.route('/api/quiz/bookmark', methods=['POST'])
def bookmark_question():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    user_id = session["user_id"]
    data = request.get_json() or {}
    question_id = data.get('question_id')
    
    if not question_id:
        return jsonify({"success": False, "message": "Question ID required."}), 400
        
    success = database.add_bookmark(user_id, question_id)
    return jsonify({"success": success})

@app.route('/api/quiz/unbookmark', methods=['POST'])
def unbookmark_question():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    user_id = session["user_id"]
    data = request.get_json() or {}
    question_id = data.get('question_id')
    
    if not question_id:
        return jsonify({"success": False, "message": "Question ID required."}), 400
        
    database.remove_bookmark(user_id, question_id)
    return jsonify({"success": True})

# --- USER & STATS API ENDPOINTS ---

@app.route('/api/user/history', methods=['GET'])
def user_history():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    history = database.get_user_history(session["user_id"])
    return jsonify({"success": True, "history": history})

@app.route('/api/user/bookmarks', methods=['GET'])
def user_bookmarks():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    bookmarks = database.get_bookmarked_questions(session["user_id"])
    return jsonify({"success": True, "bookmarks": bookmarks})

@app.route('/api/user/stats', methods=['GET'])
def user_stats():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    stats = database.get_user_stats(session["user_id"])
    return jsonify({"success": True, "stats": stats})

@app.route('/api/user/settings', methods=['GET', 'POST'])
def user_settings():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    user_id = session["user_id"]
    
    if request.method == 'POST':
        data = request.get_json() or {}
        api_key = data.get('gemini_api_key', '').strip()
        use_ai = 1 if data.get('use_ai_generation') else 0
        
        database.save_user_settings(user_id, api_key, use_ai)
        return jsonify({"success": True, "message": "Settings saved successfully."})
    else:
        settings = database.get_user_settings(user_id)
        # Hide the exact api key partially on read for security, but allow updating it
        key = settings["gemini_api_key"]
        masked_key = ""
        if key:
            masked_key = key[:6] + "..." + key[-4:] if len(key) > 10 else "..."
        return jsonify({
            "success": True,
            "settings": {
                "use_ai_generation": settings["use_ai_generation"] == 1,
                "has_api_key": bool(key),
                "masked_api_key": masked_key
            }
        })

# --- GEMINI AI INTEGRATION HELPER ---

def generate_ai_question(category, subject, api_key):
    # Constructing a structured prompt to ensure we get a valid JSON response
    subj_str = subject if subject else "General Knowledge and Current Affairs"
    
    prompt = (
        f"Generate exactly one highly relevant multiple choice question (MCQ) for the Indian government exam '{category}' "
        f"on the subject '{subj_str}'. The question should reflect the difficulty and topics seen in actual competitive exams "
        f"(like UPSC, SSC, Banking, Railways, or State PSC). If the subject is Current Affairs, focus on significant day-to-day events from 2025 or 2026.\n\n"
        f"CRITICAL REQUIREMENT: The 'question_text' must contain ONLY the actual question itself. "
        f"DO NOT prefix or begin the question with any reference to the exam or preparation, such as 'Regarding SSC preparation:', "
        f"'For the upcoming UPSC exam:', 'As a Banking aspirant:', or similar context phrases. Start the question directly and professionally.\n\n"
        f"You MUST respond ONLY with a valid JSON object. Do not include any introductory or concluding text, only the JSON block. "
        f"The JSON object must have the following exact schema:\n"
        f"{{\n"
        f"  \"question_text\": \"State the direct question content here without exam prefaces\",\n"
        f"  \"option_a\": \"Text for option A\",\n"
        f"  \"option_b\": \"Text for option B\",\n"
        f"  \"option_c\": \"Text for option C\",\n"
        f"  \"option_d\": \"Text for option D\",\n"
        f"  \"correct_option\": \"A\" or \"B\" or \"C\" or \"D\",\n"
        f"  \"explanation\": \"Provide a thorough educational explanation explaining the background context and why the chosen option is correct.\"\n"
        f"}}\n"
    )
    
    # Call Gemini API
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
    
    response = requests.post(url, headers=headers, json=payload, timeout=12)
    if response.status_code != 200:
        raise Exception(f"Gemini API returned status code {response.status_code}: {response.text}")
        
    res_json = response.json()
    try:
        text = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        # Clean markdown wrappers if returned
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        data = json.loads(text)
        
        # Verify required keys exist
        required_keys = ["question_text", "option_a", "option_b", "option_c", "option_d", "correct_option", "explanation"]
        for k in required_keys:
            if k not in data:
                raise KeyError(f"Missing key in AI response: {k}")
                
        # Standardize correct option
        data["correct_option"] = data["correct_option"].strip().upper()
        if data["correct_option"] not in ["A", "B", "C", "D"]:
            raise ValueError(f"Invalid correct_option value: {data['correct_option']}")
            
        return data
    except (KeyError, IndexError, ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing Gemini API JSON: {e}")
        # Log response body for debugging
        print(f"Raw response: {res_json}")
        return None

if __name__ == '__main__':
    # Listen on all local interfaces using an adhoc SSL context for HTTPS support
    app.run(debug=True, host="0.0.0.0", port=5000, ssl_context='adhoc')
