# AddWord Streamlit App v1.6 – Check Exact Dusun + English Match

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

# --- Clear input fields if "?clear=1" is in URL ---
if st.query_params.get("clear") == "1":
    st.query_params.clear()
    st.session_state["dusun_input"] = ""
    st.session_state["english_input"] = ""
    st.session_state["selected_type"] = ""

# --- Session state defaults ---
st.session_state.setdefault("dusun_input", "")
st.session_state.setdefault("english_input", "")
st.session_state.setdefault("selected_type", "")

# ========== Functions ==========
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
st.title("📚 Add Word to DTP_EN Dictionary")

sheet = connect_sheet()
df = load_data(sheet)

st.markdown(f"**Total entries:** {len(df)}")

# --------- Check if Phrase Exists ---------
with st.expander("🔍 Check if Dusun word/phrase exists:"):
    check_phrase = st.text_input("Enter Dusun word or phrase to check:")
    if check_phrase:
        matches = df[df["Dusun"].str.strip().str.lower() == check_phrase.strip().lower()]
        if not matches.empty:
            st.warning("This Dusun word already exists with the following translations:")
            for _, row in matches.iterrows():
                eng = str(row["English"]).strip()
                wtype = str(row.get("Type", "")).strip()
                st.markdown(f"- **{eng}** ({wtype})")
        else:
            st.success("✅ Phrase not found. You can now add it below.")
            st.session_state["dusun_input"] = check_phrase.strip()

# --------- Add Word Form ---------
with st.form("add_word_form"):
    dusun_input = st.text_input("Dusun word or phrase:", value=st.session_state["dusun_input"], key="dusun_input")
    english_input = st.text_input("English translation:", value=st.session_state["english_input"], key="english_input")

    word_types = ["", "verb", "noun", "adj", "adv", "pron", "prep", "conj", "intj", "imper", "det"]
    selected_type = st.selectbox("Select word type:", word_types, index=0, format_func=lambda x: x if x else "(skip)", key="selected_type")

    submitted = st.form_submit_button("➕ Add to Dictionary")
    if submitted:
        if not dusun_input or not english_input:
            st.error("Both Dusun and English fields are required.")
        else:
            dusun_clean = dusun_input.strip().lower()
            english_clean = english_input.strip().lower()
            exists = df[
                (df["Dusun"].str.strip().str.lower() == dusun_clean) &
                (df["English"].str.strip().str.lower() == english_clean)
            ]

            if not exists.empty:
                st.error("🚫 This Dusun–English pair already exists in the dictionary.")
            else:
                df.loc[len(df.index)] = [dusun_input.strip(), english_input.strip(), selected_type.strip()]
                save_data(sheet, df)
                st.success("✅ Entry added successfully!")

                # Clear inputs via redirect
                st.query_params["clear"] = "1"
                st.rerun()
