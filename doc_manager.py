#!/usr/bin/env python3
import os
import sys
import re
import ast
import subprocess
from datetime import datetime

# Define target directories for Obsidian vault
DIRS = ["docs", "knowledge", "architecture", "meeting-notes", "prompts", "tasks"]

# Define template directories
TEMPLATES_DIR = os.path.join("docs", "templates")

def ensure_directories():
    """Ensure all Obsidian vault folders and templates directory exist."""
    for d in DIRS:
        os.makedirs(d, exist_ok=True)
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    os.makedirs(".obsidian", exist_ok=True)

def parse_flask_routes(app_file="app.py"):
    """Parse Flask app.py using AST to find all endpoints and routes details."""
    if not os.path.exists(app_file):
        print(f"Warning: {app_file} not found. Skipping route analysis.")
        return []

    try:
        with open(app_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception as e:
        print(f"Error parsing {app_file} AST: {e}")
        return []

    routes = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        
        for decorator in node.decorator_list:
            # Check for decorator like @app.route(...)
            is_route = False
            route_path = ""
            methods = ["GET"]

            # Handle simple decorator @app.route(...)
            if (isinstance(decorator, ast.Call) and 
                isinstance(decorator.func, ast.Attribute) and 
                decorator.func.attr == "route"):
                is_route = True
                
                # Extract path (first argument)
                if decorator.args:
                    if isinstance(decorator.args[0], ast.Constant):
                        route_path = decorator.args[0].value
                
                # Extract methods kwarg
                for kw in decorator.keywords:
                    if kw.arg == "methods":
                        if isinstance(kw.value, ast.List):
                            methods = [el.value for el in kw.value.elts if isinstance(el, ast.Constant)]

            if is_route:
                docstring = ast.get_docstring(node) or "No description provided."
                routes.append({
                    "path": route_path,
                    "methods": methods,
                    "func_name": node.name,
                    "docstring": docstring.strip()
                })
    return routes

def parse_database_schema(db_file="database.py"):
    """Parse database.py to discover tables and fields by matching parenthesis blocks."""
    if not os.path.exists(db_file):
        print(f"Warning: {db_file} not found. Skipping database analysis.")
        return {}

    try:
        with open(db_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {db_file}: {e}")
        return {}

    tables = {}
    # Find all table declarations starting with "CREATE TABLE IF NOT EXISTS [table_name] ("
    pattern = re.compile(r"CREATE TABLE IF NOT EXISTS\s+(\w+)\s*\(", re.IGNORECASE)
    for match in pattern.finditer(content):
        table_name = match.group(1).lower().strip()
        start_idx = match.end() - 1 # starts at the '('
        
        # Count parentheses to locate matching closing parenthesis
        depth = 0
        end_idx = start_idx
        for i in range(start_idx, len(content)):
            if content[i] == '(':
                depth += 1
            elif content[i] == ')':
                depth -= 1
                if depth == 0:
                    end_idx = i
                    break
        
        if end_idx == start_idx:
            continue
            
        columns_str = content[start_idx+1:end_idx]
        
        columns = []
        for line in columns_str.split('\n'):
            line = line.strip()
            # Skip empty lines, system keys and indices
            if not line or line.startswith('FOREIGN KEY') or line.startswith('UNIQUE') or line.startswith('REFERENCES'):
                continue
            
            # Remove trailing commas if present
            if line.endswith(','):
                line = line[:-1].strip()
                
            parts = line.split(None, 1)
            if len(parts) >= 2:
                col_name = parts[0]
                col_def = parts[1]
                columns.append({
                    "name": col_name,
                    "type": col_def
                })
        
        # Keep first schema definition found (usually PostgreSQL is first, but keep unique entries)
        if table_name not in tables:
            tables[table_name] = columns
        
    return tables

def parse_frontend_api_calls(js_file=os.path.join("static", "js", "app.js")):
    """Scan javascript for frontend fetch calls."""
    if not os.path.exists(js_file):
        print(f"Warning: {js_file} not found. Skipping frontend api scan.")
        return {}

    try:
        with open(js_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {js_file}: {e}")
        return {}

    # Find API endpoints matched in code
    # Find patterns like '/api/auth/me', '/api/quiz/question', etc.
    api_patterns = re.findall(r"['\"](/api/[a-zA-Z0-9_\-\/]+)['\"?]", content)
    
    # Map backend path to potential frontend usage
    # We will check where these fetches are used
    endpoint_usage = {}
    for endpoint in set(api_patterns):
        # Find functions calling this endpoint
        # Let's do a simple regex search to see what function wraps it
        # We find functions above the fetch block
        usage_functions = []
        for block in content.split("function "):
            if endpoint in block:
                func_header = block.split("(")[0].strip()
                if func_header and " " not in func_header:
                    usage_functions.append(func_header)
        
        endpoint_usage[endpoint] = usage_functions
        
    return endpoint_usage

def generate_project_overview():
    """Generate docs/Project Overview.md."""
    overview_path = os.path.join("docs", "Project Overview.md")
    content = f"""# Project Overview

Welcome to the **SarkariPrep** developer knowledge base and Obsidian vault!

SarkariPrep is a mobile-first, installable Progressive Web App (PWA) designed to assist students preparing for Indian government competitive exams (UPSC, SSC, Banking, Railways, State PSC, and General Knowledge). 

---

## 📂 Vault Hub

Explore the documentation sections using these links:
* **Architecture**: [[Architecture]] — System design, components, database schemas, and codebase overview.
* **API Documentation**: [[API Documentation]] — Full backend Flask serverless endpoints mapped to frontend callers.
* **Change Logs**: [[Change Logs]] — Auto-updated log tracking codebase modifications, ADR decisions, and commits.
* **Knowledge**: [[knowledge/Developer Guide]] — Local environment setup, deployment scripts, and developer instructions.
* **Meeting Notes**: [[meeting-notes/Sprint Notes]] — Planning sessions, retrospectives, and sprint logs.
* **Tasks**: [[tasks/Project Tasks]] — Backlog items, task tracking, and milestone lists.
* **Prompts**: [[prompts/AI Prompts]] — Reusable AI instructions and prompts.

---

## 🏗️ Folder Structure

* **`/docs`**: General project manuals, API definitions, change tracking logs, and Markdown document templates.
* **`/architecture`**: System architectural layouts, component structures, and database schemas.
* **`/knowledge`**: Deep technical resources, references, and setup tutorials.
* **`/meeting-notes`**: Notes from team syncs and sprint retrospectives.
* **`/prompts`**: AI helper instructions and operational templates.
* **`/tasks`**: Interactive task lists.

---

## 🚀 Running the Doc Sync Manager

You can update this documentation vault automatically from the code using:
```bash
python doc_manager.py
```
To check files modified since last commit and write them to the change log:
```bash
python doc_manager.py --git-diff
```

Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    with open(overview_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {overview_path}")

def generate_architecture_doc(tables):
    """Generate architecture/Architecture.md."""
    arch_path = os.path.join("architecture", "Architecture.md")
    
    schema_markdown = ""
    for t_name, columns in tables.items():
        schema_markdown += f"### Table: `{t_name}`\n\n"
        schema_markdown += "| Column | Type / Constraints |\n"
        schema_markdown += "| --- | --- |\n"
        for col in columns:
            schema_markdown += f"| `{col['name']}` | `{col['type']}` |\n"
        schema_markdown += "\n"

    content = f"""# System Architecture

This document describes the high-level system architecture and database design of SarkariPrep.

For interface definitions, see [[API Documentation]].

---

## 📊 Component Diagram

```mermaid
graph TD
    Client[Mobile/Desktop Browser] <-->|PWA Manifest / Service Worker| SW[static/sw.js Cache]
    Client <-->|HTTPS API / SPA Client| Frontend[static/js/app.js]
    Frontend <-->|JSON Requests| Backend[app.py - Flask Backend]
    Backend <-->|SQL Queries| DB[(Database Layer)]
    
    subgraph DB Layer
        DB --- SQLite[study_helper.db - Local SQLite]
        DB --- Postgres[Postgres - Production Cloud Vercel]
    end
```

---

## 📁 Codebase Layout

* **[[app.py]]**: Standard Flask backend routing. Binds session authentication, quiz serving logic, answer validations, and bookmarking. Bypasses SSL with adhoc context for local PWA setup.
* **[[database.py]]**: Connection manager layer supporting SQLite for offline local dev and PostgreSQL for production deployments.
* **[[seed_questions.py]]**: Generates database tables and inserts mock questions.
* **[[generate_1000_questions.py]]**: Automated ingestion tool querying Gemini 2.5 Flash for Current Affairs questions.

---

## 💾 Database Schema

The database supports hybrid structures (SQLite/PostgreSQL mappings). Below are the documented table schemas:

{schema_markdown}

---

## 🔗 Related Documents
* [[Project Overview]]
* [[API Documentation]]
* [[Change Logs]]

Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    with open(arch_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {arch_path}")

def generate_api_doc(routes, js_usage):
    """Generate docs/API Documentation.md."""
    api_path = os.path.join("docs", "API Documentation.md")
    
    routes_markdown = ""
    for r in routes:
        methods_str = ", ".join(r["methods"])
        frontend_callers = js_usage.get(r["path"], [])
        frontend_callers_str = ", ".join([f"`{c}()`" for c in frontend_callers]) if frontend_callers else "*None directly detected*"
        
        routes_markdown += f"### `{r['path']}`\n"
        routes_markdown += f"* **HTTP Methods**: `{methods_str}`\n"
        routes_markdown += f"* **Backend Handler**: `{r['func_name']}()` in [[app.py]]\n"
        routes_markdown += f"* **Frontend Caller**: {frontend_callers_str}\n"
        routes_markdown += f"* **Description**: \n"
        routes_markdown += f"  > {r['docstring'].replace(chr(10), chr(10) + '  > ')}\n\n"
        routes_markdown += "---\n\n"

    content = f"""# API Documentation

This file documents the application API endpoints and routes exposed by the backend, mapped to frontend call locations.

For database tables and backend source descriptions, see [[Architecture]].

---

## 🔌 API Endpoints Mapped

{routes_markdown}

## 🔗 Related Documents
* [[Project Overview]]
* [[Architecture]]

Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    with open(api_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {api_path}")

def check_git_diff():
    """Identify files changed since last git commit."""
    try:
        res = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        if res.returncode != 0:
            # Fallback to general status
            res = subprocess.run(
                ["git", "status", "--porcelain"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            files = [line.strip().split()[-1] for line in res.stdout.strip().split("\n") if line.strip()]
            return files
        return res.stdout.strip().split("\n")
    except Exception as e:
        print(f"Warning: git command execution failed ({e}). Unable to run automatic diff updates.")
        return []

def update_changelog():
    """Update docs/Change Logs.md based on git modifications."""
    changelog_path = os.path.join("docs", "Change Logs.md")
    
    modified_files = check_git_diff()
    # Filter empty strings
    modified_files = [f for f in modified_files if f]
    
    if not modified_files:
        print("No file changes detected since last commit. Change log update skipped.")
        return

    # Check if changelog exists
    exists = os.path.exists(changelog_path)
    
    log_content = ""
    if not exists:
        log_content += f"""# Change Logs

This page records project updates, refactors, and feature additions.

---

"""

    # Format the new entry
    new_entry = f"## 🗓️ Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    new_entry += "### 📁 Modified Code Files:\n"
    for f in modified_files:
        new_entry += f"* `{f}` -> Impacted documentation: "
        if f == "app.py" or f.startswith("static/js/"):
            new_entry += "[[API Documentation]]"
        elif f == "database.py" or f == "seed_questions.py":
            new_entry += "[[Architecture]]"
        else:
            new_entry += "[[Project Overview]]"
        new_entry += "\n"
        
    new_entry += "\n### 📝 Developer Implementation Notes:\n"
    new_entry += "> *[Describe decision outcome, refactors, or fixes here. Link related templates like [[Technical Decision Template|ADR]] if created]*\n\n"
    new_entry += "---\n\n"

    if exists:
        with open(changelog_path, "r", encoding="utf-8") as f:
            old_data = f.read()
        
        # Insert new entry right after header
        header_split = old_data.split("# Change Logs\n\n")
        if len(header_split) > 1:
            full_content = "# Change Logs\n\n" + new_entry + header_split[1]
        else:
            full_content = old_data + "\n\n" + new_entry
    else:
        full_content = log_content + new_entry
        
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(full_content)
    print(f"Updated {changelog_path}")

def generate_initial_tasks():
    """Create a default tasks file if empty."""
    task_path = os.path.join("tasks", "Project Tasks.md")
    if os.path.exists(task_path):
        return

    content = """# Project Task List

Use this list to organize project backlog items. Mark them inside Obsidian with `- [ ]` or `- [x]`.

---

## 🏃 Active Sprint Tasks
- [x] Integrate Obsidian vault workspace hierarchy
- [x] Create standardized templates in `docs/templates/`
- [ ] Configure service worker caching for offline testing
- [ ] Fix questions view rendering bug in mobile layout
- [ ] Verify database connection settings under production environment variables

## 📋 General Backlog
- [ ] Implement quiz timer component (60 seconds per question)
- [ ] Support category-wise custom filters on history panel
- [ ] Add dark-theme settings toggle to frontend
- [ ] Integrate user authentication statistics charts using Chart.js

---
## 🔗 Links
* [[Project Overview]]
* [[docs/templates/Sprint Notes Template|Sprint Note template]]
"""
    with open(task_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {task_path}")

def generate_developer_guide():
    """Generate knowledge/Developer Guide.md."""
    guide_path = os.path.join("knowledge", "Developer Guide.md")
    content = f"""# Developer Guide

This guide is designed to help you set up, develop, and deploy the SarkariPrep application.

---

## ⚙️ Local Development Requirements

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Seed the database**:
   ```bash
   python seed_questions.py
   ```
3. **Run application server**:
   ```bash
   python app.py
   ```

---

## 📁 Document Templates

The vault comes with built-in document templates located in `docs/templates/`. You can trigger these templates inside Obsidian using the **Templates** core plugin:
* **[[docs/templates/Feature Request Template|Feature Request Template]]**
* **[[docs/templates/Bug Report Template|Bug Report Template]]**
* **[[docs/templates/Technical Decision Template|Technical Decision Template (ADR)]]**
* **[[docs/templates/Sprint Notes Template|Sprint Notes Template]]**
* **[[docs/templates/AI Prompt Template|AI Prompt Template]]**

---

## 🔗 Links
* [[Project Overview]]
* [[Architecture]]
* [[API Documentation]]
"""
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {guide_path}")

def generate_prompts_index():
    """Generate prompts/AI Prompts.md."""
    prompts_path = os.path.join("prompts", "AI Prompts.md")
    content = f"""# AI Prompts

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
"""
    with open(prompts_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {prompts_path}")

def install_pre_commit_hook():
    """Install this script as a git pre-commit hook."""
    git_dir = os.path.join(".git", "hooks")
    if not os.path.exists(git_dir):
        print("Error: .git directory not found. Are you in a git repository?")
        return False
        
    hook_path = os.path.join(git_dir, "pre-commit")
    
    hook_script = """#!/bin/sh
# Auto-generated pre-commit hook for doc_manager.py
echo "Running Obsidian doc generator check..."
python doc_manager.py --git-diff
"""
    try:
        with open(hook_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(hook_script)
        
        # Make the hook executable (Unix-style, though on Windows Git Bash respects it)
        if sys.platform != "win32":
            subprocess.run(["chmod", "+x", hook_path])
        print(f"Successfully installed Git pre-commit hook at {hook_path}")
        return True
    except Exception as e:
        print(f"Failed to write pre-commit hook: {e}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Manage Obsidian-compatible workspace documentation.")
    parser.add_argument("--git-diff", action="store_true", help="Capture git changes and append log to Change Logs.md")
    parser.add_argument("--install-hook", action="store_true", help="Install git pre-commit hook to automate execution")
    args = parser.parse_args()

    print("Checking Obsidian documentation vault components...")
    ensure_directories()

    if args.install_hook:
        install_pre_commit_hook()
        return

    # Parse project files
    routes = parse_flask_routes()
    db_schema = parse_database_schema()
    frontend_api = parse_frontend_api_calls()

    # Generate documents
    generate_project_overview()
    generate_architecture_doc(db_schema)
    generate_api_doc(routes, frontend_api)
    generate_initial_tasks()
    generate_developer_guide()
    generate_prompts_index()

    # Update change logs if requested or if there are modified files since last run
    if args.git_diff:
        update_changelog()
    else:
        # Check anyway, but let's notify
        print("Run with '--git-diff' to generate active code changes into docs/Change Logs.md")

    print("Obsidian workspace updates completed successfully!")

if __name__ == "__main__":
    main()
