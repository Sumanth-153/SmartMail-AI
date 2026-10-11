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
        ["formal", "semi-formal", "casual"]
    )

    generate = st.button("Generate Email")

    if generate:

        if not purpose.strip():
            st.warning("Please enter the purpose of your email.")

        else:
            email = generate_email(
                email_type,
                purpose,
                context,
                tone
            )

            # Do not save failed API responses as generated emails
            if email.startswith("Email generation failed:"):
                st.error(email)

            else:
                # Save the email type along with the generated email
                with open("email_history.txt", "a", encoding="utf-8") as f:
                    f.write(f"Email Type: {email_type}\n")
                    f.write(email)
                    f.write("\n")
                    f.write("=" * 50)
                    f.write("\n\n")

                st.success("Email saved to history!")
                st.success("Email generated successfully!")

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

    emails = [
    email.strip()
    for email in emails
    if email.strip()
    and not email.strip().lower().startswith(
        "email generation failed:"
    )
]


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
    import os
    import re

    st.header("📊 Email Analytics")

    history_file = "email_history.txt"

    try:
        with open(history_file, "r", encoding="utf-8") as f:
            history = f.read()
    except FileNotFoundError:
        history = ""

    st.write("📂 Current Folder:", os.getcwd())
    st.write("📄 History File:", os.path.abspath(history_file))

    # Split history into individual email records
    records = [
        record.strip()
        for record in history.split("=" * 50)
        if record.strip()
    ]

    # Exclude failed API responses
    emails = [
        record for record in records
        if not record.lower().startswith("email generation failed:")
    ]

    categories = {
        "Job": 0,
        "Follow Up": 0,
        "Leave": 0,
        "Meeting": 0,
        "Apology": 0,
        "Other / Unclassified": 0
    }

    category_map = {
        "job_application": "Job",
        "follow_up": "Follow Up",
        "leave_request": "Leave",
        "meeting_request": "Meeting",
        "apology": "Apology"
    }

    # Classify each email exactly once
    for email in emails:
        category = None

        # First, check saved email-type metadata
        match = re.search(
            r"email type:\s*([a-z_]+)",
            email,
            re.IGNORECASE
        )

        if match:
            category = category_map.get(match.group(1).lower())

        # For older emails without metadata, inspect the subject
        if category is None:
            subject_match = re.search(
                r"subject:\s*(.+)",
                email,
                re.IGNORECASE
            )

            subject = (
                subject_match.group(1).strip().lower()
                if subject_match
                else ""
            )

            if any(word in subject for word in [
                "job application", "application for",
                "applying for a job"
            ]):
                category = "Job"

            elif any(word in subject for word in [
                "follow up", "follow-up", "following up"
            ]):
                category = "Follow Up"

            elif any(word in subject for word in [
                "leave", "time off", "absence"
            ]):
                category = "Leave"

            elif any(word in subject for word in [
                "meeting", "schedule a call"
            ]):
                category = "Meeting"

            elif any(word in subject for word in [
                "apology", "apologize", "apologise", "sorry"
            ]):
                category = "Apology"

        # Every email contributes to exactly one category
        if category is None:
            category = "Other / Unclassified"

        categories[category] += 1

    # Use one source of truth for both metrics and chart
    total = len(emails)

    col1, col2, col3 = st.columns(3)

    col1.metric("📧 Total Emails", total)
    col2.metric("💼 Jobs", categories["Job"])
    col3.metric("🔄 Follow Ups", categories["Follow Up"])

    col4, col5, col6 = st.columns(3)

    col4.metric("🏥 Leave", categories["Leave"])
    col5.metric("🤝 Meetings", categories["Meeting"])
    col6.metric("🙏 Apologies", categories["Apology"])

    st.metric(
        "📂 Other / Unclassified",
        categories["Other / Unclassified"]
    )

    # Build the chart from the exact same category counts
    data = pd.DataFrame({
        "Email Type": list(categories.keys()),
        "Count": list(categories.values())
    })

    fig = px.bar(
        data,
        x="Email Type",
        y="Count",
        color="Email Type",
        title="SmartMail AI - Email Analytics",
        text="Count"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Verify that every email is accounted for
    category_total = sum(categories.values())

    if category_total == total:
        st.success(
            f"Verified: {category_total} emails accounted for "
            "across all categories."
        )
    else:
        st.error(
            f"Count mismatch: total={total}, "
            f"categories={category_total}"
        )

    st.markdown("---")
    st.caption(
        "🚀 SmartMail AI | Built by Sumanth Kotian "
        "using Python, Streamlit & Plotly"
    )
