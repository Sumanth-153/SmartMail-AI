def generate_email(email_type, purpose, context, tone):

    return f"""
Subject: {purpose.title()}

Dear Hiring Manager,

This is a {tone} {email_type} email.

Purpose:
{purpose}

Details:
{context}

Regards,
Sumanth
"""