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
#
# ============================================================


import sqlite3
from pathlib import Path
import hashlib
import secrets


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "students.db"


# ============================================================
# PASSWORD CONFIGURATION FOR SAMPLE USERS
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

    Used for sample student accounts.
    """

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
# INITIALIZE DATABASE
# ============================================================

def init_db():
    """
    Create database and students table.

    Sample students are inserted automatically
    when the database is first created.
    """

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # CREATE STUDENTS TABLE
    # --------------------------------------------------------

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

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()

    # --------------------------------------------------------
    # INSERT SAMPLE STUDENTS
    # --------------------------------------------------------

    insert_sample_students(
        connection
    )

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

    connection.close()

    return student_id


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

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    connection.close()

    if student:

        return dict(student)

    return None


# ============================================================
# GET STUDENT BY EMAIL
# ============================================================

def get_student_by_email(
    email
):
    """
    Get student using email.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE LOWER(email) = LOWER(?)
        """,
        (email.strip(),)
    )

    student = cursor.fetchone()

    connection.close()

    if student:

        return dict(student)

    return None


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

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE phone = ?
        """,
        (phone.strip(),)
    )

    student = cursor.fetchone()

    connection.close()

    if student:

        return dict(student)

    return None


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

    connection.close()

    return result is not None


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

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            email_verified,
            phone_verified

        FROM students

        WHERE id = ?
        """,

        (student_id,)
    )

    student = cursor.fetchone()

    if not student:

        connection.close()

        return False

    # --------------------------------------------------------
    # Preserve existing values when None
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

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

    connection.close()

    return True


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

    connection.close()


# ============================================================
# GET ALL STUDENTS
# ============================================================

def get_all_students():
    """
    Return all students.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *

        FROM students

        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


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

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# STUDENT COUNTS
# ============================================================

def student_counts():
    """
    Return dashboard statistics.
    """

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # Total
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM students
        """
    )

    total = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Approved
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM students

        WHERE approval_status = 'APPROVED'
        """
    )

    approved = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Pending
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM students

        WHERE approval_status = 'PENDING'
        """
    )

    pending = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Rejected
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM students

        WHERE approval_status = 'REJECTED'
        """
    )

    rejected = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Email Verified
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM students

        WHERE email_verified = 1
        """
    )

    email_verified = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Phone Verified
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)

        FROM students

        WHERE phone_verified = 1
        """
    )

    phone_verified = cursor.fetchone()[0]

    connection.close()

    return {

        "total": total,

        "approved": approved,

        "pending": pending,

        "rejected": rejected,

        "email_verified": email_verified,

        "phone_verified": phone_verified

    }


# ============================================================
# INSERT SAMPLE STUDENTS
# ============================================================

def insert_sample_students(
    connection
):
    """
    Insert sample students for testing.

    The function checks whether sample data
    already exists before inserting.

    Therefore:

        Running init_db()
        multiple times

    will NOT create duplicate
    sample students.
    """

    cursor = connection.cursor()

    # --------------------------------------------------------
    # Check whether students already exist
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM students
        """
    )

    count = cursor.fetchone()[0]

    if count > 0:

        return


    # ========================================================
    # SAMPLE PASSWORDS
    # ========================================================

    #
    # These are ONLY demonstration accounts.
    #
    # Student 1:
    #     Email:
    #     rahul.sharma@example.com
    #
    #     Password:
    #     Student@123
    #
    #
    # Student 2:
    #     Email:
    #     priya.kumar@example.com
    #
    #     Password:
    #     Student@123
    #
    #
    # Student 3:
    #     Email:
    #     arjun.rao@example.com
    #
    #     Password:
    #     Student@123
    #
    #
    # Student 4:
    #     Email:
    #     sneha.reddy@example.com
    #
    #     Password:
    #     Student@123
    #
    #
    # Student 5:
    #     Email:
    #     vivek.kumar@example.com
    #
    #     Password:
    #     Student@123
    #
    # ========================================================


    password_hash_1 = hash_sample_password(
        "Student@123"
    )

    password_hash_2 = hash_sample_password(
        "Student@123"
    )

    password_hash_3 = hash_sample_password(
        "Student@123"
    )

    password_hash_4 = hash_sample_password(
        "Student@123"
    )

    password_hash_5 = hash_sample_password(
        "Student@123"
    )


    # ========================================================
    # SAMPLE STUDENTS
    # ========================================================

    sample_students = [

        # ----------------------------------------------------
        # STUDENT 1
        # APPROVED
        # EMAIL + PHONE VERIFIED
        # ----------------------------------------------------

        (
            "Rahul Sharma",

            "East West Institute of Technology",

            "B.E",

            "Computer Science and Engineering",

            9.2,

            9.0,

            8.7,

            "+919900000001",

            "rahul.sharma@example.com",

            password_hash_1,

            1,

            1,

            "APPROVED",

            None
        ),


        # ----------------------------------------------------
        # STUDENT 2
        # PENDING
        # EMAIL + PHONE VERIFIED
        # ----------------------------------------------------

        (
            "Priya Kumar",

            "Cambridge Institute of Technology",

            "B.E",

            "Information Science and Engineering",

            9.5,

            9.2,

            8.9,

            "+919900000002",

            "priya.kumar@example.com",

            password_hash_2,

            1,

            1,

            "PENDING",

            None
        ),


        # ----------------------------------------------------
        # STUDENT 3
        # REJECTED
        # EMAIL + PHONE VERIFIED
        # ----------------------------------------------------

        (
            "Arjun Rao",

            "Sapthagiri College of Engineering",

            "B.E",

            "Artificial Intelligence and Data Science",

            8.8,

            8.6,

            7.9,

            "+919900000003",

            "arjun.rao@example.com",

            password_hash_3,

            1,

            1,

            "REJECTED",

            "Academic details require review."
        ),


        # ----------------------------------------------------
        # STUDENT 4
        # PENDING
        # EMAIL VERIFIED
        # PHONE NOT VERIFIED
        # ----------------------------------------------------

        (
            "Sneha Reddy",

            "Atria Institute of Technology",

            "B.E",

            "Electronics and Communication Engineering",

            9.1,

            8.9,

            8.3,

            "+919900000004",

            "sneha.reddy@example.com",

            password_hash_4,

            1,

            0,

            "PENDING",

            None
        ),


        # ----------------------------------------------------
        # STUDENT 5
        # PENDING
        # EMAIL NOT VERIFIED
        # PHONE VERIFIED
        # ----------------------------------------------------

        (
            "Vivek Kumar",

            "AMC Engineering College",

            "B.E",

            "Information Science and Engineering",

            8.7,

            8.5,

            8.1,

            "+919900000005",

            "vivek.kumar@example.com",

            password_hash_5,

            0,

            1,

            "PENDING",

            None
        )

    ]


    # ========================================================
    # INSERT
    # ========================================================

    cursor.executemany(
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

            ?, ?, ?, ?, ?, ?, ?,

            ?, ?, ?,

            ?, ?, ?, ?

        )
        """,

        sample_students
    )


    # ========================================================
    # COMMIT
    # ========================================================

    connection.commit()


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

    cursor = connection.cursor()

    cursor.execute(
        """
        DROP TABLE IF EXISTS students
        """
    )

    connection.commit()

    connection.close()

    init_db()


# ============================================================
# END OF db.py
# ============================================================
