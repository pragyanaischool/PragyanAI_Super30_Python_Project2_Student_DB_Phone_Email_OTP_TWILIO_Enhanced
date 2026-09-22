# ============================================================
# PragyanAI Student Verification System
# pages/1_Student_Dashboard.py
# ============================================================

import streamlit as st
import pandas as pd

from auth import (
    initialize_session_state,
    is_student_logged_in,
    logout,
)

from db import (
    get_student_by_id,
    email_or_phone_exists,
    update_student_profile,
    update_verification_status,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Student Dashboard - PragyanAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# INITIALIZE SESSION
# ============================================================

initialize_session_state()


# ============================================================
# ACCESS CONTROL
# ============================================================

if not is_student_logged_in():

    st.warning(
        "🔐 Please login as a student to access the dashboard."
    )

    if st.button(
        "🏠 Go to Login",
        type="primary"
    ):
        st.switch_page("app.py")

    st.stop()


# ============================================================
# GET STUDENT ID
# ============================================================

student_id = st.session_state.get(
    "student_id"
)

if not student_id:

    st.error(
        "Student session is invalid. Please login again."
    )

    logout()

    if st.button(
        "🏠 Return to Login"
    ):
        st.switch_page("app.py")

    st.stop()


# ============================================================
# LOAD STUDENT
# ============================================================

student = get_student_by_id(student_id)


if not student:

    st.error(
        "Student record could not be found."
    )

    logout()

    if st.button(
        "🏠 Return to Login"
    ):
        st.switch_page("app.py")

    st.stop()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .dashboard-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1f4e79;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        font-size: 1.05rem;
        color: #666666;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f4e79;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .profile-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #dddddd;
        background-color: #fafafa;
        margin-bottom: 15px;
    }

    .status-approved {
        padding: 12px;
        border-radius: 10px;
        background-color: #e8f5e9;
        border: 1px solid #81c784;
    }

    .status-pending {
        padding: 12px;
        border-radius: 10px;
        background-color: #fff8e1;
        border: 1px solid #ffca28;
    }

    .status-rejected {
        padding: 12px;
        border-radius: 10px;
        background-color: #ffebee;
        border: 1px solid #ef5350;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🎓 PragyanAI")

    st.markdown("---")

    st.success("🎓 Student Portal")

    st.markdown(
        f"**Student ID:** {student['id']}"
    )

    st.markdown(
        f"**Name:** {student['full_name']}"
    )

    st.markdown(
        f"**Email:** {student['email']}"
    )

    st.markdown(
        f"**Phone:** {student['phone']}"
    )

    st.markdown("---")

    if st.button(
        "🏠 Home",
        use_container_width=True
    ):

        st.switch_page("app.py")

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        logout()

        st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">'
    '🎓 Student Dashboard'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Welcome to your PragyanAI Student Verification Portal.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# STUDENT STATUS VALUES
# ============================================================

email_verified = bool(
    student["email_verified"]
)

phone_verified = bool(
    student["phone_verified"]
)

approval_status = (
    student["approval_status"]
    or "PENDING"
).upper()


# ============================================================
# TOP METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "🎓 Student ID",
        student["id"]
    )


with col2:

    st.metric(
        "📧 Email",
        "Verified"
        if email_verified
        else "Not Verified"
    )


with col3:

    st.metric(
        "📱 Phone",
        "Verified"
        if phone_verified
        else "Not Verified"
    )


with col4:

    st.metric(
        "🛡️ Approval",
        approval_status
    )


st.markdown("---")


# ============================================================
# DASHBOARD TABS
# ============================================================

tab_profile, tab_edit, tab_verification, tab_approval = st.tabs(
    [
        "👤 My Profile",
        "✏️ Edit Profile",
        "🔐 Verification",
        "📋 Approval Status",
    ]
)


# ============================================================
# TAB 1 — MY PROFILE
# ============================================================

