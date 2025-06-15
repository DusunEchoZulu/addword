# Dusun-English Dictionary Admin Tool (AddWord)

This project is a **Streamlit-based web app** that allows you to add and manage entries in a Dusun–English dictionary stored in **Google Sheets**.

---

## 🔍 Features

- Check if a Dusun word or phrase already exists
- View existing English translations (with word types)
- Add new Dusun words or phrases with English meanings
- Choose from common word types (e.g., noun, verb, adj)
- All data is saved directly to a connected Google Sheet

---

## 📂 Project Structure

| File | Description |
|------|-------------|
| `add_word_app.py` | Main Streamlit app |
| `requirements.txt` | Python packages needed for deployment |
| `credentials.json` | Google API credentials (not included for security) |

---

## ⚙️ Requirements

Before running the app locally or deploying to Streamlit Cloud, install the required packages:

```bash
pip install -r requirements.txt
