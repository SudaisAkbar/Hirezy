import streamlit as st
from streamlit_option_menu import option_menu
from db import Database
from auth import AuthService
from admin import admin_view
from hr import hr_view
from user import user_view


db = Database()
auth_service = AuthService(db)

db.initialize()

st.set_page_config(page_title="HIREZY", page_icon=":briefcase:")

st.markdown(
    """
    <style>
    .st-emotion-cache-11qx4gg {
        display: none;
    }

    .st-emotion-cache-13ln4jf {
        max-width: 90rem;
        padding: 3rem 1rem 10rem;
    }

    .st-emotion-cache-12fmjuu {
        display: none;
    }

    .st-emotion-cache-1u2dcfn {
        display: none;
    }

    .st-emotion-cache-6awftf {
        display: none;
    }
    
    .st-emotion-cache-gi0tri {
        display: none;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "password_valid" not in st.session_state:
    st.session_state["password_valid"] = None
if "passwords_match" not in st.session_state:
    st.session_state["passwords_match"] = None
if "username_available" not in st.session_state:
    st.session_state["username_available"] = True
if "email_available" not in st.session_state:
    st.session_state["email_available"] = True


def validate_password():
    password = st.session_state.get("register_password", "")
    st.session_state.password_valid = AuthService.is_valid_password(password)

def validate_confirm_password():
    st.session_state["passwords_match"] = (
        st.session_state.get("register_password", "") == st.session_state.get("register_confirm_password", "")
    )

def check_username(username_key):
    username = st.session_state.get(username_key, "")
    st.session_state["username_available"] = not auth_service.check_username_exists(username)

def check_email(email_key, role="User"):
    email = st.session_state.get(email_key, "")

    if role == "HR":
        blocked_domains = ["gmail.com", "outlook.com", "hotmail.com", "yahoo.com"]
        domain = email.split("@")[-1] if "@" in email else ""

        if domain in blocked_domains:
            st.session_state["email_available"] = False
            
            return

    st.session_state["email_available"] = AuthService.is_valid_email(email) and not auth_service.check_email_exists(email)


if not st.session_state["logged_in"]:
    st.markdown(
        """
        <style>
        .st-emotion-cache-ocqkz7 {
            border-left: 5px solid #0068c9; /* Left border with specified color */
            border-top: none;
            border-right: none;
            border-bottom: none;
            border-radius: 10px;
            padding: 30px 30px 30px 30px;
            background-color: #f9f9f9;
            box-shadow: 2px 2px 10px rgba(0,104,201, 0.5); /* Shadow on other sides */
            gap: 0rem;
            height: 840px;
    
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    

    authcol1, authcol2 = st.columns([0.60, 0.40])
    with authcol1:
        st.image("static/auth.png", width=700, caption="Evaluate your Resume Securely")

    with authcol2:        
        tab_login, tab_register = st.tabs(["Login", "Register"])
    
        with tab_login:
            st.subheader("Login")
            login_identifier = st.text_input("Username or Email", key="login_identifier")
            password = st.text_input("Password", type="password", key="login_password")
    
            if st.button("Login", key="login_button", type="primary"):
                user = auth_service.authenticate_user(login_identifier, password)
                if user:
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = {
                        "id": user[0],
                        "name": user[1],
                        "username": user[2],
                        "email": user[3],
                        "role": user[4],
                    }
                    st.rerun()
                else:
                    st.error("Invalid username/email or password.")
    
    
        with tab_register:
            tab_register_user, tab_register_hr = st.tabs(["Register as User", "Register as HR"])
    
            with tab_register_user:
                st.subheader("Register as User")
                full_name = st.text_input("Full Name *", key="register_user_full_name")
                username = st.text_input("Username *", key="register_user_username", on_change=check_username, args=("register_user_username",))
                email = st.text_input("Email *", key="register_user_email", on_change=check_email, args=("register_user_email",))
                industry = st.selectbox("Industry *", ["Software", "Finance", "Healthcare", "Education"])
                password = st.text_input("Password *", type="password", key="register_user_password", on_change=validate_password)
                confirm_password = st.text_input("Confirm Password *", type="password", key="register_user_confirm_password", on_change=validate_confirm_password)
    
                if not st.session_state.get("username_available", True):
                    st.error("Username is already taken. Please choose another.")
                if not st.session_state.get("email_available", True):
                    st.error("Invalid or already registered email.")
        
                register_disabled = not (
                    st.session_state.get("username_available", True)
                    and st.session_state.get("email_available", True)
                )
    
                if st.button("Register as User", disabled=register_disabled, type="primary"):
                    try:
                        auth_service.register_user(full_name, username, email, password, industry, role_name="User")
                        st.success("User registration successful! You can now log in.")
                    except ValueError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")
    
            with tab_register_hr:
                st.subheader("Register as HR")
                full_name_hr = st.text_input("Full Name *", key="register_hr_full_name")
                username_hr = st.text_input("Username *", key="register_hr_username", on_change=check_username, args=("register_hr_username",))
                email_hr = st.text_input("Company Email *", key="register_hr_email", on_change=check_email, args=("register_hr_email", "HR"))  # Pass role as HR
                password_hr = st.text_input("Password *", type="password", key="register_hr_password", on_change=validate_password)
                confirm_password_hr = st.text_input("Confirm Password *", type="password", key="register_hr_confirm_password", on_change=validate_confirm_password)
            
                if not st.session_state.get("username_available", True):
                    st.error("Username is already taken. Please choose another.")
                if not st.session_state.get("email_available", True):
                    st.error("Invalid or already registered email. HR must register with a company email (No Gmail, Outlook, Yahoo, etc.).")
            
                register_disabled = not (
                    st.session_state.get("username_available", True)
                    and st.session_state.get("email_available", True)
                )
            
                if st.button("Register as HR", disabled=register_disabled, type="primary"):
                    try:
                        auth_service.register_user(full_name_hr, username_hr, email_hr, password_hr, None, role_name="HR")
                        st.success("HR registration successful! You can now log in.")
                    except ValueError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")
            

else:
    with st.sidebar:
        st.image("static/hirezy-logo.png")
        
    user = st.session_state.get("user", {})
    user_role = user.get("role", "")
    user_name = user.get("name", "")

    if not user_role:
        st.error("User role is missing. Please log in again.")
        st.stop()

    st.sidebar.header(f"Welcome, {user_name} ({user_role})")

    if user_role == "Admin":
        admin_view(auth_service)

    elif user_role == "HR":
        if "username" not in user:
            st.error("HR details are incomplete. Please log in again.")
            st.stop()
        hr_view(auth_service)

    elif user_role == "User":
        user_view(auth_service)