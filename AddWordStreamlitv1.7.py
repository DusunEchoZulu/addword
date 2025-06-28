# AddWord Streamlit App v1.7 – Simplified Flow

import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

# ========== Configuration ==========
GSHEET_NAME = "DTP_EN Dictionary"
SHEET_NAME = "DTP-EN WORDS"
CREDENTIALS_FILE = "credentials.json"
# ===================================

@st.cache_resource
def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    return client.open(GSHEET_NAME).worksheet(SHEET_NAME)

@st.cache_data(ttl=60)
def load_data(_sheet):
    df = get_as_dataframe(_sheet).dropna(how="all")
    df.columns = [col.strip().capitalize() for col in df.columns]
    return df

def save_data(sheet, df):
    sheet.clear()
    set_with_dataframe(sheet, df)

# ========== UI Starts Here ==========
st.markdown("<h4>📚 Add Word to DTP_EN Dictionary v1.7</h4>", unsafe_allow_html=True)


sheet = connect_sheet()
df = load_data(sheet)
st.markdown(f"**Total entries:** {len(df)}")

# --- Step 1: Dusun input ---
dusun_input = st.text_input("Enter Dusun word or phrase:")

if dusun_input:
    cleaned = dusun_input.strip().lower()
    matches = df[df["Dusun"].str.strip().str.lower() == cleaned]

    if not matches.empty:
        st.warning("🚫 Already exists:")
        for _, row in matches.iterrows():
            eng = str(row["English"]).strip()
            wtype = str(row.get("Type", "")).strip()
            st.markdown(f"- **{eng}** ({wtype})")
    else:
        st.success("✅ Not found. You may add it below.")

        # --- Step 2: Input English + Type ---
        with st.form("add_word_form"):
            english_input = st.text_input("English translation:")
            word_types = ["", "verb", "noun", "adj", "adv", "pron", "prep", "conj", "intj", "imper", "det"]
            selected_type = st.selectbox("Select word type:", word_types, format_func=lambda x: x if x else "(skip)")

            submitted = st.form_submit_button("Add to Dictionary")

            if submitted:
                if not english_input:
                    st.error("English translation is required.")
                else:
                    df.loc[len(df.index)] = [dusun_input.strip(), english_input.strip(), selected_type.strip()]
                    save_data(sheet, df)
                    st.success("✅ Entry added successfully!")
                    st.rerun()
