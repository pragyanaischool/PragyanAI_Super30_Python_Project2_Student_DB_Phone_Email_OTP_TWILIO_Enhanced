# ============================================================
# PragyanAI Student Verification System
# auth.py
# ============================================================

import hashlib
import hmac
import os
import secrets

import streamlit as st


# ============================================================
# PASSWORD CONFIGURATION
# ============================================================
#
# IMPORTANT:
# These values MUST MATCH db.py.
#
# db.py currently uses:
#
#   HASH_ITERATIONS = 310_000
#   SALT_LENGTH     = 32
#   KEY_LENGTH      = 32
#
# Sample database password format:
#
#   <salt_hex>$<hash_hex>
#
# New registered student password format created here:
#
#   pbkdf2_sha256$310000$<salt_hex>$<hash_hex>
#
# verify_password() supports BOTH formats.
#
# ============================================================

PASSWORD_HASH_ALGORITHM = "sha256"

PASSWORD_ITERATIONS = 310_000

SALT_LENGTH = 32

KEY_LENGTH = 32


# ============================================================
# PASSWORD VALIDATION
# ============================================================

def validate_password(password):
    """
    Validate student password.

    Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number

    Returns:
        (True, message)
        OR
        (False, message)
    """

    if not password:

        return (
            False,
            "Password is required."
        )

    if len(password) < 8:

        return (
            False,
            "Password must contain at least 8 characters."
        )

    if not any(
        character.isupper()
        for character in password
    ):

        return (
            False,
            "Password must contain at least one uppercase letter."
        )

    if not any(
        character.islower()
        for character in password
    ):

        return (
            False,
            "Password must contain at least one lowercase letter."
        )

    if not any(
        character.isdigit()
        for character in password
    ):

        return (
            False,
            "Password must contain at least one number."
        )

    return (
        True,
        "Password is valid."
    )


# ============================================================
# HASH PASSWORD
# ============================================================

def hash_password(password):
    """
    Securely hash a password using:

        PBKDF2-HMAC-SHA256

    New registered-student format:

        pbkdf2_sha256$310000$<salt>$<hash>

    This function is used when creating a new
    student account.
    """

    if password is None:

        raise ValueError(
            "Password cannot be None."
        )

    password = str(password)

    # --------------------------------------------------------
    # Validate password
    # --------------------------------------------------------

    valid, message = validate_password(
        password
    )

    if not valid:

        raise ValueError(
            message
        )

    # --------------------------------------------------------
    # Generate random salt
    # --------------------------------------------------------

    salt = secrets.token_bytes(
        SALT_LENGTH
    )

    # --------------------------------------------------------
    # Generate password hash
    # --------------------------------------------------------

    password_hash = hashlib.pbkdf2_hmac(
        PASSWORD_HASH_ALGORITHM,
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
        dklen=KEY_LENGTH
    )

    # --------------------------------------------------------
    # Convert to hexadecimal
    # --------------------------------------------------------

    salt_hex = salt.hex()

    hash_hex = password_hash.hex()

    # --------------------------------------------------------
    # Store algorithm metadata
    # --------------------------------------------------------

    return (
        f"pbkdf2_sha256$"
        f"{PASSWORD_ITERATIONS}$"
        f"{salt_hex}$"
        f"{hash_hex}"
    )


# ============================================================
# VERIFY PASSWORD
# ============================================================

