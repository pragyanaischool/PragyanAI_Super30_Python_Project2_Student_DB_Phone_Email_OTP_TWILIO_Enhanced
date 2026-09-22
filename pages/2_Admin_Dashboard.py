# ============================================================
# PragyanAI Student Verification System
# pages/2_Admin_Dashboard.py
# ============================================================

import streamlit as st
import pandas as pd

from auth import (
    initialize_session_state,
    is_admin_logged_in,
    logout,
)

from db import (
    get_all_students,
    get_students_by_status,
    get_student_by_id,
    update_approval_status,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Admin Dashboard - PragyanAI",
    page_icon="🛡️",
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

if not is_admin_logged_in():

    st.warning(
        " Please login as an administrator to access "
        "the Admin Dashboard."
    )

    if st.button(
        " Go to Login",
        type="primary"
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

    .approved-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #e8f5e9;
        border: 1px solid #81c784;
    }

    .pending-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #fff8e1;
        border: 1px solid #ffca28;
    }

    .rejected-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #ffebee;
        border: 1px solid #ef5350;
    }

    .student-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #dddddd;
        background-color: #fafafa;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    
    st.image("PragyanAI_Transperent.png")
    
    st.markdown("##  PragyanAI")

    st.markdown("---")

    st.success(" Administrator")

    st.markdown(
        "**Student Verification Portal**"
    )

    st.markdown("---")

    if st.button(
        " Home",
        use_container_width=True
    ):

        st.switch_page("app.py")

    if st.button(
        " Refresh Dashboard",
        use_container_width=True
    ):

        st.rerun()

    if st.button(
        " Logout",
        use_container_width=True
    ):

        logout()

        st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">'
    ' Admin Dashboard'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Manage PragyanAI student registrations, verification '
    'and approval status.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# LOAD STUDENTS
# ============================================================

students = get_all_students()


# ============================================================
# CONVERT TO DATAFRAME
# ============================================================

if students:

    df = pd.DataFrame(
        [dict(student) for student in students]
    )

else:

    df = pd.DataFrame()


# ============================================================
# CALCULATE COUNTS
# ============================================================

if not df.empty:

    total_students = len(df)

    approved_count = len(
        df[
            df["approval_status"].str.upper()
            == "APPROVED"
        ]
    )

    pending_count = len(
        df[
            df["approval_status"].str.upper()
            == "PENDING"
        ]
    )

    rejected_count = len(
        df[
            df["approval_status"].str.upper()
            == "REJECTED"
        ]
    )

    email_verified_count = int(
        df["email_verified"].sum()
    )

    phone_verified_count = int(
        df["phone_verified"].sum()
    )

else:

    total_students = 0
    approved_count = 0
    pending_count = 0
    rejected_count = 0
    email_verified_count = 0
    phone_verified_count = 0


# ============================================================
# TOP METRICS
# ============================================================

st.markdown(
    "###  Student Overview"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        " Total Students",
        total_students
    )

with col2:

    st.metric(
        "✅ Approved",
        approved_count
    )

with col3:

    st.metric(
        " Yet to Approve",
        pending_count
    )

with col4:

    st.metric(
        "❌ Rejected",
        rejected_count
    )


col5, col6 = st.columns(2)

with col5:

    st.metric(
        " Email Verified",
        email_verified_count
    )

with col6:

    st.metric(
        " Phone Verified",
        phone_verified_count
    )


st.markdown("---")


# ============================================================
# NO STUDENTS
# ============================================================

if df.empty:

    st.info(
        "No students are currently registered."
    )

    st.stop()


# ============================================================
# FILTER SECTION
# ============================================================

st.markdown(
    '<div class="section-title">'
    ' Filter Students'
    '</div>',
    unsafe_allow_html=True
)


filter_col1, filter_col2, filter_col3 = st.columns(3)


# ============================================================
# APPROVAL FILTER
# ============================================================

with filter_col1:

    approval_filter = st.selectbox(
        "Approval Status",
        [
            "All",
            "APPROVED",
            "PENDING",
            "REJECTED",
        ]
    )


# ============================================================
# COLLEGE FILTER
# ============================================================

