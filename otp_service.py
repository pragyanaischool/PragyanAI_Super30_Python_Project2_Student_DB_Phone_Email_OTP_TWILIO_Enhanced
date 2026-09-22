# ============================================================
# PragyanAI Student Verification System
# otp_service.py
# ============================================================

import re
import time
import random
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import streamlit as st

from twilio.rest import Client


# ============================================================
# OTP CONFIGURATION
# ============================================================

OTP_LENGTH = 6

# OTP validity = 5 minutes
OTP_EXPIRY_SECONDS = 300


# ============================================================
# EMAIL CONFIGURATION
# ============================================================

def get_email_config():
    """
    Read Gmail configuration from Streamlit Secrets.

    Expected secrets:

    EMAIL_ADDRESS = "your-email@gmail.com"
    EMAIL_APP_PASSWORD = "your-gmail-app-password"
    """

    try:

        email_address = st.secrets["EMAIL_ADDRESS"]
        email_app_password = st.secrets["EMAIL_APP_PASSWORD"]

        if not email_address or not email_app_password:

            return None, None

        return (
            str(email_address).strip(),
            str(email_app_password).strip(),
        )

    except Exception:

        return None, None


# ============================================================
# TWILIO CONFIGURATION
# ============================================================

def get_twilio_config():
    """
    Read Twilio configuration from Streamlit Secrets.

    Expected secrets:

    TWILIO_ACCOUNT_SID = "AC..."
    TWILIO_AUTH_TOKEN = "..."
    TWILIO_VERIFY_SERVICE_SID = "VA..."
    """

    try:

        account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
        auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
        verify_service_sid = st.secrets[
            "TWILIO_VERIFY_SERVICE_SID"
        ]

        if (
            not account_sid
            or not auth_token
            or not verify_service_sid
        ):
            return None, None, None

        return (
            str(account_sid).strip(),
            str(auth_token).strip(),
            str(verify_service_sid).strip(),
        )

    except Exception:

        return None, None, None


# ============================================================
# EMAIL VALIDATION
# ============================================================

