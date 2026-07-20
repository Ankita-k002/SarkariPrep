# API Documentation

This file documents the application API endpoints and routes exposed by the backend, mapped to frontend call locations.

For database tables and backend source descriptions, see [[Architecture]].

---

## 🔌 API Endpoints Mapped

### `/`
* **HTTP Methods**: `GET`
* **Backend Handler**: `index()` in [[app.py]]
* **Frontend Caller**: *None directly detected*
* **Description**: 
  > No description provided.

---

### `/sw.js`
* **HTTP Methods**: `GET`
* **Backend Handler**: `serve_sw()` in [[app.py]]
* **Frontend Caller**: *None directly detected*
* **Description**: 
  > No description provided.

---

### `/manifest.json`
* **HTTP Methods**: `GET`
* **Backend Handler**: `serve_manifest()` in [[app.py]]
* **Frontend Caller**: *None directly detected*
* **Description**: 
  > No description provided.

---

### `/api/auth/signup`
* **HTTP Methods**: `POST`
* **Backend Handler**: `signup()` in [[app.py]]
* **Frontend Caller**: `handleAuthSubmit()`
* **Description**: 
  > No description provided.

---

### `/api/auth/login`
* **HTTP Methods**: `POST`
* **Backend Handler**: `login()` in [[app.py]]
* **Frontend Caller**: `handleAuthSubmit()`
* **Description**: 
  > No description provided.

---

### `/api/auth/logout`
* **HTTP Methods**: `POST`
* **Backend Handler**: `logout()` in [[app.py]]
* **Frontend Caller**: `handleLogout()`
* **Description**: 
  > No description provided.

---

### `/api/auth/me`
* **HTTP Methods**: `GET`
* **Backend Handler**: `me()` in [[app.py]]
* **Frontend Caller**: `checkAuthSession()`
* **Description**: 
  > No description provided.

---

### `/api/quiz/question`
* **HTTP Methods**: `GET`
* **Backend Handler**: `get_question()` in [[app.py]]
* **Frontend Caller**: *None directly detected*
* **Description**: 
  > No description provided.

---

### `/api/quiz/submit`
* **HTTP Methods**: `POST`
* **Backend Handler**: `submit_answer()` in [[app.py]]
* **Frontend Caller**: `selectOption()`
* **Description**: 
  > No description provided.

---

### `/api/quiz/bookmark`
* **HTTP Methods**: `POST`
* **Backend Handler**: `bookmark_question()` in [[app.py]]
* **Frontend Caller**: `toggleBookmarkCurrentQuestion()`
* **Description**: 
  > No description provided.

---

### `/api/quiz/unbookmark`
* **HTTP Methods**: `POST`
* **Backend Handler**: `unbookmark_question()` in [[app.py]]
* **Frontend Caller**: `toggleBookmarkCurrentQuestion()`
* **Description**: 
  > No description provided.

---

### `/api/user/history`
* **HTTP Methods**: `GET`
* **Backend Handler**: `user_history()` in [[app.py]]
* **Frontend Caller**: `loadHistory()`
* **Description**: 
  > No description provided.

---

### `/api/user/bookmarks`
* **HTTP Methods**: `GET`
* **Backend Handler**: `user_bookmarks()` in [[app.py]]
* **Frontend Caller**: *None directly detected*
* **Description**: 
  > No description provided.

---

### `/api/user/stats`
* **HTTP Methods**: `GET`
* **Backend Handler**: `user_stats()` in [[app.py]]
* **Frontend Caller**: `initializeDashboard()`, `loadStatsDashboard()`
* **Description**: 
  > No description provided.

---

### `/api/user/settings`
* **HTTP Methods**: `GET, POST`
* **Backend Handler**: `user_settings()` in [[app.py]]
* **Frontend Caller**: *None directly detected*
* **Description**: 
  > No description provided.

---



## 🔗 Related Documents
* [[Project Overview]]
* [[Architecture]]

Generated at: 2026-07-21 00:26:54
