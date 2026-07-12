import streamlit as st
import plotly.express as px
import pandas as pd
from email_generator import generate_email
st.set_page_config(
    page_title="SmartMail AI",
    page_icon="📧",
    layout="wide"
)


# ==========================================
# Sidebar
# ==========================================

st.sidebar.title("📧 SmartMail AI")
st.sidebar.markdown("---")

st.sidebar.header("ℹ️ About")

st.sidebar.write("""
SmartMail AI is an AI-powered email assistant built using:

- Python
- Streamlit
- Plotly
- Pandas

Features:

✅ Generate Emails

✅ Search History

✅ Analytics Dashboard

✅ Export CSV
""")

page = st.sidebar.radio(
    "Navigation",
    [
        "Generate Email",
        "Email History",
        "Analytics"
    ]
)


# ==========================================
# Generate Email Page
# ==========================================

if page == "Generate Email":

    st.title("📧 SmartMail AI")
    st.subheader("AI-Powered Email Assistant")

    email_type = st.selectbox(
        "Select Email Type",
        [
            "job_application",
            "follow_up",
            "meeting_request",
            "leave_request",
            "apology"
        ]
    )

    purpose = st.text_input("Purpose of the Email")

    context = st.text_area("Context / Details")

    tone = st.selectbox(
        "Select Tone",
        [
            "formal",
            "semi-formal",
            "casual"
        ]
    )

    generate = st.button("Generate Email")

    if generate:

        email = generate_email(
            email_type,
            purpose,
            context,
            tone
        )

        with open("email_history.txt", "a", encoding="utf-8") as f:
            f.write(email)
            f.write("\n")
            f.write("=" * 50)
            f.write("\n\n")

        st.success("Email saved to history!")
        st.success("Email Generated Successfully!")

        st.subheader("Generated Email")

        st.text_area(
            "Output",
            email,
            height=300,
            key="generated_email"
        )

        st.download_button(
            "📥 Download Email",
            email,
            file_name="generated_email.txt",
            mime="text/plain"
        )


# ==========================================
# Email History Page
# ==========================================

elif page == "Email History":

    st.header("📜 Email History")

    search = st.text_input("🔍 Search Previous Emails")

    try:
        with open("email_history.txt", "r", encoding="utf-8") as f:
            history = f.read()

    except FileNotFoundError:
        history = ""

    emails = history.split("=" * 50)
    emails = [email.strip() for email in emails if email.strip()]

    df = pd.DataFrame({
        "Email": emails
    })

    if search:

        matching = []

        for email in emails:
            if search.lower() in email.lower():
                matching.append(email)

        if matching:

            st.success(f"Found {len(matching)} matching email(s)!")

            for i, email in enumerate(matching, start=1):

                st.text_area(
                    f"Result {i}",
                    email,
                    height=250,
                    key=f"result_{i}"
                )

        else:

            st.error("No matching emails found.")

    st.subheader("Previous Emails")

    st.text_area(
        "History",
        history,
        height=350,
        key="history"
    )

    csv = df.to_csv(index=False)

    st.download_button(
        label="📥 Download Email History (CSV)",
        data=csv,
        file_name="email_history.csv",
        mime="text/csv"
    )


# ==========================================
# Analytics Page
# ==========================================

elif page == "Analytics":

    st.header("📊 Email Analytics")

    try:
        with open("email_history.txt", "r", encoding="utf-8") as f:
            history = f.read()

    except FileNotFoundError:
        history = ""

    import os

    st.write("📂 Current Folder:", os.getcwd())
    st.write("📄 History File:", os.path.abspath("email_history.txt"))

    # Split history into individual emails
    emails = history.split("=" * 50)
    emails = [email.strip() for email in emails if email.strip()]

    total = len(emails)

    job = 0
    follow = 0
    leave = 0
    meeting = 0
    apology = 0

    for email in emails:

        text = email.lower()

        if "job_application" in text:
            job += 1

        elif "follow_up" in text:
            follow += 1

        elif "leave_request" in text:
            leave += 1

        elif "meeting_request" in text:
            meeting += 1

        elif "apology" in text:
            apology += 1

    data = {
        "Email Type": [
            "Job",
            "Follow Up",
            "Leave",
            "Meeting",
            "Apology"
        ],
        "Count": [
            job,
            follow,
            leave,
            meeting,
            apology
        ]
    }

    fig = px.bar(
        data,
        x="Email Type",
        y="Count",
        color="Email Type",
        title="SmartMail AI - Email Analytics"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("📧 Total", total)
    col2.metric("💼 Jobs", job)
    col3.metric("🔄 Follow Up", follow)

    col4, col5, col6 = st.columns(3)

    col4.metric("🏥 Leave", leave)
    col5.metric("🤝 Meetings", meeting)
    col6.metric("🙏 Apologies", apology)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("---")

    st.caption(
        "🚀 SmartMail AI | Built by Sumanth Kotian using Python, Streamlit & Plotly"
    )