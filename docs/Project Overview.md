# Project Overview

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

Generated at: 2026-06-21 21:35:17
