# ============================================================
# db.py
# ============================================================
# PragyanAI Student Verification System
#
# Database Layer
#
# Database:
#     SQLite
#
# Features:
#     1. Create Database
#     2. Create Students Table
#     3. Create Student
#     4. Get Student by ID
#     5. Get Student by Email
#     6. Get Student by Phone
#     7. Check Email / Phone
#     8. Update Student Profile
#     9. Update Verification Status
#    10. Update Approval Status
#    11. Get All Students
#    12. Get Students by Status
#    13. Student Dashboard Counts
#    14. Insert Sample Students
#    15. Repair Sample Passwords
#    16. Verify Password Hash
#
# ============================================================


import sqlite3
from pathlib import Path
import hashlib
import secrets
import hmac


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "students.db"


# ============================================================
# PASSWORD CONFIGURATION
# ============================================================
#
# IMPORTANT:
# auth.py MUST use the same HASH_ITERATIONS,
# SALT_LENGTH and hashing algorithm.
#
# ============================================================

HASH_ITERATIONS = 310_000

SALT_LENGTH = 32

KEY_LENGTH = 32


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create and return SQLite database connection.
    """

    connection = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# HASH PASSWORD
# ============================================================

def hash_sample_password(password):
    """
    Hash password using PBKDF2-HMAC-SHA256.

    Format:

        salt_hex$password_hash_hex

    Used for sample student accounts.

    IMPORTANT:
    The same HASH_ITERATIONS must be used by auth.py
    when verifying the password.
    """

    if not password:
        raise ValueError("Password cannot be empty.")

    salt = secrets.token_bytes(
        SALT_LENGTH
    )

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        HASH_ITERATIONS,
        dklen=KEY_LENGTH
    )

    return (
        salt.hex()
        + "$"
        + password_hash.hex()
    )


# ============================================================
# VERIFY PASSWORD HASH
# ============================================================

def verify_sample_password(password, stored_password):
    """
    Verify password against stored PBKDF2 password hash.

    This function uses EXACTLY the same configuration
    as hash_sample_password().

    Returns:
        True  -> password is correct
        False -> password is incorrect
    """

    try:

        if not password:
            return False

        if not stored_password:
            return False

        # ----------------------------------------------------
        # Split stored password
        # ----------------------------------------------------

        parts = stored_password.split("$", 1)

        if len(parts) != 2:
            return False

        salt_hex = parts[0]

        hash_hex = parts[1]

        # ----------------------------------------------------
        # Convert HEX to bytes
        # ----------------------------------------------------

        salt = bytes.fromhex(
            salt_hex
        )

        expected_hash = bytes.fromhex(
            hash_hex
        )

        # ----------------------------------------------------
        # Generate hash using SAME configuration
        # ----------------------------------------------------

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            HASH_ITERATIONS,
            dklen=KEY_LENGTH
        )

        # ----------------------------------------------------
        # Secure comparison
        # ----------------------------------------------------

        return hmac.compare_digest(
            calculated_hash,
            expected_hash
        )

    except (
        ValueError,
        TypeError,
        AttributeError
    ):

        return False


# ============================================================
# REPAIR SAMPLE STUDENT PASSWORDS
# ============================================================

def repair_sample_student_passwords(connection):
    """
    Repair passwords for predefined demo/sample
    student accounts.

    This does NOT delete students.

    This does NOT modify:
        - Name
        - College
        - Degree
        - Branch
        - CGPA
        - Phone
        - Verification
        - Approval status
        - Rejection reason

    It only updates password_hash for predefined
    sample accounts.

    Sample password:

        Student@123
    """

    sample_accounts = [

        "rahul.sharma@example.com",

        "priya.kumar@example.com",

        "arjun.rao@example.com",

        "sneha.reddy@example.com",

        "vivek.kumar@example.com",

    ]

    cursor = connection.cursor()

    repaired = 0

    # --------------------------------------------------------
    # Generate ONE valid password hash
    # --------------------------------------------------------

    new_password_hash = hash_sample_password(
        "Student@123"
    )

    # --------------------------------------------------------
    # Update each sample account
    # --------------------------------------------------------

    for email in sample_accounts:

        cursor.execute(
            """
            UPDATE students

            SET
                password_hash = ?,
                updated_at = CURRENT_TIMESTAMP

            WHERE
                LOWER(email) = LOWER(?)
            """,

            (
                new_password_hash,
                email
            )
        )

        if cursor.rowcount > 0:

            repaired += cursor.rowcount

    # --------------------------------------------------------
    # Commit changes
    # --------------------------------------------------------

    connection.commit()

    print(
        "Sample student passwords repaired: "
        f"{repaired}"
    )

    return repaired


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():
    """
    Initialize database.

    Behaviour:

    1. Create students table if it does not exist.
    2. Check whether student data exists.
    3. If database is empty:
           Add sample students.
    4. If students already exist:
           Preserve existing data.
    5. Repair predefined sample account passwords.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ====================================================
        # CREATE STUDENTS TABLE
        # ====================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                full_name TEXT NOT NULL,

                college_name TEXT NOT NULL,

                degree TEXT NOT NULL,

                branch TEXT NOT NULL,

                tenth_cgpa REAL,

                twelfth_cgpa REAL,

                be_cgpa REAL,

                phone TEXT UNIQUE NOT NULL,

                email TEXT UNIQUE NOT NULL,

                password_hash TEXT NOT NULL,

                email_verified INTEGER DEFAULT 0,

                phone_verified INTEGER DEFAULT 0,

                approval_status TEXT DEFAULT 'PENDING',

                rejection_reason TEXT,

                created_at
                    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                updated_at
                    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()

        # ====================================================
        # CHECK WHETHER STUDENTS ALREADY EXIST
        # ====================================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM students
            """
        )

        result = cursor.fetchone()

        student_count = int(
            result[0]
        )

        # ====================================================
        # DATABASE EMPTY
        # ====================================================

        if student_count == 0:

            print(
                "No student data found."
            )

            print(
                "Adding sample students..."
            )

            inserted = insert_sample_students(
                connection
            )

            print(
                "Sample student data added "
                f"successfully: {inserted}"
            )

        # ====================================================
        # DATABASE ALREADY HAS DATA
        # ====================================================

        else:

            print(
                f"{student_count} student(s) "
                "already exist."
            )

            print(
                "Existing student data preserved."
            )

        # ====================================================
        # REPAIR SAMPLE PASSWORDS
        # ====================================================
        #
        # This is intentionally executed even when
        # students already exist.
        #
        # This fixes old sample accounts whose password
        # hashes were generated using a different hashing
        # configuration.
        #
        # ====================================================

        repair_sample_student_passwords(
            connection
        )

    except Exception as error:

        connection.rollback()

        print(
            "Database initialization error:"
        )

        print(error)

        raise

    finally:

        connection.close()


# ============================================================
# CREATE STUDENT
# ============================================================

def create_student(
    full_name,
    college_name,
    degree,
    branch,
    tenth_cgpa,
    twelfth_cgpa,
    be_cgpa,
    phone,
    email,
    password_hash,
    email_verified=0,
    phone_verified=0
):
    """
    Create a new student account.

    Default approval status:

        PENDING
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO students (

                full_name,

                college_name,

                degree,

                branch,

                tenth_cgpa,

                twelfth_cgpa,

                be_cgpa,

                phone,

                email,

                password_hash,

                email_verified,

                phone_verified,

                approval_status

            )

            VALUES (
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, 'PENDING'
            )
            """,

            (
                full_name,
                college_name,
                degree,
                branch,
                tenth_cgpa,
                twelfth_cgpa,
                be_cgpa,
                phone,
                email,
                password_hash,
                email_verified,
                phone_verified
            )
        )

        student_id = cursor.lastrowid

        connection.commit()

        return student_id

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


# ============================================================
# GET STUDENT BY ID
# ============================================================

def get_student_by_id(
    student_id
):
    """
    Get one student by Student ID.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE id = ?
            """,

            (
                student_id,
            )
        )

        student = cursor.fetchone()

        if student:

            return dict(student)

        return None

    finally:

        connection.close()


# ============================================================
# GET STUDENT BY EMAIL
# ============================================================

def get_student_by_email(
    email
):
    """
    Get student using email.

    Email comparison is case-insensitive.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE LOWER(email) = LOWER(?)
            """,

            (
                email.strip(),
            )
        )

        student = cursor.fetchone()

        if student:

            return dict(student)

        return None

    finally:

        connection.close()


# ============================================================
# GET STUDENT BY PHONE
# ============================================================

def get_student_by_phone(
    phone
):
    """
    Get student using phone number.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE phone = ?
            """,

            (
                phone.strip(),
            )
        )

        student = cursor.fetchone()

        if student:

            return dict(student)

        return None

    finally:

        connection.close()


# ============================================================
# EMAIL OR PHONE EXISTS
# ============================================================

def email_or_phone_exists(
    email,
    phone,
    exclude_id=None
):
    """
    Check whether email or phone already exists.

    exclude_id is used when editing
    an existing student profile.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        if exclude_id:

            cursor.execute(
                """
                SELECT id
                FROM students

                WHERE
                    (
                        LOWER(email) = LOWER(?)
                        OR phone = ?
                    )

                    AND id != ?

                LIMIT 1
                """,

                (
                    email.strip(),
                    phone.strip(),
                    exclude_id
                )
            )

        else:

            cursor.execute(
                """
                SELECT id
                FROM students

                WHERE
                    LOWER(email) = LOWER(?)
                    OR phone = ?

                LIMIT 1
                """,

                (
                    email.strip(),
                    phone.strip()
                )
            )

        result = cursor.fetchone()

        return result is not None

    finally:

        connection.close()


