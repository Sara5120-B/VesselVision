# gpt_engine.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask_groq(df, user_query):
    if df.empty:
        return "⚠️ No data found in the uploaded noon reports."

    # Convert DataFrame to string
    try:
        context = df.fillna("").astype(str).head(10).to_string(index=False)
    except:
        context = str(df)

    # Build prompt
    prompt = f"""
You are a marine performance analyst AI.

Use the following noon report data to answer the user's query. Highlight trends, anomalies, and suggest improvements.

--- NOON REPORT DATA ---
{context[:4000]}  # only include first 4000 characters for token safety
------------------------

QUERY: {user_query}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful vessel performance AI assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    # Send request to Groq
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )

    # Handle response
    try:
        response_json = response.json()
        print("🟢 Groq Response:", response_json)
        return response_json["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ Groq Error:", response.status_code, response.text)
        return f"Error: Could not get response from Groq.\n\n{response.text}"