def verify_password(
    password,
    stored_password
):
    """
    Verify a plain-text password against a stored
    password hash.

    Supports BOTH formats:

    --------------------------------------------------------
    FORMAT 1 - Current registered users
    --------------------------------------------------------

    pbkdf2_sha256$310000$<salt>$<hash>


    --------------------------------------------------------
    FORMAT 2 - Existing sample users from db.py
    --------------------------------------------------------

    <salt>$<hash>

    The second format uses:

        SHA256
        310000 iterations
        32-byte salt
        32-byte derived key

    This compatibility is important because your
    existing sample accounts were created by db.py.
    """

    if password is None:

        return False

    if not stored_password:

        return False

    password = str(password)

    stored_password = str(
        stored_password
    ).strip()

    if not password:

        return False

    if not stored_password:

        return False

    try:

        # ====================================================
        # FORMAT 1
        #
        # pbkdf2_sha256$310000$salt$hash
        # ====================================================

        parts = stored_password.split("$")

        if len(parts) == 4:

            algorithm = parts[0]

            iterations_text = parts[1]

            salt_hex = parts[2]

            stored_hash_hex = parts[3]

            # ------------------------------------------------
            # Validate algorithm
            # ------------------------------------------------

            if algorithm != "pbkdf2_sha256":

                return False

            # ------------------------------------------------
            # Read iteration count from stored hash
            # ------------------------------------------------

            iterations = int(
                iterations_text
            )

            if iterations <= 0:

                return False

            # ------------------------------------------------
            # Convert salt
            # ------------------------------------------------

            salt = bytes.fromhex(
                salt_hex
            )

            # ------------------------------------------------
            # Convert stored hash
            # ------------------------------------------------

            stored_hash = bytes.fromhex(
                stored_hash_hex
            )

            # ------------------------------------------------
            # Generate calculated hash
            # ------------------------------------------------

            calculated_hash = hashlib.pbkdf2_hmac(
                PASSWORD_HASH_ALGORITHM,
                password.encode("utf-8"),
                salt,
                iterations,
                dklen=len(stored_hash)
            )

            # ------------------------------------------------
            # Secure comparison
            # ------------------------------------------------

            return hmac.compare_digest(
                calculated_hash,
                stored_hash
            )

        # ====================================================
        # FORMAT 2
        #
        # salt$hash
        #
        # Used by db.py sample accounts
        # ====================================================

        if len(parts) == 2:

            salt_hex = parts[0]

            stored_hash_hex = parts[1]

            # ------------------------------------------------
            # Convert salt
            # ------------------------------------------------

            salt = bytes.fromhex(
                salt_hex
            )

            # ------------------------------------------------
            # Convert stored hash
            # ------------------------------------------------

            stored_hash = bytes.fromhex(
                stored_hash_hex
            )

            # ------------------------------------------------
            # Validate expected sample configuration
            #
            # db.py:
            #
            #   HASH_ITERATIONS = 310_000
            #   SALT_LENGTH = 32
            #   KEY_LENGTH = 32
            # ------------------------------------------------

            if len(salt) != SALT_LENGTH:

                return False

            if len(stored_hash) != KEY_LENGTH:

                return False

            # ------------------------------------------------
            # Generate calculated hash
            # ------------------------------------------------

            calculated_hash = hashlib.pbkdf2_hmac(
                PASSWORD_HASH_ALGORITHM,
                password.encode("utf-8"),
                salt,
                PASSWORD_ITERATIONS,
                dklen=KEY_LENGTH
            )

            # ------------------------------------------------
            # Secure comparison
            # ------------------------------------------------

            return hmac.compare_digest(
                calculated_hash,
                stored_hash
            )

        # ====================================================
        # Unknown password format
        # ====================================================

        return False

    except (
        ValueError,
        TypeError,
        UnicodeError
    ):

        return False

    except Exception:

        return False


# ============================================================
# STUDENT LOGIN
# ============================================================