# ============================================================
# UPDATE STUDENT PROFILE
# ============================================================

def update_student_profile(
    student_id,
    full_name,
    college_name,
    degree,
    branch,
    tenth_cgpa,
    twelfth_cgpa,
    be_cgpa,
    phone,
    email
):
    """
    Update complete student profile.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE students

            SET

                full_name = ?,

                college_name = ?,

                degree = ?,

                branch = ?,

                tenth_cgpa = ?,

                twelfth_cgpa = ?,

                be_cgpa = ?,

                phone = ?,

                email = ?,

                updated_at = CURRENT_TIMESTAMP

            WHERE id = ?
            """,

            (
                full_name,
                college_name,
                degree,
                branch,
                tenth_cgpa,
                twelfth_cgpa,
                be_cgpa,
                phone,
                email,
                student_id
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


# ============================================================
# UPDATE VERIFICATION STATUS
# ============================================================

def update_verification_status(
    student_id,
    email_verified=None,
    phone_verified=None
):
    """
    Update Email / Phone verification status.

    Existing values are preserved when
    None is supplied.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                email_verified,
                phone_verified

            FROM students

            WHERE id = ?
            """,

            (
                student_id,
            )
        )

        student = cursor.fetchone()

        if not student:

            return False

        # ----------------------------------------------------
        # Preserve existing values
        # ----------------------------------------------------

        current_email_verified = (
            student["email_verified"]
        )

        current_phone_verified = (
            student["phone_verified"]
        )

        if email_verified is None:

            email_verified = (
                current_email_verified
            )

        if phone_verified is None:

            phone_verified = (
                current_phone_verified
            )

        # ----------------------------------------------------
        # Update
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE students

            SET

                email_verified = ?,

                phone_verified = ?,

                updated_at = CURRENT_TIMESTAMP

            WHERE id = ?
            """,

            (
                int(email_verified),
                int(phone_verified),
                student_id
            )
        )

        connection.commit()

        return True

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


# ============================================================
# UPDATE APPROVAL STATUS
# ============================================================

def update_approval_status(
    student_id,
    status,
    rejection_reason=None
):
    """
    Update student approval status.

    Allowed:

        PENDING
        APPROVED
        REJECTED
    """

    allowed_statuses = [
        "PENDING",
        "APPROVED",
        "REJECTED"
    ]

    status = status.upper()

    if status not in allowed_statuses:

        raise ValueError(
            "Invalid approval status."
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE students

            SET

                approval_status = ?,

                rejection_reason = ?,

                updated_at = CURRENT_TIMESTAMP

            WHERE id = ?
            """,

            (
                status,
                rejection_reason,
                student_id
            )
        )

        connection.commit()

        return cursor.rowcount > 0

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