def validate_email(email):
    """
    Validate email address.

    Returns:
        (True, success_message)
        OR
        (False, error_message)
    """

    if not email:

        return (
            False,
            "Email address is required."
        )

    email = email.strip().lower()

    email_pattern = (
        r"^[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    if not re.match(email_pattern, email):

        return (
            False,
            "Please enter a valid email address."
        )

    return (
        True,
        "Valid email address."
    )


# ============================================================
# PHONE VALIDATION
# ============================================================

def validate_phone(phone):
    """
    Validate phone number.

    Recommended format:

        +919900000001

    International format is expected because
    Twilio Verify requires an internationally
    formatted phone number.
    """

    if not phone:

        return (
            False,
            "Phone number is required."
        )

    phone = phone.strip()

    # Remove spaces, hyphens and brackets
    normalized_phone = re.sub(
        r"[\s\-\(\)]",
        "",
        phone
    )

    # International format
    if not normalized_phone.startswith("+"):

        return (
            False,
            "Phone number must include country code. "
            "Example: +919900000001"
        )

    # Must contain only + and digits
    if not re.match(
        r"^\+[1-9][0-9]{7,14}$",
        normalized_phone
    ):

        return (
            False,
            "Please enter a valid international phone number."
        )

    return (
        True,
        "Valid phone number."
    )


# ============================================================
# GENERATE OTP
# ============================================================

def generate_otp():
    """
    Generate a secure 6-digit numeric OTP.
    """

    return "".join(
        str(random.randint(0, 9))
        for _ in range(OTP_LENGTH)
    )


# ============================================================
# OTP EXPIRY CHECK
# ============================================================

def otp_is_valid(otp_time):
    """
    Check whether an OTP timestamp is still valid.

    OTP validity:
        5 minutes / 300 seconds
    """

    if otp_time is None:

        return False

    try:

        elapsed_time = time.time() - float(otp_time)

        return elapsed_time <= OTP_EXPIRY_SECONDS

    except (
        TypeError,
        ValueError,
        OverflowError
    ):

        return False


# ============================================================
# OTP REMAINING TIME
# ============================================================

def otp_remaining_seconds(otp_time):
    """
    Return remaining OTP validity in seconds.

    Returns:
        Integer seconds remaining.

    Returns 0 if expired or invalid.
    """

    if otp_time is None:

        return 0

    try:

        elapsed_time = time.time() - float(otp_time)

        remaining = OTP_EXPIRY_SECONDS - elapsed_time

        if remaining <= 0:

            return 0

        return int(remaining)

    except (
        TypeError,
        ValueError,
        OverflowError
    ):

        return 0


# ============================================================
# SEND EMAIL OTP
# ============================================================

def send_email_otp(email, otp):
    """
    Send OTP through Gmail SMTP.

    Gmail SMTP:
        smtp.gmail.com
        Port 587
        STARTTLS
    """

    # --------------------------------------------------------
    # Validate email
    # --------------------------------------------------------

    valid, message = validate_email(email)

    if not valid:

        return False, message


    # --------------------------------------------------------
    # Validate OTP
    # --------------------------------------------------------

    if not otp:

        return (
            False,
            "OTP is required."
        )


    # --------------------------------------------------------
    # Get Gmail configuration
    # --------------------------------------------------------

    sender_email, sender_password = get_email_config()

    if not sender_email or not sender_password:

        return (
            False,
            "Email configuration is missing from "
            "Streamlit Secrets. Please configure "
            "EMAIL_ADDRESS and EMAIL_APP_PASSWORD."
        )


    # --------------------------------------------------------
    # Prepare email
    # --------------------------------------------------------

    subject = "PragyanAI Student Verification - Email OTP"

    body = f"""
Dear Student,

Welcome to PragyanAI Student Verification Portal.

Your Email Verification OTP is:

{otp}

This OTP is valid for 5 minutes.

Please do not share this OTP with anyone.

If you did not request this OTP, please ignore this email.

Regards,

PragyanAI
Student Verification Team
"""


    # --------------------------------------------------------
    # Create MIME message
    # --------------------------------------------------------

    message_obj = MIMEMultipart()

    message_obj["From"] = sender_email
    message_obj["To"] = email.strip().lower()
    message_obj["Subject"] = subject

    message_obj.attach(
        MIMEText(
            body,
            "plain"
        )
    )


    # --------------------------------------------------------
    # Send email
    # --------------------------------------------------------

    try:

        with smtplib.SMTP(
            "smtp.gmail.com",
            587,
            timeout=30
        ) as server:

            server.ehlo()

            server.starttls()

            server.ehlo()

            server.login(
                sender_email,
                sender_password
            )

            server.sendmail(
                sender_email,
                email.strip().lower(),
                message_obj.as_string()
            )

        return (
            True,
            "Email OTP sent successfully."
        )

    except smtplib.SMTPAuthenticationError:

        return (
            False,
            "Gmail authentication failed. "
            "Please verify EMAIL_ADDRESS and "
            "EMAIL_APP_PASSWORD in Streamlit Secrets."
        )

    except smtplib.SMTPException as e:

        return (
            False,
            f"Unable to send email OTP: {e}"
        )

    except Exception as e:

        return (
            False,
            f"Email OTP error: {e}"
        )


# ============================================================
# SEND PHONE OTP
# ============================================================

def send_phone_otp(phone):
    """
    Send OTP using Twilio Verify.

    Twilio Verify generates and sends the OTP.
    """

    # --------------------------------------------------------
    # Validate phone
    # --------------------------------------------------------

    valid, message = validate_phone(phone)

    if not valid:

        return False, message


    # --------------------------------------------------------
    # Get Twilio configuration
    # --------------------------------------------------------

    (
        account_sid,
        auth_token,
        verify_service_sid,
    ) = get_twilio_config()

    if (
        not account_sid
        or not auth_token
        or not verify_service_sid
    ):

        return (
            False,
            "Twilio configuration is missing from "
            "Streamlit Secrets. Please configure "
            "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN "
            "and TWILIO_VERIFY_SERVICE_SID."
        )


    # --------------------------------------------------------
    # Normalize phone
    # --------------------------------------------------------

    phone = re.sub(
        r"[\s\-\(\)]",
        "",
        phone.strip()
    )


    # --------------------------------------------------------
    # Send OTP
    # --------------------------------------------------------

    try:

        client = Client(
            account_sid,
            auth_token
        )

        verification = (
            client.verify
            .v2
            .services(verify_service_sid)
            .verifications
            .create(
                to=phone,
                channel="sms"
            )
        )

        if verification.status in (
            "pending",
            "approved"
        ):

            return (
                True,
                "Phone OTP sent successfully."
            )

        return (
            False,
            f"Unable to send Phone OTP. "
            f"Twilio status: {verification.status}"
        )

    except Exception as e:

        return (
            False,
            f"Phone OTP error: {e}"
        )


# ============================================================
# VERIFY PHONE OTP
# ============================================================

def verify_phone_otp(phone, otp):
    """
    Verify the OTP entered by the student
    using Twilio Verify.
    """

    # --------------------------------------------------------
    # Validate phone
    # --------------------------------------------------------

    valid, message = validate_phone(phone)

    if not valid:

        return False, message


    # --------------------------------------------------------
    # Validate OTP
    # --------------------------------------------------------

    if not otp:

        return (
            False,
            "Please enter the Phone OTP."
        )


    otp = str(otp).strip()

    if not otp.isdigit():

        return (
            False,
            "Phone OTP must contain only numbers."
        )


    # --------------------------------------------------------
    # Get Twilio configuration
    # --------------------------------------------------------

    (
        account_sid,
        auth_token,
        verify_service_sid,
    ) = get_twilio_config()

    if (
        not account_sid
        or not auth_token
        or not verify_service_sid
    ):

        return (
            False,
            "Twilio configuration is missing from "
            "Streamlit Secrets."
        )


    # --------------------------------------------------------
    # Normalize phone
    # --------------------------------------------------------

    phone = re.sub(
        r"[\s\-\(\)]",
        "",
        phone.strip()
    )


    # --------------------------------------------------------
    # Verify OTP
    # --------------------------------------------------------

    try:

        client = Client(
            account_sid,
            auth_token
        )

        verification_check = (
            client.verify
            .v2
            .services(verify_service_sid)
            .verification_checks
            .create(
                to=phone,
                code=otp
            )
        )


        # ----------------------------------------------------
        # Twilio returns "approved" when OTP is correct
        # ----------------------------------------------------

        if verification_check.status == "approved":

            return (
                True,
                "Phone OTP verified successfully."
            )


        return (
            False,
            "Invalid or expired Phone OTP."
        )

    except Exception as e:

        return (
            False,
            f"Phone OTP verification error: {e}"
        )


# ============================================================
# OPTIONAL EMAIL OTP VERIFICATION HELPER
# ============================================================

def verify_email_otp(
    entered_otp,
    stored_otp,
    otp_time
):
    """
    Verify an Email OTP.

    This helper is optional but useful if the
    verification logic needs to be reused elsewhere.

    Returns:
        (True, message)
        OR
        (False, message)
    """

    if not stored_otp:

        return (
            False,
            "Please request an Email OTP first."
        )


    if not otp_time:

        return (
            False,
            "OTP timestamp is missing."
        )


    if not otp_is_valid(otp_time):

        return (
            False,
            "OTP has expired. Please request a new OTP."
        )


    if not entered_otp:

        return (
            False,
            "Please enter the Email OTP."
        )


    entered_otp = str(
        entered_otp
    ).strip()

    stored_otp = str(
        stored_otp
    ).strip()


    if entered_otp != stored_otp:

        return (
            False,
            "Invalid Email OTP."
        )


    return (
        True,
        "Email OTP verified successfully."
    )


# ============================================================
# END OF otp_service.py
# ============================================================
