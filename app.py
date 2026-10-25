import streamlit as st
import plotly.express as px
import pandas as pd
from supabase import create_client
from email_generator import generate_email
st.set_page_config(

    page_title="SmartMail AI",
    page_icon="📧",
    layout="wide"
)

# Supabase connection
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_PUBLISHABLE_KEY"]
)


# Authentication state
if "user" not in st.session_state:
    st.session_state.user = None

if "access_token" not in st.session_state:
    st.session_state.access_token = None


# Login and Signup Interface
if st.session_state.user is None:
    left_space, center_form, right_space = st.columns([1, 2, 1])

    with center_form:
        st.title("📧 SmartMail AI")
        st.subheader("Welcome! Please log in or create an account.")

        auth_mode = st.radio(
            "Choose an option",
            ["Login", "Sign Up"],
            horizontal=True,
            key="auth_mode"
        )

        email = st.text_input("Email address", key="auth_email")

        password = st.text_input(
            "Password",
            type="password",
            key="auth_password"
        )

        confirm_password = ""
        if auth_mode == "Sign Up":
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                key="auth_confirm_password"
            )

        if auth_mode == "Sign Up":
            if st.button("Create Account", type="primary"):
                email = email.strip()

                if not email or not password:
                    st.error("Enter your email address and password.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    try:
                        result = supabase.auth.sign_up({
                            "email": email,
                            "password": password,
                            "options": {
                                "email_redirect_to": (
                                    "https://smartmail-ai-sumanth.streamlit.app"
                                )
                            }
                        })

                        if result.user:
                            st.success(
                                "Account created. Check your email "
                                "to confirm your account before logging in."
                            )
                        else:
                            st.error("Signup could not be completed.")

                    except Exception as e:
                        st.error(
                            "Sorry, we couldn't create your account."
                        )
                        st.caption(f"Debug details: {e}")

        else:
            if st.button("Login", type="primary"):
                email = email.strip()

                if not email or not password:
                    st.error("Enter your email address and password.")
                else:
                    try:
                        result = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })

                        if result.user and result.session:
                            st.session_state.user = result.user
                            st.session_state.access_token = (
                                result.session.access_token
                            )
                            st.rerun()
                        else:
                            st.error("Login failed. Please try again.")

                    except Exception:
                        st.error(
                            "Login failed. Check your credentials and "
                            "confirm your email address."
                        )

    st.stop()




# ==========================================
# Sidebar
# ==========================================

st.sidebar.title("📧 SmartMail AI")
st.sidebar.markdown("---")

# Navigation at the top
st.sidebar.subheader("Navigation")

page = st.sidebar.radio(
    "Choose a page",
    [
        "Generate Email",
        "Email History",
        "Analytics",
    ],
    key="main_navigation",
    label_visibility="collapsed",
)

st.sidebar.markdown("---")

# About section
st.sidebar.header("About")

st.sidebar.write("""
An AI-powered assistant for professional email writing.

**Features**
- ✨ AI email generation
- 🔎 Email history and search
- 📊 Analytics dashboard
- 📥 CSV export

**Built with**
Python · Streamlit · Gemini AI
""")