# ============================================================
# GET ALL STUDENTS
# ============================================================

def get_all_students():
    """
    Return all students.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM students
            ORDER BY created_at DESC
            """
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# GET STUDENTS BY STATUS
# ============================================================

def get_students_by_status(
    status
):
    """
    Return students by approval status.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM students

            WHERE approval_status = ?

            ORDER BY created_at DESC
            """,

            (
                status.upper(),
            )
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# STUDENT COUNTS
# ============================================================

def student_counts():
    """
    Return dashboard statistics.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Total
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM students
            """
        )

        total = cursor.fetchone()[0]

        # ----------------------------------------------------
        # Approved
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM students
            WHERE approval_status = 'APPROVED'
            """
        )

        approved = cursor.fetchone()[0]

        # ----------------------------------------------------
        # Pending
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM students
            WHERE approval_status = 'PENDING'
            """
        )

        pending = cursor.fetchone()[0]

        # ----------------------------------------------------
        # Rejected
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM students
            WHERE approval_status = 'REJECTED'
            """
        )

        rejected = cursor.fetchone()[0]

        # ----------------------------------------------------
        # Email Verified
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM students
            WHERE email_verified = 1
            """
        )

        email_verified = cursor.fetchone()[0]

        # ----------------------------------------------------
        # Phone Verified
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM students
            WHERE phone_verified = 1
            """
        )

        phone_verified = cursor.fetchone()[0]

        return {

            "total": total,

            "approved": approved,

            "pending": pending,

            "rejected": rejected,

            "email_verified": email_verified,

            "phone_verified": phone_verified

        }

    finally:

        connection.close()


# ============================================================
# INSERT SAMPLE STUDENTS
# ============================================================

def insert_sample_students(connection):
    """
    Insert sample students only when they do not
    already exist.

    Existing student records are never deleted
    or modified.

    Returns:
        Number of students inserted.
    """

    sample_students = [

        # ====================================================
        # RAHUL
        # ====================================================

        {
            "full_name":
                "Rahul Sharma",

            "college_name":
                "East West Institute of Technology",

            "degree":
                "B.E",

            "branch":
                "CSE",

            "tenth_cgpa":
                9.2,

            "twelfth_cgpa":
                9.0,

            "be_cgpa":
                8.7,

            "phone":
                "+919900000001",

            "email":
                "rahul.sharma@example.com",

            "password":
                "Student@123",

            "email_verified":
                1,

            "phone_verified":
                1,

            "approval_status":
                "APPROVED",

            "rejection_reason":
                None,
        },

        # ====================================================
        # PRIYA
        # ====================================================

        {
            "full_name":
                "Priya Kumar",

            "college_name":
                "Cambridge Institute of Technology",

            "degree":
                "B.E",

            "branch":
                "ISE",

            "tenth_cgpa":
                9.5,

            "twelfth_cgpa":
                9.2,

            "be_cgpa":
                8.9,

            "phone":
                "+919900000002",

            "email":
                "priya.kumar@example.com",

            "password":
                "Student@123",

            "email_verified":
                1,

            "phone_verified":
                1,

            "approval_status":
                "PENDING",

            "rejection_reason":
                None,
        },

        # ====================================================
        # ARJUN
        # ====================================================

        {
            "full_name":
                "Arjun Rao",

            "college_name":
                "Sapthagiri College of Engineering",

            "degree":
                "B.E",

            "branch":
                "AI&DS",

            "tenth_cgpa":
                8.8,

            "twelfth_cgpa":
                8.6,

            "be_cgpa":
                7.9,

            "phone":
                "+919900000003",

            "email":
                "arjun.rao@example.com",

            "password":
                "Student@123",

            "email_verified":
                1,

            "phone_verified":
                1,

            "approval_status":
                "REJECTED",

            "rejection_reason":
                "Academic details require review.",
        },

        # ====================================================
        # SNEHA
        # ====================================================

        {
            "full_name":
                "Sneha Reddy",

            "college_name":
                "Atria Institute of Technology",

            "degree":
                "B.E",

            "branch":
                "ECE",

            "tenth_cgpa":
                9.1,

            "twelfth_cgpa":
                8.9,

            "be_cgpa":
                8.3,

            "phone":
                "+919900000004",

            "email":
                "sneha.reddy@example.com",

            "password":
                "Student@123",

            "email_verified":
                1,

            "phone_verified":
                0,

            "approval_status":
                "PENDING",

            "rejection_reason":
                None,
        },

        # ====================================================
        # VIVEK
        # ====================================================

        {
            "full_name":
                "Vivek Kumar",

            "college_name":
                "AMC Engineering College",

            "degree":
                "B.E",

            "branch":
                "ISE",

            "tenth_cgpa":
                8.7,

            "twelfth_cgpa":
                8.5,

            "be_cgpa":
                8.1,

            "phone":
                "+919900000005",

            "email":
                "vivek.kumar@example.com",

            "password":
                "Student@123",

            "email_verified":
                0,

            "phone_verified":
                1,

            "approval_status":
                "PENDING",

            "rejection_reason":
                None,
        },

    ]

    cursor = connection.cursor()

    inserted = 0

    # ========================================================
    # INSERT EACH STUDENT
    # ========================================================

    for student in sample_students:

        # ----------------------------------------------------
        # CHECK EMAIL
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE LOWER(email) = LOWER(?)
            LIMIT 1
            """,

            (
                student["email"],
            )
        )

        if cursor.fetchone():

            continue

        # ----------------------------------------------------
        # CHECK PHONE
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE phone = ?
            LIMIT 1
            """,

            (
                student["phone"],
            )
        )

        if cursor.fetchone():

            continue

        # ----------------------------------------------------
        # HASH PASSWORD
        # ----------------------------------------------------

        password_hash = hash_sample_password(
            student["password"]
        )

        # ----------------------------------------------------
        # INSERT
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO students (

                full_name,

                college_name,

                degree,

                branch,

                tenth_cgpa,

                twelfth_cgpa,

                be_cgpa,

                phone,

                email,

                password_hash,

                email_verified,

                phone_verified,

                approval_status,

                rejection_reason

            )

            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?
            )
            """,

            (
                student["full_name"],
                student["college_name"],
                student["degree"],
                student["branch"],
                student["tenth_cgpa"],
                student["twelfth_cgpa"],
                student["be_cgpa"],
                student["phone"],
                student["email"],
                password_hash,
                student["email_verified"],
                student["phone_verified"],
                student["approval_status"],
                student["rejection_reason"],
            )
        )

        inserted += 1

    # ========================================================
    # COMMIT
    # ========================================================

    connection.commit()

    return inserted


