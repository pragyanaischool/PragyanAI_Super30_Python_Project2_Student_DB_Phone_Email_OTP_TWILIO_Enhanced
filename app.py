# ============================================================
# PragyanAI Student Verification System
# app.py
# ============================================================

import streamlit as st

from db import (
    init_db,
    create_student,
    get_student_by_email,
)

from auth import (
    initialize_session_state,
    student_login,
    admin_login,
    set_student_session,
    set_admin_session,
    is_logged_in,
    is_student_logged_in,
    is_admin_logged_in,
    logout,
)

from otp_service import (
    validate_email,
    validate_phone,
    generate_otp,
    otp_is_valid,
    send_email_otp,
    send_phone_otp,
    verify_phone_otp,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PragyanAI Student Verification",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# INITIALIZE DATABASE & SESSION
# ============================================================

init_db()
initialize_session_state()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #1f4e79;
        margin-bottom: 0.2rem;
    }

    .subtitle {
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

    .success-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #e8f5e9;
        border: 1px solid #81c784;
        margin: 10px 0;
    }

    .info-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #e3f2fd;
        border: 1px solid #64b5f6;
        margin: 10px 0;
    }

    .warning-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #fff8e1;
        border: 1px solid #ffca28;
        margin: 10px 0;
    }

    .danger-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #ffebee;
        border: 1px solid #ef5350;
        margin: 10px 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("##  PragyanAI")

    st.markdown("---")

    if is_student_logged_in():

        st.success(" Student Logged In")

        student_name = st.session_state.get(
            "student_name",
            "Student"
        )

        student_email = st.session_state.get(
            "student_email",
            ""
        )

        st.write(f"**Name:** {student_name}")
        st.write(f"**Email:** {student_email}")

        st.markdown("---")

        if st.button(
            " Student Dashboard",
            use_container_width=True
        ):
            st.switch_page(
                "pages/1_Student_Dashboard.py"
            )

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):
            logout()
            st.rerun()

    elif is_admin_logged_in():

        st.success(" Admin Logged In")

        st.markdown("---")

        if st.button(
            " Admin Dashboard",
            use_container_width=True
        ):
            st.switch_page(
                "pages/2_Admin_Dashboard.py"
            )

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):
            logout()
            st.rerun()

    else:

        st.info("Please login or create an account.")

        st.markdown("---")

        st.markdown(
            """
            **PragyanAI Student Verification**

            Secure student registration and
            verification platform.

            **Features**

            - 1. Student Registration
            - 2. Email OTP Verification
            - 3. Phone OTP Verification
            - 4. Secure Login
            - 5. Admin Approval
            - 6. Student Dashboard
            """
        )


# ============================================================
# IF STUDENT IS ALREADY LOGGED IN
# ============================================================

if is_student_logged_in():

    st.markdown(
        '<div class="main-title"> Student Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Welcome to the PragyanAI Student Verification Portal.'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "You are already logged in as a student. "
        "Use the Student Dashboard from the sidebar."
    )

    if st.button(
        "Open Student Dashboard",
        type="primary"
    ):
        st.switch_page(
            "pages/1_Student_Dashboard.py"
        )

    st.stop()


# ============================================================
# IF ADMIN IS ALREADY LOGGED IN
# ============================================================

if is_admin_logged_in():

    st.markdown(
        '<div class="main-title"> Admin Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Manage PragyanAI student verification and approvals.'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "You are already logged in as an administrator."
    )

    if st.button(
        " Open Admin Dashboard",
        type="primary"
    ):
        st.switch_page(
            "pages/2_Admin_Dashboard.py"
        )

    st.stop()


# ============================================================
# HOME PAGE
# ============================================================

st.markdown(
    '<div class="main-title">'
    ' PragyanAI Student Verification'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Student Registration • Email Verification • Phone Verification '
    '• Secure Login • Admin Approval'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# HOME INFORMATION
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🎓 Student Registration",
        "Available"
    )

with col2:
    st.metric(
        "📧 Email Verification",
        "OTP"
    )

with col3:
    st.metric(
        "📱 Phone Verification",
        "OTP"
    )

with col4:
    st.metric(
        "🛡️ Admin Approval",
        "Required"
    )


st.markdown("---")


# ============================================================
# MAIN TABS
# ============================================================

tab_login, tab_register, tab_admin = st.tabs(
    [
        "🎓 Student Login",
        "📝 Create Student Account",
        "🛡️ Admin Login",
    ]
)


# ============================================================
# TAB 1 — STUDENT LOGIN
# ============================================================

