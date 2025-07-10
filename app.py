import streamlit as st
import pandas as pd
from gpt_engine import ask_groq
from analyzer import generate_pdf, plot_graph  
from analyzer import generate_insightful_graphs

st.set_page_config(page_title="VesselVision", layout="wide")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None

st.title("🚢 VesselVision — Vessel Performance Chatbot")

# Sidebar for chat topic selection
st.sidebar.header("🗂️ Chat History")

# ➕ Add New Chat Button
if st.sidebar.button("➕ New Chat", key="new_chat"):
    st.session_state.chat_input = ""
    st.session_state.selected_topic = None

chat_topics = [chat['user'][:40] for chat in st.session_state.chat_history]

for i, topic in enumerate(chat_topics):
    if st.sidebar.button(topic, key=f"topic_{i}"):
        st.session_state.selected_topic = i

if st.sidebar.button("🧹 Clear Chat History", key="clear_chat"):
    st.session_state.chat_history = []
    st.session_state.selected_topic = None
    st.success("History cleared")

# File uploader
uploaded_files = st.file_uploader("📤 Upload Noon Report Excel File(s)", type=[".xlsx"], accept_multiple_files=True)

if uploaded_files:
    all_dfs = []
    for file in uploaded_files:
        df = pd.read_excel(file, engine="openpyxl")
        all_dfs.append(df)
    combined_df = pd.concat(all_dfs, ignore_index=True)
    # Handle missing values correctly
    for col in combined_df.columns:
        if combined_df[col].dtype == "object":
            combined_df[col].fillna("", inplace=True)
        elif pd.api.types.is_numeric_dtype(combined_df[col]):
            combined_df[col].fillna(0, inplace=True)

    st.success("✅ Files loaded successfully")
    st.subheader("📋 Uploaded Data Preview")
    st.dataframe(combined_df.head())

    # Tabs for functionality
    tab1, tab2 = st.tabs(["💬 Chatbot", "📊 Graph Generator"])

    with tab1:
        st.subheader("🧠 Ask the AI")
        st.markdown("Type questions like:")
        st.markdown("- Why did fuel increase last week?\n- Suggest RPM improvements\n- What anomalies do you see?")

        # Text input and store in session
        chat_input = st.text_area("Your Question:", value=st.session_state["chat_input"], key="chat_input_key")
        st.session_state["chat_input"] = chat_input

        if st.button("💬 Ask", key="ask_btn"):
            if chat_input.strip():
                with st.spinner("Analyzing..."):
                    try:
                        response = ask_groq(combined_df, chat_input)
                        st.session_state.chat_history.append({"user": chat_input, "bot": response})
                        st.session_state.chat_input = ""
                        st.rerun()
                    except Exception as e:
                        st.error("⚠️ Something went wrong.")
                        st.exception(e)
            else:
                st.warning("Please enter a question.")

        st.markdown("---")
        if st.session_state.selected_topic is not None:
            chat = st.session_state.chat_history[st.session_state.selected_topic]
            st.markdown(f"👨‍💻 **You**: {chat['user']}")
            st.markdown(f"🤖 **Bot**: {chat['bot']}")
        elif st.session_state.chat_history:
            st.subheader("📡 Conversation")
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                st.markdown(f"👨‍💻 **You**: {chat['user']}")
                st.markdown(f"🤖 **Bot**: {chat['bot']}")
                st.markdown("---")

        # PDF Export of last response
        if st.session_state.chat_history:
            try:
                last_response = st.session_state.chat_history[-1]['bot']
                generate_pdf(last_response)
                with open("summary.pdf", "rb") as f:
                    st.download_button(
                        label="⬇️ Download Summary as PDF",
                        data=f,
                        file_name="summary.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error("❌ Failed to generate or load the PDF.")
                st.exception(e)

    with tab2:
        st.subheader("📈 Custom Graph Generator")
        st.markdown("Select any two columns to generate a graph from the uploaded noon reports.")

        col_options = combined_df.columns.tolist()
        x_axis = st.selectbox("📌 Select X-axis", col_options)
        y_axis = st.selectbox("📍 Select Y-axis", col_options)
        chart_type = st.selectbox("📊 Chart Type", ["Line", "Bar", "Scatter"])

        if st.button("🔍 Generate Chart"):
            try:
                plot_graph(combined_df, x_axis, y_axis, chart_type)
            except Exception as e:
                st.error("Graph generation failed.")
                st.exception(e)
                
else:
    st.markdown("---")
    st.warning("📂 Please upload one or more Excel noon report files to start.")