def student_login(
    email,
    password,
    db_connection=None
):
    """
    Authenticate a student using email and password.

    Parameters:
        email:
            Student email address.

        password:
            Student password.

        db_connection:
            Optional SQLite connection.

    Returns:

        (
            success,
            message,
            student
        )

    Example:

        success, message, student = student_login(
            email,
            password
        )
    """

    # ========================================================
    # VALIDATE EMAIL
    # ========================================================

    if not email:

        return (
            False,
            "Please enter your email address.",
            None
        )

    # ========================================================
    # VALIDATE PASSWORD
    # ========================================================

    if not password:

        return (
            False,
            "Please enter your password.",
            None
        )

    # ========================================================
    # NORMALIZE EMAIL
    # ========================================================

    email = (
        str(email)
        .strip()
        .lower()
    )

    # ========================================================
    # FIND STUDENT
    # ========================================================

    try:

        from db import get_student_by_email

        student = get_student_by_email(
            email
        )

    except Exception as e:

        print(
            "LOGIN DATABASE ERROR:",
            e
        )

        return (
            False,
            "Unable to access student database.",
            None
        )

    # ========================================================
    # STUDENT NOT FOUND
    # ========================================================

    if not student:

        print(
            "LOGIN DEBUG: Student not found:",
            email
        )

        return (
            False,
            "Invalid email or password.",
            None
        )

    # ========================================================
    # STUDENT FOUND
    # ========================================================

    print(
        "LOGIN DEBUG: Student found:",
        student.get("full_name"),
        "|",
        student.get("email")
    )

    # ========================================================
    # GET STORED PASSWORD
    # ========================================================

    stored_password = student.get(
        "password_hash"
    )

    if not stored_password:

        print(
            "LOGIN DEBUG: Password hash missing."
        )

        return (
            False,
            "Invalid email or password.",
            None
        )

    # ========================================================
    # VERIFY PASSWORD
    # ========================================================

    password_valid = verify_password(
        password,
        stored_password
    )

    print(
        "LOGIN DEBUG: Password valid =",
        password_valid
    )

    # ========================================================
    # INVALID PASSWORD
    # ========================================================

    if not password_valid:

        return (
            False,
            "Invalid email or password.",
            None
        )

    # ========================================================
    # LOGIN SUCCESS
    # ========================================================

    print(
        "LOGIN DEBUG: Login successful for:",
        email
    )

    return (
        True,
        "Student login successful.",
        student
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

def admin_login(
    email,
    password
):
    """
    Authenticate administrator using Streamlit Secrets.

    Expected secrets:

        ADMIN_EMAIL
        ADMIN_PASSWORD
    """

    if not email:

        return (
            False,
            "Please enter admin email."
        )

    if not password:

        return (
            False,
            "Please enter admin password."
        )

    # ========================================================
    # READ ADMIN CONFIGURATION
    # ========================================================

    try:

        configured_email = st.secrets[
            "ADMIN_EMAIL"
        ]

        configured_password = st.secrets[
            "ADMIN_PASSWORD"
        ]

    except Exception:

        return (
            False,
            "Admin configuration is missing from "
            "Streamlit Secrets. Please configure "
            "ADMIN_EMAIL and ADMIN_PASSWORD."
        )

    # ========================================================
    # NORMALIZE EMAIL
    # ========================================================

    email = (
        str(email)
        .strip()
        .lower()
    )

    configured_email = (
        str(configured_email)
        .strip()
        .lower()
    )

    configured_password = str(
        configured_password
    )

    # ========================================================
    # VERIFY ADMIN CREDENTIALS
    # ========================================================

    email_match = hmac.compare_digest(
        email,
        configured_email
    )

    password_match = hmac.compare_digest(
        str(password),
        configured_password
    )

    if not email_match or not password_match:

        return (
            False,
            "Invalid admin email or password."
        )

    # ========================================================
    # LOGIN SUCCESS
    # ========================================================

    return (
        True,
        "Admin login successful."
    )


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

def initialize_session_state():
    """
    Initialize all Streamlit session-state variables
    used by the application.
    """

    # ========================================================
    # GENERAL LOGIN STATE
    # ========================================================

    if "logged_in" not in st.session_state:

        st.session_state.logged_in = False

    if "user_type" not in st.session_state:

        st.session_state.user_type = None

    # ========================================================
    # STUDENT SESSION
    # ========================================================

    if "student_id" not in st.session_state:

        st.session_state.student_id = None

    if "student_email" not in st.session_state:

        st.session_state.student_email = None

    if "student_name" not in st.session_state:

        st.session_state.student_name = None

    # ========================================================
    # ADMIN SESSION
    # ========================================================

    if "admin_logged_in" not in st.session_state:

        st.session_state.admin_logged_in = False

    # ========================================================
    # EMAIL OTP
    # ========================================================

    if "email_otp" not in st.session_state:

        st.session_state.email_otp = None

    if "email_otp_time" not in st.session_state:

        st.session_state.email_otp_time = None

    # ========================================================
    # PHONE OTP
    # ========================================================

    if "phone_otp_sent" not in st.session_state:

        st.session_state.phone_otp_sent = False

    # ========================================================
    # REGISTRATION DATA
    # ========================================================

    if "registration_data" not in st.session_state:

        st.session_state.registration_data = {}

    # ========================================================
    # VERIFICATION STATUS
    # ========================================================

    if "email_verified" not in st.session_state:

        st.session_state.email_verified = False

    if "phone_verified" not in st.session_state:

        st.session_state.phone_verified = False


# ============================================================
# SET STUDENT SESSION
# ============================================================

def set_student_session(student):
    """
    Store authenticated student information
    in Streamlit session state.
    """

    if not student:

        return

    # ========================================================
    # GENERAL LOGIN
    # ========================================================

    st.session_state.logged_in = True

    st.session_state.user_type = "student"

    # ========================================================
    # STUDENT INFORMATION
    # ========================================================

    st.session_state.student_id = (
        student["id"]
    )

    st.session_state.student_email = (
        student["email"]
    )

    st.session_state.student_name = (
        student["full_name"]
    )

    # ========================================================
    # ADMIN SESSION MUST BE FALSE
    # ========================================================

    st.session_state.admin_logged_in = False


# ============================================================
# SET ADMIN SESSION
# ============================================================

def set_admin_session():
    """
    Store authenticated administrator information
    in Streamlit session state.
    """

    st.session_state.logged_in = True

    st.session_state.user_type = "admin"

    st.session_state.admin_logged_in = True

    # ========================================================
    # CLEAR STUDENT SESSION
    # ========================================================

    st.session_state.student_id = None

    st.session_state.student_email = None

    st.session_state.student_name = None


# ============================================================
# CHECK GENERAL LOGIN
# ============================================================

def is_logged_in():
    """
    Return True when any authenticated user
    is currently logged in.
    """

    return bool(
        st.session_state.get(
            "logged_in",
            False
        )
    )


# ============================================================
# CHECK STUDENT LOGIN
# ============================================================

def is_student_logged_in():
    """
    Return True if the current session belongs
    to an authenticated student.
    """

    return (
        st.session_state.get(
            "logged_in",
            False
        )
        and
        st.session_state.get(
            "user_type"
        ) == "student"
        and
        st.session_state.get(
            "student_id"
        ) is not None
    )


# ============================================================
# CHECK ADMIN LOGIN
# ============================================================

def is_admin_logged_in():
    """
    Return True if an administrator is authenticated.
    """

    return (
        st.session_state.get(
            "logged_in",
            False
        )
        and
        st.session_state.get(
            "user_type"
        ) == "admin"
        and
        st.session_state.get(
            "admin_logged_in",
            False
        )
    )


# ============================================================
# GET CURRENT USER TYPE
# ============================================================

def get_current_user_type():
    """
    Return:

        "student"
        "admin"
        None
    """

    if not is_logged_in():

        return None

    return st.session_state.get(
        "user_type"
    )


# ============================================================
# LOGOUT
# ============================================================

def logout():
    """
    Clear authentication-related session state.

    Registration/OTP state is also cleared so that
    another user cannot accidentally continue an
    incomplete registration after logout.
    """

    # ========================================================
    # LOGIN STATE
    # ========================================================

    st.session_state.logged_in = False

    st.session_state.user_type = None

    # ========================================================
    # STUDENT STATE
    # ========================================================

    st.session_state.student_id = None

    st.session_state.student_email = None

    st.session_state.student_name = None

    # ========================================================
    # ADMIN STATE
    # ========================================================

    st.session_state.admin_logged_in = False

    # ========================================================
    # EMAIL OTP
    # ========================================================

    st.session_state.email_otp = None

    st.session_state.email_otp_time = None

    # ========================================================
    # PHONE OTP
    # ========================================================

    st.session_state.phone_otp_sent = False

    # ========================================================
    # REGISTRATION STATE
    # ========================================================

    st.session_state.registration_data = {}

    st.session_state.email_verified = False

    st.session_state.phone_verified = False


# ============================================================
# CLEAR REGISTRATION SESSION
# ============================================================

def clear_registration_session():
    """
    Clear only registration and OTP-related state.

    Useful after successful registration without
    logging out of an existing session.
    """

    st.session_state.email_otp = None

    st.session_state.email_otp_time = None

    st.session_state.phone_otp_sent = False

    st.session_state.registration_data = {}

    st.session_state.email_verified = False

    st.session_state.phone_verified = False


# ============================================================
# GET CURRENT STUDENT ID
# ============================================================

def get_current_student_id():
    """
    Return currently logged-in student ID.
    """

    if not is_student_logged_in():

        return None

    return st.session_state.get(
        "student_id"
    )


# ============================================================
# GET CURRENT STUDENT EMAIL
# ============================================================

def get_current_student_email():
    """
    Return currently logged-in student email.
    """

    if not is_student_logged_in():

        return None

    return st.session_state.get(
        "student_email"
    )


# ============================================================
# GET CURRENT STUDENT NAME
# ============================================================

def get_current_student_name():
    """
    Return currently logged-in student name.
    """

    if not is_student_logged_in():

        return None

    return st.session_state.get(
        "student_name"
    )


# ============================================================
# END OF auth.py
# ============================================================
