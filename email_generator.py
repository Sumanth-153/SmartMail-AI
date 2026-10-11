import streamlit as st
from google import genai


def generate_email(email_type, purpose, context, tone):
    """Generate a personalized email using Google's Gemini API."""

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)

        prompt = f"""
You are a professional email-writing assistant.

Write a complete, polished, natural-sounding email based on the details below.

Email type: {email_type}
Purpose: {purpose}
Additional context: {context}
Preferred tone: {tone}

Requirements:
- Create a relevant subject line.
- Start with "Subject:" exactly. Never put a hyphen, dash, or bullet before it.
- Use an appropriate greeting and closing.
- Incorporate the supplied details naturally.
- Do not merely repeat the user's input.
- Do not invent facts that were not provided.
- Return only the completed email.
"""

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )

        if not response.text:
            return "Gemini returned an empty response. Please try again."

        return response.text.strip()

    except Exception as e:
        return f"Email generation failed: {e}"