with filter_col2:

    college_values = sorted(
        df["college_name"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    college_filter = st.selectbox(
        "College",
        ["All"] + college_values
    )


# ============================================================
# BRANCH FILTER
# ============================================================

with filter_col3:

    branch_values = sorted(
        df["branch"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    branch_filter = st.selectbox(
        "Branch",
        ["All"] + branch_values
    )


filter_col4, filter_col5, filter_col6 = st.columns(3)


# ============================================================
# EMAIL VERIFICATION FILTER
# ============================================================

with filter_col4:

    email_filter = st.selectbox(
        "Email Verification",
        [
            "All",
            "Verified",
            "Not Verified",
        ]
    )


# ============================================================
# PHONE VERIFICATION FILTER
# ============================================================

with filter_col5:

    phone_filter = st.selectbox(
        "Phone Verification",
        [
            "All",
            "Verified",
            "Not Verified",
        ]
    )


# ============================================================
# SEARCH
# ============================================================

with filter_col6:

    search_text = st.text_input(
        " Search",
        placeholder="Name / Email / Phone"
    )


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()


# ------------------------------------------------------------
# Approval
# ------------------------------------------------------------

if approval_filter != "All":

    filtered_df = filtered_df[
        filtered_df["approval_status"]
        .fillna("")
        .astype(str)
        .str.upper()
        == approval_filter
    ]


# ------------------------------------------------------------
# College
# ------------------------------------------------------------

if college_filter != "All":

    filtered_df = filtered_df[
        filtered_df["college_name"]
        .fillna("")
        .astype(str)
        == college_filter
    ]


# ------------------------------------------------------------
# Branch
# ------------------------------------------------------------

if branch_filter != "All":

    filtered_df = filtered_df[
        filtered_df["branch"]
        .fillna("")
        .astype(str)
        == branch_filter
    ]


# ------------------------------------------------------------
# Email verification
# ------------------------------------------------------------

if email_filter == "Verified":

    filtered_df = filtered_df[
        filtered_df["email_verified"] == 1
    ]

elif email_filter == "Not Verified":

    filtered_df = filtered_df[
        filtered_df["email_verified"] == 0
    ]


# ------------------------------------------------------------
# Phone verification
# ------------------------------------------------------------

if phone_filter == "Verified":

    filtered_df = filtered_df[
        filtered_df["phone_verified"] == 1
    ]

elif phone_filter == "Not Verified":

    filtered_df = filtered_df[
        filtered_df["phone_verified"] == 0
    ]


# ------------------------------------------------------------
# Search
# ------------------------------------------------------------

if search_text.strip():

    search_value = search_text.strip().lower()

    search_mask = (
        filtered_df["full_name"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            search_value,
            na=False
        )
        |
        filtered_df["email"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            search_value,
            na=False
        )
        |
        filtered_df["phone"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            search_value,
            na=False
        )
    )

    filtered_df = filtered_df[
        search_mask
    ]


# ============================================================
# FILTER RESULT COUNT
# ============================================================

st.info(
    f"Showing **{len(filtered_df)}** student(s) "
    f"out of **{len(df)}**."
)


# ============================================================
# DISPLAY COLUMNS
# ============================================================

display_columns = [
    "id",
    "full_name",
    "college_name",
    "degree",
    "branch",
    "phone",
    "email",
    "email_verified",
    "phone_verified",
    "approval_status",
    "created_at",
]


available_columns = [
    column
    for column in display_columns
    if column in filtered_df.columns
]


display_df = filtered_df[
    available_columns
].copy()


# ============================================================
# MAKE DISPLAY FRIENDLY
# ============================================================

if "email_verified" in display_df.columns:

    display_df["email_verified"] = (
        display_df["email_verified"]
        .apply(
            lambda x:
            "✅ Verified"
            if int(x) == 1
            else "❌ Not Verified"
        )
    )


if "phone_verified" in display_df.columns:

    display_df["phone_verified"] = (
        display_df["phone_verified"]
        .apply(
            lambda x:
            "✅ Verified"
            if int(x) == 1
            else "❌ Not Verified"
        )
    )


if "approval_status" in display_df.columns:

    display_df["approval_status"] = (
        display_df["approval_status"]
        .fillna("PENDING")
        .astype(str)
        .str.upper()
    )


# ============================================================
# MAIN TABS
# ============================================================

tab_all, tab_approved, tab_pending, tab_rejected = st.tabs(
    [
        "1. All Students",
        "2. Approved",
        "3. Yet to Approve",
        "4. Rejected",
    ]
)


# ============================================================
# TAB — ALL STUDENTS
# ============================================================

with tab_all:

    st.markdown(
        "###  All Students"
    )

    if display_df.empty:

        st.info(
            "No students match the selected filters."
        )

    else:

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# TAB — APPROVED
# ============================================================

with tab_approved:

    st.markdown(
        "###  Approved Students"
    )

    approved_df = display_df[
        display_df["approval_status"]
        == "APPROVED"
    ]

    if approved_df.empty:

        st.info(
            "No approved students match the selected filters."
        )

    else:

        st.dataframe(
            approved_df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# TAB — PENDING
# ============================================================

with tab_pending:

    st.markdown(
        "###  Students Yet to Approve"
    )

    pending_df = display_df[
        display_df["approval_status"]
        == "PENDING"
    ]

    if pending_df.empty:

        st.info(
            "No pending students match the selected filters."
        )

    else:

        st.dataframe(
            pending_df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# TAB — REJECTED
# ============================================================

with tab_rejected:

    st.markdown(
        "###  Rejected Students"
    )

    rejected_df = display_df[
        display_df["approval_status"]
        == "REJECTED"
    ]

    if rejected_df.empty:

        st.info(
            "No rejected students match the selected filters."
        )

    else:

        st.dataframe(
            rejected_df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# CSV DOWNLOAD
# ============================================================

st.markdown("---")

st.markdown(
    "###  Export Student Data"
)

csv_df = filtered_df.copy()

csv_data = csv_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label=" Download Filtered Students CSV",
    data=csv_data,
    file_name="pragyanai_students.csv",
    mime="text/csv",
    use_container_width=True,
)


# ============================================================
# STUDENT MANAGEMENT
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">'
    ' Student Management'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# STUDENT SELECTION
# ============================================================

if filtered_df.empty:

    st.info(
        "No students are available for selection."
    )

    st.stop()


student_options = filtered_df[
    "id"
].tolist()


student_labels = {}

for _, row in filtered_df.iterrows():

    student_labels[
        int(row["id"])
    ] = (
        f"{row['id']} — "
        f"{row['full_name']} — "
        f"{row['email']}"
    )


selected_student_id = st.selectbox(
    "Select Student",
    options=student_options,
    format_func=lambda x:
        student_labels.get(
            int(x),
            str(x)
        )
)


# ============================================================
# LOAD SELECTED STUDENT
# ============================================================

selected_student = get_student_by_id(
    int(selected_student_id)
)


if not selected_student:

    st.error(
        "Selected student record could not be found."
    )

    st.stop()


# ============================================================
# STUDENT PROFILE
# ============================================================

st.markdown(
    "###  Student Profile"
)


profile_col1, profile_col2 = st.columns(2)


# ============================================================
# PERSONAL INFORMATION
# ============================================================

with profile_col1:

    st.markdown("#### Personal Information")

    st.write(
        f"**Student ID:** {selected_student['id']}"
    )

    st.write(
        f"**Full Name:** {selected_student['full_name']}"
    )

    st.write(
        f"**College:** {selected_student['college_name']}"
    )

    st.write(
        f"**Degree:** {selected_student['degree']}"
    )

    st.write(
        f"**Branch:** {selected_student['branch']}"
    )

    st.write(
        f"**Phone:** {selected_student['phone']}"
    )

    st.write(
        f"**Email:** {selected_student['email']}"
    )


# ============================================================
# ACADEMIC INFORMATION
# ============================================================

with profile_col2:

    st.markdown("#### Academic Information")

    tenth_value = selected_student["tenth_cgpa"]

    twelfth_value = selected_student["twelfth_cgpa"]

    be_value = selected_student["be_cgpa"]


    if tenth_value is not None:

        st.write(
            f"**10th CGPA:** {float(tenth_value):.2f}"
        )

    else:

        st.write(
            "**10th CGPA:** N/A"
        )


    if twelfth_value is not None:

        st.write(
            f"**12th CGPA:** {float(twelfth_value):.2f}"
        )

    else:

        st.write(
            "**12th CGPA:** N/A"
        )


    if be_value is not None:

        st.write(
            f"**B.E / B.Tech CGPA:** "
            f"{float(be_value):.2f}"
        )

    else:

        st.write(
            "**B.E / B.Tech CGPA:** N/A"
        )


    st.write(
        f"**Created:** {selected_student['created_at']}"
    )

    st.write(
        f"**Updated:** {selected_student['updated_at']}"
    )


# ============================================================
# VERIFICATION STATUS
# ============================================================

st.markdown("---")

st.markdown(
    "###  Verification Status"
)


verification_col1, verification_col2 = st.columns(2)


with verification_col1:

    if selected_student["email_verified"]:

        st.success(
            " Email Verified"
        )

    else:

        st.error(
            " Email Not Verified"
        )


with verification_col2:

    if selected_student["phone_verified"]:

        st.success(
            " Phone Verified"
        )

    else:

        st.error(
            " Phone Not Verified"
        )


# ============================================================
# APPROVAL STATUS
# ============================================================

current_status = (
    selected_student["approval_status"]
    or "PENDING"
).upper()


st.markdown("---")

st.markdown(
    "###  Current Approval Status"
)


if current_status == "APPROVED":

    st.success(
        "✅ APPROVED"
    )

elif current_status == "PENDING":

    st.warning(
        " PENDING"
    )

elif current_status == "REJECTED":

    st.error(
        " REJECTED"
    )

else:

    st.warning(
        f"Unknown status: {current_status}"
    )


# ============================================================
# REJECTION REASON
# ============================================================

if selected_student["rejection_reason"]:

    st.markdown(
        "####  Existing Rejection Reason"
    )

    st.info(
        selected_student["rejection_reason"]
    )


# ============================================================
# APPROVAL MANAGEMENT
# ============================================================

st.markdown("---")

st.markdown(
    "###  Manage Student Approval"
)


st.info(
    "A student can be marked **Approved** only after "
    "both Email and Phone verification are complete."
)


# ============================================================
# APPROVE
# ============================================================

action_col1, action_col2, action_col3 = st.columns(3)


with action_col1:

    approve_button = st.button(
        " Approve Student",
        type="primary",
        use_container_width=True
    )


# ============================================================
# SET PENDING
# ============================================================

with action_col2:

    pending_button = st.button(
        " Set Pending",
        use_container_width=True
    )


# ============================================================
# REJECT
# ============================================================

with action_col3:

    reject_button = st.button(
        " Reject Student",
        use_container_width=True
    )


# ============================================================
# APPROVE ACTION
# ============================================================

if approve_button:

    email_is_verified = bool(
        selected_student["email_verified"]
    )

    phone_is_verified = bool(
        selected_student["phone_verified"]
    )


    if not email_is_verified:

        st.error(
            "❌ Cannot approve this student because "
            "Email is not verified."
        )

    elif not phone_is_verified:

        st.error(
            "❌ Cannot approve this student because "
            "Phone is not verified."
        )

    else:

        try:

            success = update_approval_status(
                student_id=selected_student["id"],
                status="APPROVED",
                rejection_reason=None
            )

            if success:

                st.success(
                    f"✅ {selected_student['full_name']} "
                    "has been approved."
                )

                st.rerun()

            else:

                st.error(
                    "Unable to update approval status."
                )

        except Exception as e:

            st.error(
                f"Approval update failed: {e}"
            )


# ============================================================
# SET PENDING ACTION
# ============================================================

if pending_button:

    try:

        success = update_approval_status(
            student_id=selected_student["id"],
            status="PENDING",
            rejection_reason=None
        )

        if success:

            st.success(
                f" {selected_student['full_name']} "
                "has been moved to Pending."
            )

            st.rerun()

        else:

            st.error(
                "Unable to update approval status."
            )

    except Exception as e:

        st.error(
            f"Pending status update failed: {e}"
        )


# ============================================================
# REJECT ACTION
# ============================================================

if reject_button:

    st.markdown(
        "#### ❌ Reject Student"
    )

    st.warning(
        "Please provide a reason for rejection."
    )

    rejection_reason = st.text_area(
        "Rejection Reason",
        placeholder=(
            "Example: Academic details require review."
        ),
        key="admin_rejection_reason"
    )

    confirm_rejection = st.button(
        "Confirm Rejection",
        type="secondary",
        use_container_width=True
    )

    if confirm_rejection:

        if not rejection_reason.strip():

            st.error(
                "Please enter a rejection reason."
            )

        else:

            try:

                success = update_approval_status(
                    student_id=selected_student["id"],
                    status="REJECTED",
                    rejection_reason=(
                        rejection_reason.strip()
                    )
                )

                if success:

                    st.success(
                        f"❌ {selected_student['full_name']} "
                        "has been rejected."
                    )

                    st.rerun()

                else:

                    st.error(
                        "Unable to update rejection status."
                    )

            except Exception as e:

                st.error(
                    f"Rejection update failed: {e}"
                )


# ============================================================
# APPROVAL RULE SUMMARY
# ============================================================

st.markdown("---")

st.markdown(
    "###  Approval Rules"
)

rule_col1, rule_col2, rule_col3 = st.columns(3)


with rule_col1:

    st.markdown(
        """
        ** Email**

        Student must have a
        verified email address.
        """
    )


with rule_col2:

    st.markdown(
        """
        ** Phone**

        Student must have a
        verified phone number.
        """
    )


with rule_col3:

    st.markdown(
        """
        ** Approval**

        Admin can approve only
        after both verifications.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "© PragyanAI — Student Verification System"
)

st.caption(
    "Administrator Portal • Student Verification • "
    "Approval Management"
)