with tab_login:

    st.markdown(
        '<div class="section-title">'
        '🎓 Student Login'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Login using your registered email address and password."
    )

    with st.form("student_login_form"):

        login_email = st.text_input(
            "📧 Email Address",
            placeholder="student@example.com"
        )

        login_password = st.text_input(
            "🔐 Password",
            type="password",
            placeholder="Enter your password"
        )

        login_button = st.form_submit_button(
            "🔐 Login",
            type="primary",
            use_container_width=True
        )

    if login_button:

        login_email = login_email.strip().lower()

        if not login_email:
            st.error("Please enter your email address.")

        elif not login_password:
            st.error("Please enter your password.")

        else:

            success, message, student = student_login(
                login_email,
                login_password,
                None
            )

            if success:

                # ------------------------------------------------
                # Verify Email and Phone before login
                # ------------------------------------------------

                if not student["email_verified"]:
                    st.error(
                        "📧 Your email address is not verified."
                    )

                elif not student["phone_verified"]:
                    st.error(
                        "📱 Your phone number is not verified."
                    )

                else:

                    set_student_session(student)

                    st.success(
                        "✅ Login successful. "
                        "Opening Student Dashboard..."
                    )

                    st.switch_page(
                        "pages/1_🎓_Student_Dashboard.py"
                    )

            else:

                st.error(message)


# ============================================================
# TAB 2 — CREATE STUDENT ACCOUNT
# ============================================================

