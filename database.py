import sqlite3
import hashlib
import os
from datetime import datetime, date

# Database selection: check if a cloud PostgreSQL database URL is configured
DATABASE_URL = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL") or os.environ.get("STORAGE_URL")
IS_POSTGRES = bool(DATABASE_URL)

if IS_POSTGRES:
    # Adjust Vercel/Supabase url prefix from 'postgres://' to 'postgresql://' for psycopg2 compatibility
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
    import psycopg2
    import psycopg2.extras
    import psycopg2.extensions
    DBIntegrityError = psycopg2.IntegrityError
    DBError = psycopg2.Error

    class PostgresConnectionWrapper(psycopg2.extensions.connection):
        def cursor(self, *args, **kwargs):
            if 'cursor_factory' not in kwargs:
                kwargs['cursor_factory'] = psycopg2.extras.DictCursor
            pg_cursor = super().cursor(*args, **kwargs)
            return PostgresCursorWrapper(pg_cursor)
else:
    DBIntegrityError = sqlite3.IntegrityError
    DBError = sqlite3.Error

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "study_helper.db")

# PostgreSQL wrapper to map parameter formats and primary key retrievals
class PostgresCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor
        self._lastrowid = None

    def execute(self, query, params=None):
        # Translate SQLite '?' parameter format to PostgreSQL '%s'
        if params is not None:
            query = query.replace('?', '%s')
            
        # Dynamically append RETURNING id to INSERT queries to mimic lastrowid functionality
        query_type = query.strip().split()[0].upper() if query.strip() else ""
        query_lower = query.lower()
        if query_type == "INSERT" and "returning" not in query_lower:
            # Only append RETURNING id for tables that have an auto-incrementing 'id' column and need lastrowid
            if "into users" in query_lower or "into questions" in query_lower:
                query_temp = query.rstrip('; ') + " RETURNING id"
                try:
                    if params is not None:
                        self.cursor.execute(query_temp, params)
                    else:
                        self.cursor.execute(query_temp)
                    row = self.cursor.fetchone()
                    if row:
                        self._lastrowid = row[0]
                    return
                except Exception:
                    pass

        if params is not None:
            return self.cursor.execute(query, params)
        else:
            return self.cursor.execute(query)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    @property
    def lastrowid(self):
        return self._lastrowid

    def __getattr__(self, name):
        return getattr(self.cursor, name)

def get_db_connection():
    if IS_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require', connection_factory=PostgresConnectionWrapper)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if IS_POSTGRES:
        # Create Users table (PostgreSQL schema)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            streak INTEGER DEFAULT 0,
            last_active VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create Questions table (PostgreSQL schema)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            category VARCHAR(255) NOT NULL,
            subject VARCHAR(255) NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option VARCHAR(10) NOT NULL,
            explanation TEXT NOT NULL,
            is_ai_generated INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create User Attempts table (PostgreSQL schema)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_attempts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            selected_option VARCHAR(10) NOT NULL,
            is_correct INTEGER NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
        ''')
        
        # Create Bookmarks table (PostgreSQL schema)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (question_id) REFERENCES questions (id),
            UNIQUE(user_id, question_id)
        )
        ''')

        # Create User Settings table (PostgreSQL schema)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            gemini_api_key TEXT,
            use_ai_generation INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
    else:
        # Create Users table (SQLite schema)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            streak INTEGER DEFAULT 0,
            last_active TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create Questions table (SQLite schema)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            subject TEXT NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL,
            explanation TEXT NOT NULL,
            is_ai_generated INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create User Attempts table (SQLite schema)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            selected_option TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
        ''')
        
        # Create Bookmarks table (SQLite schema)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (question_id) REFERENCES questions (id),
            UNIQUE(user_id, question_id)
        )
        ''')

        # Create User Settings table (SQLite schema)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            gemini_api_key TEXT,
            use_ai_generation INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# User Helpers
def register_user(name, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users (name, password, streak, last_active) VALUES (?, ?, 0, NULL)",
            (name, hashed)
        )
        user_id = cursor.lastrowid
        # Initialize default settings for user
        cursor.execute(
            "INSERT INTO user_settings (user_id, gemini_api_key, use_ai_generation) VALUES (?, ?, 0)",
            (user_id, "")
        )
        conn.commit()
        return {"success": True, "user_id": user_id, "name": name}
    except DBIntegrityError:
        return {"success": False, "message": "Username already exists."}
    finally:
        conn.close()

