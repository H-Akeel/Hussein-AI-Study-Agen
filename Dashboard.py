import streamlit as st
import pandas as pd
import re
import os

st.set_page_config(page_title="Hussein AI Study Center", layout="wide")
st.title("🚀 Hussein AI Study Analysis Center")

def parse_logs(file_path):
    if not os.path.exists(file_path): return None
    with open(file_path, "r", encoding="utf-8") as f: content = f.read()
    blocks = content.split('============================================================')
    data = []
    for block in blocks:
        if "TIME:" in block:
            time_m = re.search(r"TIME:\s*(.*)", block)
            ans_m = re.search(r"AI ANSWER:\s*(.*?)\n\nREASONING:", block, re.DOTALL)
            logic_m = re.search(r"REASONING:\s*(.*?)\n", block, re.DOTALL)
            data.append({
                "Timestamp": time_m.group(1).strip() if time_m else "N/A",
                "Answer": ans_m.group(1).strip() if ans_m else "N/A",
                "Reasoning": logic_m.group(1).strip() if logic_m else "N/A"
            })
    return pd.DataFrame(data)

df = parse_logs("ai_study_logs.txt")
if df is not None and not df.empty:
    st.metric("Total Questions Solved", len(df))
    st.dataframe(df, width='stretch') # Fixed for 2026 update
    st.subheader("💡 Logic Review")
    idx = st.selectbox("Select Record:", df.index)
    st.success(f"Answer: {df.iloc[idx]['Answer']}")
    st.info(f"Reasoning: {df.iloc[idx]['Reasoning']}")
else:
    st.warning("No logs found. Run the Sniper tool first!")

if st.button("🔄 Refresh"): st.rerun()