# ============================================================
# DATABASE LOGIN DIAGNOSTIC
# ============================================================

def test_sample_login(
    email="rahul.sharma@example.com",
    password="Student@123"
):
    """
    Development/testing helper.

    Tests the database record and password hash
    without changing any data.

    Returns:

        {
            "student_found": True/False,
            "password_valid": True/False,
            "email_verified": True/False,
            "phone_verified": True/False,
            "approval_status": "...",
        }
    """

    student = get_student_by_email(
        email
    )

    if not student:

        return {
            "student_found": False,
            "password_valid": False,
            "email_verified": False,
            "phone_verified": False,
            "approval_status": None,
        }

    password_valid = verify_sample_password(
        password,
        student["password_hash"]
    )

    return {

        "student_found": True,

        "password_valid":
            password_valid,

        "email_verified":
            bool(student["email_verified"]),

        "phone_verified":
            bool(student["phone_verified"]),

        "approval_status":
            student["approval_status"],

    }


# ============================================================
# RESET DATABASE - DEVELOPMENT ONLY
# ============================================================

def reset_database():
    """
    WARNING:

    This deletes all student records.

    Use ONLY during development/testing.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DROP TABLE IF EXISTS students
            """
        )

        connection.commit()

    finally:

        connection.close()

    init_db()


# ============================================================
# END OF db.py
# ============================================================
