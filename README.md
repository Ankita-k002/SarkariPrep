# SarkariPrep - Exam Study Helper

SarkariPrep is a mobile-first, installable Progressive Web App (PWA) designed to help students prepare for Indian government exams (UPSC, SSC, Banking, Railways, State PSC, and General Knowledge). 

It features streak tracking, quiz statistics, detailed answer history, bookmarking, and dynamic AI-powered question generation using Gemini 2.5 Flash.

## 🌟 Features

- **PWA Support**: Installable directly onto mobile home screens (requires HTTPS / Vercel deployment).
- **Exam Categories**: Practice MCQs customized for UPSC, SSC, Banking, Railways, State PSC, and General GK.
- **Streak & Accuracy Tracking**: View daily study streaks and overall accuracy rates.
- **Practice History**: Review all attempted questions with detailed explanations.
- **Bookmarking**: Save challenging questions to review later.
- **Dynamic AI Mode**: Enable AI generation in settings to generate brand new competitive exam MCQs dynamically using Gemini.

---

## 📁 Project Structure

```text
├── api/
│   └── index.py            # Vercel serverless entrypoint
├── templates/
│   └── index.html          # Main SPA template markup
├── static/
│   ├── css/
│   │   └── style.css       # Clean, forest-green theme styles
│   ├── js/
│   │   └── app.js          # Main SPA frontend router and engine
│   ├── img/
│   │   └── study_banner.png # Dashboard marketing graphics
│   ├── manifest.json       # PWA Manifest configuration
│   └── sw.js               # Service Worker for local caching
├── app.py                  # Flask application routes
├── database.py             # SQLite (Local) / PostgreSQL (Cloud) hybrid database wrapper
├── seed_questions.py       # Seed script with 250+ clean competitive exam questions
├── generate_1000_questions.py # Script to generate and seed 1000+ Current Affairs questions via Gemini
├── requirements.txt        # Backend dependencies
└── vercel.json             # Vercel deployment routes config
```

---

## 💻 Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize & Seed Database**:
   Run the seed script to create the local SQLite database (`study_helper.db`) and pre-populate it with over 160 competitive exam questions:
   ```bash
   python seed_questions.py
   ```

3. **Run the App**:
   Start the Flask development server (runs with adhoc HTTPS for local mobile PWA testing):
   ```bash
   python app.py
   ```
   Open **`https://127.0.0.1:5000`** or your local IP (e.g., `https://192.168.1.XX:5000`) on your mobile/desktop browser.

---

## 🚀 Live Deployment to Vercel

SarkariPrep is configured to run out-of-the-box on Vercel with **Vercel Postgres** database integration.

### Step 1: Create a GitHub Repository
1. Create a new **Private** repository on GitHub (e.g., `study-helper`).
2. Push your local files to the repository:
   ```bash
   git remote add origin YOUR_GITHUB_REPOSITORY_URL
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Vercel
1. Log in to [Vercel](https://vercel.com) and click **Add New** -> **Project**.
2. Import your GitHub repository.
3. Select **Flask** as the framework template and deploy.

### Step 3: Link Vercel Postgres
1. In your project page on Vercel, navigate to the **Storage** tab.
2. Select **Postgres** and click **Create** (choose the free tier).
3. Connect the Postgres database to your project. Vercel will automatically inject the `POSTGRES_URL` environment variables.
4. Redeploy your project so it picks up the environment variables.

### Step 4: Seed the Cloud Database
To seed the cloud Postgres database with questions, run the seed script locally pointing to the cloud database:
1. Copy the **.env.local** connection string from your Vercel project's integration page (or from the environment variables settings as `POSTGRES_URL`).
2. Run the seed script locally with that environment variable:
   ```bash
   # Windows PowerShell:
   $env:POSTGRES_URL="YOUR_VERCEL_POSTGRES_CONNECTION_STRING"
   python seed_questions.py
   ```
   *(This connects to the cloud database and seeds it with all the questions).*

### Step 5: Generate 1,000+ Factual Current Affairs Questions
To expand your database with 1,000+ additional Indian competitive exam Current Affairs questions (factual, preface-free, and updated through 2025/2026):
1. Obtain a free **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).
2. Run the generator script pointing to your database (either local SQLite or Vercel Postgres by setting the appropriate connection environment variable):
   ```bash
   # For Local SQLite:
   $env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
   python generate_1000_questions.py

   # For Cloud Vercel Postgres:
   $env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
   $env:DATABASE_URL="YOUR_VERCEL_POSTGRES_CONNECTION_STRING"
   python generate_1000_questions.py
   ```
   *(This runs 50 batches of 20 questions each across 50 major Current Affairs categories and inserts them directly into the database, respecting API rate limits).*

---

## 📚 Knowledge Management & Documentation (Obsidian Vault)

This project integrates **Obsidian** as its primary developer documentation and knowledge management layer. The entire root repository acts as an Obsidian vault.

### 📁 Vault Directory Structure

* **`/docs`**: General project manuals, API definitions, template files, and change logs.
  * `docs/templates/`: Reusable document skeletons (Feature requests, bug reports, ADRs, etc.).
* **`/architecture`**: System architectural layouts, component structure flowcharts, and database schemas.
* **`/knowledge`**: Deep technical documentation, guidelines, and developer guides.
* **`/meeting-notes`**: Notes from team syncs, sprint planning, and retrospectives.
* **`/prompts`**: AI engineering prompts used by the generator or for developer assistance.
* **`/tasks`**: Interactive sprint task lists.
* **`/.obsidian`**: Config files enabling core templates and pointing to the `docs/templates` directory.

### ⚙️ Automated Documentation Generator

Documentation files are auto-generated directly from the source code by running the `doc_manager.py` script. The script:
1. Parses `app.py` AST to extract all Flask routes, HTTP methods, and handlers.
2. Scans `database.py` parenthesis structures to extract SQLite & Postgres schemas.
3. Map frontend caller actions from `static/js/app.js` to their backend endpoints.
4. Auto-generates `docs/Project Overview.md`, `architecture/Architecture.md`, and `docs/API Documentation.md` with Obsidian internal links (e.g. `[[API Documentation]]`).

#### Commands:
* **Regenerate Documentation**:
  ```bash
  python doc_manager.py
  ```
* **Git-Integrated Changelog (Diff mode)**:
  Scans modified files since the last commit, maps them to impacted documents, and appends a structured summary to `docs/Change Logs.md`:
  ```bash
  python doc_manager.py --git-diff
  ```
* **Install Git Pre-commit Hook**:
  Installs a git pre-commit hook that automatically updates the changelog whenever you commit:
  ```bash
  python doc_manager.py --install-hook
  ```

### 📝 Using Vault Templates in Obsidian

To draft new design decisions or report issues, use the standardized templates in `docs/templates/` inside Obsidian:
1. Open Obsidian and select **Open folder as vault**. Choose this project's root folder.
2. The core **Templates** plugin is auto-enabled and configured via `.obsidian/`.
3. Create a new note, press `Alt + T` (or open command palette and type `Insert template`), and choose from:
   * `Feature Request Template` — To draft user requirements and specifications.
   * `Bug Report Template` — To document defects and reproduction steps.
   * `Technical Decision Template` — Architecture Decision Records (ADRs) to capture tech decisions.
   * `Sprint Notes Template` — To record meeting details and retrospective items.
   * `AI Prompt Template` — For registering and engineering AI instructions.