with tab_register:

    st.markdown(
        '<div class="section-title">'
        '📝 Create Student Account'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Complete your profile and verify both your email "
        "and phone number using OTP."
    )

    # ========================================================
    # PERSONAL INFORMATION
    # ========================================================

    st.markdown("### 👤 Personal Information")

    col1, col2 = st.columns(2)

    with col1:

        full_name = st.text_input(
            "Full Name *",
            placeholder="Rahul Sharma",
            key="registration_full_name"
        )

        college_name = st.text_input(
            "College Name *",
            placeholder="East West Institute of Technology",
            key="registration_college"
        )

        degree = st.text_input(
            "Degree *",
            placeholder="B.E",
            key="registration_degree"
        )

        branch = st.text_input(
            "Branch *",
            placeholder="Computer Science and Engineering",
            key="registration_branch"
        )

    with col2:

        phone = st.text_input(
            "📱 Phone Number *",
            placeholder="+919900000001",
            key="registration_phone"
        )

        email = st.text_input(
            "📧 Email Address *",
            placeholder="student@example.com",
            key="registration_email"
        )

        password = st.text_input(
            "🔐 Password *",
            type="password",
            placeholder="Minimum 8 characters",
            key="registration_password"
        )

        confirm_password = st.text_input(
            "🔐 Confirm Password *",
            type="password",
            placeholder="Re-enter password",
            key="registration_confirm_password"
        )


    # ========================================================
    # ACADEMIC INFORMATION
    # ========================================================

    st.markdown("### 📚 Academic Information")

    col1, col2, col3 = st.columns(3)

    with col1:

        tenth_cgpa = st.number_input(
            "10th CGPA",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.1,
            key="registration_tenth"
        )

    with col2:

        twelfth_cgpa = st.number_input(
            "12th CGPA",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.1,
            key="registration_twelfth"
        )

    with col3:

        be_cgpa = st.number_input(
            "B.E / B.Tech CGPA",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.1,
            key="registration_be"
        )


    st.markdown("---")


    # ========================================================
    # EMAIL OTP
    # ========================================================

    st.markdown("### 📧 Email Verification")

    email_verified = st.session_state.get(
        "email_verified",
        False
    )

    if email_verified:

        st.success(
            "✅ Email address verified successfully."
        )

    else:

        email_col1, email_col2 = st.columns(
            [3, 1]
        )

        with email_col1:

            email_otp = st.text_input(
                "Enter Email OTP",
                max_chars=6,
                placeholder="6-digit OTP",
                key="registration_email_otp"
            )

        with email_col2:

            st.write("")

            send_email_button = st.button(
                "📧 Send Email OTP",
                use_container_width=True
            )

        if send_email_button:

            email_clean = email.strip().lower()

            valid_email, email_message = validate_email(
                email_clean
            )

            if not valid_email:

                st.error(email_message)

            else:

                # --------------------------------------------
                # Check if email already exists
                # --------------------------------------------

                existing_student = get_student_by_email(
                    email_clean
                )

                if existing_student:

                    st.error(
                        "An account with this email address "
                        "already exists. Please use another "
                        "email address or login."
                    )

                else:

                    try:

                        otp = generate_otp()

                        success, message = send_email_otp(
                            email_clean,
                            otp
                        )

                        if success:

                            st.session_state.email_otp = otp
                            st.session_state.email_otp_time = (
                                __import__("time").time()
                            )

                            st.session_state.registration_data = {
                                "email": email_clean
                            }

                            st.success(
                                "✅ Email OTP sent successfully."
                            )

                            st.info(
                                "Please check your email inbox "
                                "and enter the 6-digit OTP."
                            )

                        else:

                            st.error(message)

                    except Exception as e:

                        st.error(
                            f"Unable to send email OTP: {e}"
                        )


        # ----------------------------------------------------
        # Verify Email OTP
        # ----------------------------------------------------

        verify_email_button = st.button(
            "✅ Verify Email OTP",
            use_container_width=True
        )

        if verify_email_button:

            stored_otp = st.session_state.get(
                "email_otp"
            )

            otp_time = st.session_state.get(
                "email_otp_time"
            )

            if not stored_otp:

                st.error(
                    "Please request an Email OTP first."
                )

            elif not otp_is_valid(otp_time):

                st.error(
                    "⏰ OTP has expired. "
                    "Please request a new OTP."
                )

            elif email_otp.strip() != stored_otp:

                st.error(
                    "❌ Invalid Email OTP."
                )

            else:

                st.session_state.email_verified = True

                st.success(
                    "✅ Email verified successfully."
                )

                st.rerun()


    # ========================================================
    # PHONE OTP
    # ========================================================

    st.markdown("### 📱 Phone Verification")

    phone_verified = st.session_state.get(
        "phone_verified",
        False
    )

    if phone_verified:

        st.success(
            "✅ Phone number verified successfully."
        )

    else:

        phone_col1, phone_col2 = st.columns(
            [3, 1]
        )

        with phone_col1:

            phone_otp = st.text_input(
                "Enter Phone OTP",
                max_chars=10,
                placeholder="Enter OTP received on phone",
                key="registration_phone_otp"
            )

        with phone_col2:

            st.write("")

            send_phone_button = st.button(
                "📱 Send Phone OTP",
                use_container_width=True
            )

        if send_phone_button:

            phone_clean = phone.strip()

            valid_phone, phone_message = validate_phone(
                phone_clean
            )

            if not valid_phone:

                st.error(phone_message)

            else:

                # --------------------------------------------
                # Check if phone already exists
                # --------------------------------------------

                from db import get_student_by_phone

                existing_student = get_student_by_phone(
                    phone_clean
                )

                if existing_student:

                    st.error(
                        "An account with this phone number "
                        "already exists. Please use another "
                        "phone number or login."
                    )

                else:

                    try:

                        success, message = send_phone_otp(
                            phone_clean
                        )

                        if success:

                            st.session_state.phone_otp_sent = True
                            st.session_state.registration_data = {
                                **st.session_state.get(
                                    "registration_data",
                                    {}
                                ),
                                "phone": phone_clean,
                            }

                            st.success(
                                "✅ Phone OTP sent successfully."
                            )

                            st.info(
                                "Please check your phone for "
                                "the verification OTP."
                            )

                        else:

                            st.error(message)

                    except Exception as e:

                        st.error(
                            f"Unable to send phone OTP: {e}"
                        )


        # ----------------------------------------------------
        # Verify Phone OTP
        # ----------------------------------------------------

        verify_phone_button = st.button(
            "✅ Verify Phone OTP",
            use_container_width=True
        )

        if verify_phone_button:

            if not st.session_state.get(
                "phone_otp_sent",
                False
            ):

                st.error(
                    "Please request a Phone OTP first."
                )

            else:

                phone_clean = phone.strip()

                valid_phone, phone_message = validate_phone(
                    phone_clean
                )

                if not valid_phone:

                    st.error(phone_message)

                else:

                    try:

                        success, message = verify_phone_otp(
                            phone_clean,
                            phone_otp.strip()
                        )

                        if success:

                            st.session_state.phone_verified = True

                            st.success(
                                "✅ Phone number verified successfully."
                            )

                            st.rerun()

                        else:

                            st.error(message)

                    except Exception as e:

                        st.error(
                            f"Unable to verify phone OTP: {e}"
                        )


    # ========================================================
    # REGISTRATION
    # ========================================================

    st.markdown("---")

    both_verified = (
        st.session_state.get(
            "email_verified",
            False
        )
        and
        st.session_state.get(
            "phone_verified",
            False
        )
    )

    if both_verified:

        st.success(
            "✅ Email and Phone are both verified. "
            "You can now create your student account."
        )

    else:

        st.warning(
            "⚠️ Please verify both Email and Phone "
            "before creating your account."
        )


    # ========================================================
    # CREATE ACCOUNT BUTTON
    # ========================================================

    create_account_button = st.button(
        "🎓 Create Student Account",
        type="primary",
        use_container_width=True,
        disabled=not both_verified
    )


    if create_account_button:

        # ====================================================
        # VALIDATE BASIC INFORMATION
        # ====================================================

        if not full_name.strip():

            st.error(
                "Please enter your full name."
            )
            st.stop()

        if not college_name.strip():

            st.error(
                "Please enter your college name."
            )
            st.stop()

        if not degree.strip():

            st.error(
                "Please enter your degree."
            )
            st.stop()

        if not branch.strip():

            st.error(
                "Please enter your branch."
            )
            st.stop()

        if not phone.strip():

            st.error(
                "Please enter your phone number."
            )
            st.stop()

        if not email.strip():

            st.error(
                "Please enter your email address."
            )
            st.stop()


        # ====================================================
        # VALIDATE EMAIL
        # ====================================================

        email_clean = email.strip().lower()

        valid_email, email_message = validate_email(
            email_clean
        )

        if not valid_email:

            st.error(email_message)
            st.stop()


        # ====================================================
        # VALIDATE PHONE
        # ====================================================

        phone_clean = phone.strip()

        valid_phone, phone_message = validate_phone(
            phone_clean
        )

        if not valid_phone:

            st.error(phone_message)
            st.stop()


        # ====================================================
        # PASSWORD VALIDATION
        # ====================================================

        if not password:

            st.error(
                "Please enter a password."
            )
            st.stop()

        if password != confirm_password:

            st.error(
                "Passwords do not match."
            )
            st.stop()


        # ====================================================
        # CHECK EXISTING EMAIL / PHONE
        # ====================================================

        existing_email = get_student_by_email(
            email_clean
        )

        if existing_email:

            st.error(
                "A student account with this email "
                "already exists."
            )
            st.stop()


        from db import get_student_by_phone

        existing_phone = get_student_by_phone(
            phone_clean
        )

        if existing_phone:

            st.error(
                "A student account with this phone "
                "number already exists."
            )
            st.stop()


        # ====================================================
        # CREATE STUDENT
        # ====================================================

        try:

            student_id = create_student(
                full_name=full_name.strip(),
                college_name=college_name.strip(),
                degree=degree.strip(),
                branch=branch.strip(),
                tenth_cgpa=tenth_cgpa,
                twelfth_cgpa=twelfth_cgpa,
                be_cgpa=be_cgpa,
                phone=phone_clean,
                email=email_clean,
                password=password,
                email_verified=1,
                phone_verified=1,
            )

            if student_id:

                st.success(
                    "🎉 Student account created successfully!"
                )

                st.info(
                    f"Your Student ID is **{student_id}**"
                )

                st.success(
                    "You can now login using your email "
                    "and password."
                )

                # --------------------------------------------
                # Clear registration verification state
                # --------------------------------------------

                st.session_state.email_otp = None
                st.session_state.email_otp_time = None
                st.session_state.phone_otp_sent = False
                st.session_state.email_verified = False
                st.session_state.phone_verified = False
                st.session_state.registration_data = {}

            else:

                st.error(
                    "Unable to create student account."
                )

        except Exception as e:

            st.error(
                f"Registration failed: {e}"
            )