# Push account and Logout to the bottom
st.sidebar.markdown(
    """
    <style>
    [data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")

if st.session_state.user is not None:
    st.sidebar.subheader("Your Account")

    st.sidebar.caption(
        f"Logged in as: {st.session_state.user.email}"
    )

    # Flexible space above the account section
    st.sidebar.markdown(
        '<div style="height: 18vh;"></div>',
        unsafe_allow_html=True,
    )

    if st.sidebar.button(
        "Logout",
        use_container_width=True,
        key="sidebar_logout",
    ):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        st.session_state.user = None
        st.session_state.access_token = None
        st.rerun()



# ==========================================
# Generate Email Page
# ==========================================

if page == "Generate Email":

    with st.container(width=900):
        st.title("📧 SmartMail AI")
        st.subheader("AI-Powered Email Assistant")

        # User-friendly email type labels
        email_type_options = {
            "Job Application": "job_application",
            "Follow-up Email": "follow_up",
            "Meeting Request": "meeting_request",
            "Leave Request": "leave_request",
            "Apology Email": "apology",
        }

        selected_email_type = st.selectbox(
            "Select Email Type",
            list(email_type_options.keys()),
        )

        email_type = email_type_options[selected_email_type]

        # Email purpose
        purpose = st.text_input(
            "Purpose of the Email",
            placeholder="e.g., Apply for a Business Analyst position",
        )

        # Additional context
        context = st.text_area(
            "Context / Details",
            placeholder=(
                "Add relevant details, experience, "
                "recipient information, or key points..."
            ),
        )

        # Email tone
        tone = st.selectbox(
            "Select Tone",
            ["formal", "semi-formal", "casual"],
        )

        # Primary generate button
        generate = st.button(
            "✨ Generate Email",
            type="primary",
            use_container_width=True,
        )

        if generate:
            if not purpose.strip():
                st.warning("Please enter the purpose of your email.")

            else:
                email = generate_email(
                    email_type,
                    purpose,
                    context,
                    tone,
                )

                # Do not save failed API responses
                if email.startswith("Email generation failed:"):
                   st.error(
                      "Email generation is temporarily unavailable. "
                     "Please try again later."
         )

                else:
                    # Save successful emails to Supabase
                    try:
                        supabase.postgrest.auth(
                            st.session_state.access_token
                        )

                        supabase.table("emails").insert({
                            "user_id": str(st.session_state.user.id),
                            "email_type": email_type,
                            "purpose": purpose,
                            "context": context,
                            "tone": tone,
                            "email_content": email
                        }).execute()

                        st.success(
                            "Email generated successfully and saved to your account!"
                        )

                    except Exception as e:
                        st.error(
                            "Email generated, but saving to your history failed."
                        )
                        st.caption(f"Debug details: {e}")



                    st.subheader("✉️ Generated Email")

                    # Dark document-style preview
                    import html

                    formatted_email = html.escape(email).replace(
                        "\n", "<br>"
                    )

                    st.markdown(
                        f"""
                        <div style="
                            background-color: #1e2029;
                            color: #f1f3f5;
                            padding: 28px 32px;
                            border-radius: 12px;
                            border: 1px solid #383b46;
                            line-height: 1.9;
                            font-size: 16px;
                            font-family: Arial, sans-serif;
                            overflow-wrap: anywhere;
                            box-shadow: 0 4px 14px rgba(0,0,0,0.18);
                        ">
                            {formatted_email}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Download generated email
                    st.download_button(
                        "📥 Download Email",
                        email,
                        file_name="generated_email.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )





# ==========================================
# Email History Page
# ==========================================

elif page == "Email History":

    st.header("📜 Email History")

    # Authenticate database requests as the logged-in user
    supabase.postgrest.auth(
        st.session_state.access_token
    )

    search = st.text_input(
        "🔍 Search Previous Emails",
        key="email_history_search"
    )

    try:
        # Fetch this user's complete email history
        response = (
            supabase.table("emails")
            .select("*")
            .eq(
                "user_id",
                str(st.session_state.user.id)
            )
            .order("created_at", desc=True)
            .execute()
        )

        emails = response.data or []

        # Apply search to the same records used by the page
        if search.strip():
            term = search.strip().lower()

            emails = [
                row for row in emails
                if any(
                    term in str(row.get(field) or "").lower()
                    for field in [
                        "email_type",
                        "purpose",
                        "context",
                        "tone",
                        "email_content"
                    ]
                )
            ]

        # Count and display the same filtered list
        st.write(f"Showing {len(emails)} email(s)")

        if not emails:
            st.info(
                "No emails found. Generate an email or "
                "try a different search."
            )

        else:
            for row in emails:

                created_at = pd.to_datetime(
                    row["created_at"],
                    utc=True
                ).tz_convert("Asia/Kolkata")

                formatted_date = created_at.strftime(
                    "%d %b %Y · %I:%M %p IST"
                )

                email_type = row.get(
                    "email_type", "Email"
                )

                with st.expander(
                    f"{email_type} — {formatted_date}"
                ):
                    st.write(
                        f"**Purpose:** "
                        f"{row.get('purpose') or '—'}"
                    )

                    st.write(
                        f"**Tone:** "
                        f"{row.get('tone') or '—'}"
                    )

                    st.text_area(
                        "Email content",
                        value=row.get("email_content") or "",
                        height=250,
                        key=f"email_content_{row['id']}",
                    )

                    st.download_button(
                        "📥 Download Email",
                        data=row.get("email_content") or "",
                        file_name=f"{email_type}.txt",
                        mime="text/plain",
                        key=f"download_email_{row['id']}",
                    )

        # Export exactly the records currently displayed
        if emails:
            export_df = pd.DataFrame([
                {
                    "Email Type": row.get("email_type"),
                    "Purpose": row.get("purpose"),
                    "Context": row.get("context"),
                    "Tone": row.get("tone"),
                    "Email Content": row.get("email_content"),
                    "Created At (IST)": pd.to_datetime(
                        row["created_at"],
                        utc=True
                    ).tz_convert(
                        "Asia/Kolkata"
                    ).strftime("%d %b %Y %I:%M %p IST"),
                }
                for row in emails
            ])

            st.download_button(
                label="📥 Download Email History (CSV)",
                data=export_df.to_csv(index=False),
                file_name="email_history.csv",
                mime="text/csv",
                key="download_email_history_csv",
            )

    except Exception as e:
        st.error("Unable to load your email history.")
        st.caption(f"Debug details: {e}")



# ==========================================
# Analytics Page
# ==========================================

elif page == "Analytics":

    st.header("📊 Email Analytics")

    try:
        # Authenticate database requests as the logged-in user
        supabase.postgrest.auth(
            st.session_state.access_token
        )

        # Fetch this user's emails from Supabase
        response = (
            supabase.table("emails")
            .select("id, email_type, purpose, email_content")
            .eq(
                "user_id",
                str(st.session_state.user.id)
            )
            .execute()
        )

        emails = response.data or []

        # Categories for the dashboard
        categories = {
            "Job": 0,
            "Follow Up": 0,
            "Leave": 0,
            "Meeting": 0,
            "Apology": 0,
            "Other / Unclassified": 0,
        }

        category_map = {
            "job_application": "Job",
            "follow_up": "Follow Up",
            "leave_request": "Leave",
            "meeting_request": "Meeting",
            "apology": "Apology",
        }

        # Classify each database record exactly once
        for row in emails:

            email_type = str(
                row.get("email_type") or ""
            ).strip().lower()

            category = category_map.get(email_type)

            # Fall back to the email subject when type is unknown
            if category is None:

                content = str(
                    row.get("email_content") or ""
                ).lower()

                purpose = str(
                    row.get("purpose") or ""
                ).lower()

                text_to_check = content + " " + purpose

                if any(word in text_to_check for word in [
                    "job application",
                    "application for",
                    "applying for a job",
                ]):
                    category = "Job"

                elif any(word in text_to_check for word in [
                    "follow up",
                    "follow-up",
                    "following up",
                ]):
                    category = "Follow Up"

                elif any(word in text_to_check for word in [
                    "leave request",
                    "time off",
                    "absence",
                ]):
                    category = "Leave"

                elif any(word in text_to_check for word in [
                    "meeting request",
                    "schedule a call",
                ]):
                    category = "Meeting"

                elif any(word in text_to_check for word in [
                    "apology",
                    "apologize",
                    "apologise",
                ]):
                    category = "Apology"

                else:
                    category = "Other / Unclassified"

            categories[category] += 1

        # Display metrics
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
            categories["Other / Unclassified"],
        )

        # Build the chart from the same counts
        data = pd.DataFrame({
            "Email Type": list(categories.keys()),
            "Count": list(categories.values()),
        })

        fig = px.bar(
            data,
            x="Email Type",
            y="Count",
            color="Email Type",
            title="SmartMail AI - Email Analytics",
            text="Count",
        )

        fig.update_layout(
            xaxis_title="Email Type",
            yaxis_title="Number of Emails",
            showlegend=False,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

        # Verify the category counts
        category_total = sum(categories.values())

        if category_total == total:
            st.success(
                f"Verified: {category_total} emails accounted "
                "for across all categories."
            )
        else:
            st.error(
                f"Count mismatch: total={total}, "
                f"categories={category_total}"
            )

        if total == 0:
            st.info(
                "Your analytics will appear here after you "
                "generate and save your first email."
            )

    except Exception as e:
        st.error("Unable to load your analytics.")
        st.caption(f"Debug details: {e}")

    st.markdown("---")
    st.caption(
        "🚀 SmartMail AI | Built by Sumanth Kotian "
        "using Python, Streamlit & Plotly"
    )