def authenticate_user(name, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute(
        "SELECT id, name, streak, last_active FROM users WHERE name = ? AND password = ?",
        (name, hashed)
    )
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "streak": user["streak"],
                "last_active": user["last_active"]
            }
        }
    return {"success": False, "message": "Invalid username or password."}

def update_user_streak(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT streak, last_active FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return
        
    current_streak = user["streak"]
    last_active_str = user["last_active"]
    today_str = date.today().isoformat()
    
    new_streak = current_streak
    if last_active_str is None:
        new_streak = 1
    else:
        last_active_date = datetime.strptime(last_active_str, "%Y-%m-%d").date()
        today_date = date.today()
        delta = (today_date - last_active_date).days
        
        if delta == 1:
            new_streak = current_streak + 1
        elif delta > 1:
            new_streak = 1
        # if delta == 0, they already practiced today, streak remains same.
        
    cursor.execute(
        "UPDATE users SET streak = ?, last_active = ? WHERE id = ?",
        (new_streak, today_str, user_id)
    )
    conn.commit()
    conn.close()
    return new_streak

# Question Helpers
def add_question(category, subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, is_ai=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO questions 
    (category, subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, is_ai_generated)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (category, subject, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, is_ai))
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return question_id

def get_random_question(category=None, subject=None, user_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    params = []
    conditions = []
    
    if category and category != 'General':
        conditions.append("category = ?")
        params.append(category)
        
    if subject:
        conditions.append("subject = ?")
        params.append(subject)
        
    base_where = ""
    if conditions:
        base_where = " AND ".join(conditions)
        
    question = None
    
    if user_id:
        # Phase 1: Try to fetch a question the user has NOT attempted yet
        query = "SELECT * FROM questions WHERE id NOT IN (SELECT question_id FROM user_attempts WHERE user_id = ?)"
        if base_where:
            query += " AND " + base_where
        query += " ORDER BY RANDOM() LIMIT 1"
        
        cursor.execute(query, [user_id] + params)
        question = cursor.fetchone()
        
        # Phase 2: If all questions are attempted, show ones they got wrong in the past (review mistakes)
        if not question:
            query = """
            SELECT * FROM questions 
            WHERE id IN (
                SELECT question_id FROM user_attempts 
                WHERE user_id = ?
                GROUP BY question_id
                HAVING SUM(is_correct) = 0
            )
            """
            if base_where:
                query += " AND " + base_where
            query += " ORDER BY RANDOM() LIMIT 1"
            
            cursor.execute(query, [user_id] + params)
            question = cursor.fetchone()
            
    # Phase 3 (Fallback): Fetch any random question matching the filter
    if not question:
        query = "SELECT * FROM questions"
        if base_where:
            query += " WHERE " + base_where
        query += " ORDER BY RANDOM() LIMIT 1"
        
        cursor.execute(query, params)
        question = cursor.fetchone()
        
    if not question:
        conn.close()
        return None
        
    q_dict = dict(question)
    
    # Check if bookmarked by the user
    is_bookmarked = 0
    if user_id:
        cursor.execute(
            "SELECT 1 FROM bookmarks WHERE user_id = ? AND question_id = ?",
            (user_id, q_dict["id"])
        )
        if cursor.fetchone():
            is_bookmarked = 1
            
    q_dict["is_bookmarked"] = is_bookmarked
    conn.close()
    return q_dict

# Attempt & History Helpers
def record_attempt(user_id, question_id, selected_option, is_correct):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO user_attempts (user_id, question_id, selected_option, is_correct)
    VALUES (?, ?, ?, ?)
    ''', (user_id, question_id, selected_option, is_correct))
    
    conn.commit()
    conn.close()
    
    # Trigger streak update
    update_user_streak(user_id)

def get_user_history(user_id, limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT 
        ua.id as attempt_id,
        ua.selected_option,
        ua.is_correct,
        ua.attempted_at,
        q.id as question_id,
        q.category,
        q.subject,
        q.question_text,
        q.option_a,
        q.option_b,
        q.option_c,
        q.option_d,
        q.correct_option,
        q.explanation,
        (SELECT 1 FROM bookmarks b WHERE b.user_id = ua.user_id AND b.question_id = q.id) as is_bookmarked
    FROM user_attempts ua
    JOIN questions q ON ua.question_id = q.id
    WHERE ua.user_id = ?
    ORDER BY ua.attempted_at DESC
    LIMIT ?
    ''', (user_id, limit))
    
    attempts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return attempts

# Bookmark Helpers
def add_bookmark(user_id, question_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO bookmarks (user_id, question_id) VALUES (?, ?) ON CONFLICT (user_id, question_id) DO NOTHING",
            (user_id, question_id)
        )
        conn.commit()
        return True
    except DBError:
        return False
    finally:
        conn.close()

def remove_bookmark(user_id, question_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM bookmarks WHERE user_id = ? AND question_id = ?",
        (user_id, question_id)
    )
    conn.commit()
    conn.close()

def get_bookmarked_questions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT 
        q.id as question_id,
        q.category,
        q.subject,
        q.question_text,
        q.option_a,
        q.option_b,
        q.option_c,
        q.option_d,
        q.correct_option,
        q.explanation,
        1 as is_bookmarked
    FROM bookmarks b
    JOIN questions q ON b.question_id = q.id
    WHERE b.user_id = ?
    ORDER BY b.created_at DESC
    ''', (user_id,))
    bookmarks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return bookmarks

# Stats Helper
def get_user_stats(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # User streak details
    cursor.execute("SELECT name, streak, last_active FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return None
        
    username = user["name"]
    streak = user["streak"]
    
    # Calculate global stats
    cursor.execute('''
    SELECT 
        COUNT(*) as total_attempted,
        SUM(case when is_correct = 1 then 1 else 0 end) as total_correct
    FROM user_attempts
    WHERE user_id = ?
    ''', (user_id,))
    
    row = cursor.fetchone()
    total_attempted = row["total_attempted"] or 0
    total_correct = row["total_correct"] or 0
    total_wrong = total_attempted - total_correct
    accuracy = round((total_correct / total_attempted * 100), 1) if total_attempted > 0 else 0.0
    
    # Category-wise stats
    cursor.execute('''
    SELECT 
        q.category,
        COUNT(ua.id) as attempted,
        SUM(ua.is_correct) as correct
    FROM user_attempts ua
    JOIN questions q ON ua.question_id = q.id
    WHERE ua.user_id = ?
    GROUP BY q.category
    ''', (user_id,))
    category_stats = {row["category"]: {"attempted": row["attempted"], "correct": row["correct"]} for row in cursor.fetchall()}
    
    # Subject-wise stats
    cursor.execute('''
    SELECT 
        q.subject,
        COUNT(ua.id) as attempted,
        SUM(ua.is_correct) as correct
    FROM user_attempts ua
    JOIN questions q ON ua.question_id = q.id
    WHERE ua.user_id = ?
    GROUP BY q.subject
    ''', (user_id,))
    subject_stats = {row["subject"]: {"attempted": row["attempted"], "correct": row["correct"]} for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        "username": username,
        "streak": streak,
        "total_attempted": total_attempted,
        "total_correct": total_correct,
        "total_wrong": total_wrong,
        "accuracy": accuracy,
        "category_stats": category_stats,
        "subject_stats": subject_stats
    }

# Settings Helper
def get_user_settings(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT gemini_api_key, use_ai_generation FROM user_settings WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "gemini_api_key": row["gemini_api_key"],
            "use_ai_generation": row["use_ai_generation"]
        }
    return {"gemini_api_key": "", "use_ai_generation": 0}

def save_user_settings(user_id, api_key, use_ai):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO user_settings (user_id, gemini_api_key, use_ai_generation)
    VALUES (?, ?, ?)
    ON CONFLICT (user_id) DO UPDATE SET
        gemini_api_key = EXCLUDED.gemini_api_key,
        use_ai_generation = EXCLUDED.use_ai_generation
    ''', (user_id, api_key, use_ai))
    conn.commit()
    conn.close()