with tab_profile:

    st.markdown(
        '<div class="section-title">'
        '👤 My Profile'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Personal Information
    # --------------------------------------------------------

    st.markdown("### 👤 Personal Information")

    col1, col2 = st.columns(2)

    with col1:

        st.text_input(
            "Full Name",
            value=student["full_name"] or "",
            disabled=True,
            key="profile_full_name"
        )

        st.text_input(
            "College Name",
            value=student["college_name"] or "",
            disabled=True,
            key="profile_college_name"
        )

        st.text_input(
            "Degree",
            value=student["degree"] or "",
            disabled=True,
            key="profile_degree"
        )

        st.text_input(
            "Branch",
            value=student["branch"] or "",
            disabled=True,
            key="profile_branch"
        )

    with col2:

        st.text_input(
            "Phone Number",
            value=student["phone"] or "",
            disabled=True,
            key="profile_phone"
        )

        st.text_input(
            "Email Address",
            value=student["email"] or "",
            disabled=True,
            key="profile_email"
        )

        st.text_input(
            "Student ID",
            value=str(student["id"]),
            disabled=True,
            key="profile_student_id"
        )

        st.text_input(
            "Account Created",
            value=str(student["created_at"]),
            disabled=True,
            key="profile_created_at"
        )


    # --------------------------------------------------------
    # Academic Information
    # --------------------------------------------------------

    st.markdown("### 📚 Academic Information")

    academic_col1, academic_col2, academic_col3 = st.columns(3)

    with academic_col1:

        st.metric(
            "10th CGPA",
            f"{student['tenth_cgpa']:.2f}"
            if student["tenth_cgpa"] is not None
            else "N/A"
        )

    with academic_col2:

        st.metric(
            "12th CGPA",
            f"{student['twelfth_cgpa']:.2f}"
            if student["twelfth_cgpa"] is not None
            else "N/A"
        )

    with academic_col3:

        st.metric(
            "B.E / B.Tech CGPA",
            f"{student['be_cgpa']:.2f}"
            if student["be_cgpa"] is not None
            else "N/A"
        )


# ============================================================
# TAB 2 — EDIT PROFILE
# ============================================================

with tab_edit:

    st.markdown(
        '<div class="section-title">'
        '✏️ Edit Profile'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "You can update your profile information. "
        "If you change your email or phone number, "
        "that contact method will require verification again."
    )

    # --------------------------------------------------------
    # Current values
    # --------------------------------------------------------

    with st.form("edit_student_profile_form"):

        st.markdown("### 👤 Personal Information")

        col1, col2 = st.columns(2)

        with col1:

            edit_full_name = st.text_input(
                "Full Name *",
                value=student["full_name"] or "",
            )

            edit_college_name = st.text_input(
                "College Name *",
                value=student["college_name"] or "",
            )

            edit_degree = st.text_input(
                "Degree *",
                value=student["degree"] or "",
            )

            edit_branch = st.text_input(
                "Branch *",
                value=student["branch"] or "",
            )

        with col2:

            edit_email = st.text_input(
                "Email Address *",
                value=student["email"] or "",
            )

            edit_phone = st.text_input(
                "Phone Number *",
                value=student["phone"] or "",
            )

        st.markdown("### 📚 Academic Information")

        academic_col1, academic_col2, academic_col3 = st.columns(3)

        with academic_col1:

            edit_tenth_cgpa = st.number_input(
                "10th CGPA",
                min_value=0.0,
                max_value=10.0,
                value=float(
                    student["tenth_cgpa"] or 0.0
                ),
                step=0.1,
            )

        with academic_col2:

            edit_twelfth_cgpa = st.number_input(
                "12th CGPA",
                min_value=0.0,
                max_value=10.0,
                value=float(
                    student["twelfth_cgpa"] or 0.0
                ),
                step=0.1,
            )

        with academic_col3:

            edit_be_cgpa = st.number_input(
                "B.E / B.Tech CGPA",
                min_value=0.0,
                max_value=10.0,
                value=float(
                    student["be_cgpa"] or 0.0
                ),
                step=0.1,
            )

        st.markdown("---")

        update_button = st.form_submit_button(
            "💾 Save Profile Changes",
            type="primary",
            use_container_width=True
        )


    # --------------------------------------------------------
    # Process Update
    # --------------------------------------------------------

    if update_button:

        edit_full_name = edit_full_name.strip()
        edit_college_name = edit_college_name.strip()
        edit_degree = edit_degree.strip()
        edit_branch = edit_branch.strip()
        edit_email = edit_email.strip().lower()
        edit_phone = edit_phone.strip()

        # ====================================================
        # BASIC VALIDATION
        # ====================================================

        if not edit_full_name:

            st.error(
                "Full Name cannot be empty."
            )
            st.stop()

        if not edit_college_name:

            st.error(
                "College Name cannot be empty."
            )
            st.stop()

        if not edit_degree:

            st.error(
                "Degree cannot be empty."
            )
            st.stop()

        if not edit_branch:

            st.error(
                "Branch cannot be empty."
            )
            st.stop()

        if not edit_email:

            st.error(
                "Email cannot be empty."
            )
            st.stop()

        if not edit_phone:

            st.error(
                "Phone number cannot be empty."
            )
            st.stop()


        # ====================================================
        # CHECK DUPLICATE EMAIL / PHONE
        # ====================================================

        duplicate = email_or_phone_exists(
            edit_email,
            edit_phone,
            exclude_id=student["id"]
        )

        if duplicate:

            st.error(
                "The email address or phone number "
                "is already registered with another student."
            )

            st.stop()


        # ====================================================
        # DETECT CONTACT CHANGES
        # ====================================================

        email_changed = (
            edit_email !=
            str(student["email"]).strip().lower()
        )

        phone_changed = (
            edit_phone !=
            str(student["phone"]).strip()
        )


        # ====================================================
        # UPDATE DATABASE
        # ====================================================

        try:

            success = update_student_profile(
                student_id=student["id"],
                full_name=edit_full_name,
                college_name=edit_college_name,
                degree=edit_degree,
                branch=edit_branch,
                tenth_cgpa=edit_tenth_cgpa,
                twelfth_cgpa=edit_twelfth_cgpa,
                be_cgpa=edit_be_cgpa,
                phone=edit_phone,
                email=edit_email,
            )

            if success:

                # ------------------------------------------------
                # Reset verification if contact details changed
                # ------------------------------------------------

                if email_changed:

                    update_verification_status(
                        student["id"],
                        email_verified=0
                    )

                if phone_changed:

                    update_verification_status(
                        student["id"],
                        phone_verified=0
                    )


                # ------------------------------------------------
                # Update session information
                # ------------------------------------------------

                st.session_state.student_email = edit_email

                st.session_state.student_name = edit_full_name


                st.success(
                    "✅ Profile updated successfully."
                )


                if email_changed:

                    st.warning(
                        "📧 Your email address was changed. "
                        "Email verification is required again."
                    )

                if phone_changed:

                    st.warning(
                        "📱 Your phone number was changed. "
                        "Phone verification is required again."
                    )


                st.rerun()

            else:

                st.error(
                    "Unable to update profile."
                )

        except Exception as e:

            st.error(
                f"Profile update failed: {e}"
            )


# ============================================================
# TAB 3 — VERIFICATION
# ============================================================

with tab_verification:

    st.markdown(
        '<div class="section-title">'
        '🔐 Verification Status'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Your email and phone verification status is shown below."
    )

    # --------------------------------------------------------
    # Email Verification
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 📧 Email Verification")

        st.write(
            f"**Email:** {student['email']}"
        )

        if email_verified:

            st.success(
                "✅ Email Verified"
            )

        else:

            st.error(
                "❌ Email Not Verified"
            )

            st.warning(
                "Please contact the PragyanAI administrator "
                "if your email requires re-verification."
            )


    # --------------------------------------------------------
    # Phone Verification
    # --------------------------------------------------------

    with col2:

        st.markdown("### 📱 Phone Verification")

        st.write(
            f"**Phone:** {student['phone']}"
        )

        if phone_verified:

            st.success(
                "✅ Phone Verified"
            )

        else:

            st.error(
                "❌ Phone Not Verified"
            )

            st.warning(
                "Please contact the PragyanAI administrator "
                "if your phone requires re-verification."
            )


    # --------------------------------------------------------
    # Overall Verification
    # --------------------------------------------------------

    st.markdown("---")

    if email_verified and phone_verified:

        st.success(
            "🎉 Your Email and Phone are both verified."
        )

    elif email_verified:

        st.warning(
            "⚠️ Email is verified, but Phone verification "
            "is still pending."
        )

    elif phone_verified:

        st.warning(
            "⚠️ Phone is verified, but Email verification "
            "is still pending."
        )

    else:

        st.error(
            "❌ Email and Phone verification are both pending."
        )


# ============================================================
# TAB 4 — APPROVAL STATUS
# ============================================================

with tab_approval:

    st.markdown(
        '<div class="section-title">'
        '📋 Approval Status'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # APPROVED
    # --------------------------------------------------------

    if approval_status == "APPROVED":

        st.markdown(
            """
            <div class="status-approved">
                <h3>✅ Application Approved</h3>
                <p>
                Your student application has been approved
                by the PragyanAI administrator.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # PENDING
    # --------------------------------------------------------

    elif approval_status == "PENDING":

        st.markdown(
            """
            <div class="status-pending">
                <h3>⏳ Application Pending</h3>
                <p>
                Your application has been submitted and is
                waiting for administrator approval.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.info(
            "Please ensure that your profile information "
            "and verification details are complete."
        )


    # --------------------------------------------------------
    # REJECTED
    # --------------------------------------------------------

    elif approval_status == "REJECTED":

        st.markdown(
            """
            <div class="status-rejected">
                <h3>❌ Application Rejected</h3>
                <p>
                Your application has been rejected by the
                administrator.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        rejection_reason = student["rejection_reason"]

        if rejection_reason:

            st.markdown(
                "### 📝 Rejection Reason"
            )

            st.error(
                rejection_reason
            )

        else:

            st.warning(
                "No rejection reason has been provided."
            )


    # --------------------------------------------------------
    # UNKNOWN STATUS
    # --------------------------------------------------------

    else:

        st.warning(
            f"Unknown approval status: {approval_status}"
        )


    # --------------------------------------------------------
    # Verification prerequisite
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown(
        "### 🔐 Verification Summary"
    )

    verification_col1, verification_col2 = st.columns(2)

    with verification_col1:

        if email_verified:

            st.success(
                "📧 Email: Verified"
            )

        else:

            st.error(
                "📧 Email: Not Verified"
            )

    with verification_col2:

        if phone_verified:

            st.success(
                "📱 Phone: Verified"
            )

        else:

            st.error(
                "📱 Phone: Not Verified"
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "© PragyanAI — Student Verification System"
)

st.caption(
    f"Student ID: {student['id']} | "
    f"Account Status: {approval_status}"
)
