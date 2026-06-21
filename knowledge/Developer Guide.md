# Developer Guide

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