# ============================================================
# TAB 3 — ADMIN LOGIN
# ============================================================

with tab_admin:

    st.markdown(
        '<div class="section-title">'
        '🛡️ Admin Login'
        '</div>',
        unsafe_allow_html=True
    )

    st.warning(
        "This section is only for authorized PragyanAI administrators."
    )

    with st.form("admin_login_form"):

        admin_email = st.text_input(
            "📧 Admin Email",
            placeholder="admin@pragyanai.com"
        )

        admin_password = st.text_input(
            "🔐 Admin Password",
            type="password",
            placeholder="Enter admin password"
        )

        admin_login_button = st.form_submit_button(
            "🛡️ Admin Login",
            type="primary",
            use_container_width=True
        )


    if admin_login_button:

        admin_email = admin_email.strip().lower()

        if not admin_email:

            st.error(
                "Please enter admin email."
            )

        elif not admin_password:

            st.error(
                "Please enter admin password."
            )

        else:

            success, message = admin_login(
                admin_email,
                admin_password
            )

            if success:

                set_admin_session()

                st.success(
                    "✅ Admin login successful."
                )

                st.switch_page(
                    "pages/2_🛡️_Admin_Dashboard.py"
                )

            else:

                st.error(message)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "© PragyanAI — Student Verification System"
)

st.caption(
    "Secure Student Registration • Email OTP • Phone OTP "
    "• Admin Approval"
)

