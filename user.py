import streamlit as st
from streamlit_option_menu import option_menu


def user_view(auth_service):
    user = st.session_state.get("user", {})
    if not user:
        st.error("User information is missing. Please log in again.")
        st.stop()

    user_id = user.get("id")
    full_name = user.get("name")
    email = user.get("email")

    with st.sidebar:
        selected = option_menu(
            menu_title="User Menu",
            options=["Upload CV", "Jobs", "View Applied Jobs", "View Messages", "Chatbot", "ATS Evaluation", "CV Builder", "Manage Profile", "Logout"],
            icons=["upload", "briefcase", "list", "envelope", "chat-dots", "search", "file-text",  "person", "box-arrow-right"],
            menu_icon="menu-button",
            default_index=0,
            orientation="vertical",
        )


    if selected == "Upload CV":
        st.header("Upload CV", divider="blue")
        st.info("This feature is coming soon! Stay tuned.")

    elif selected == "Jobs":
        st.header("Available Jobs", divider="blue")
        st.info("This feature is coming soon! Stay tuned.")

    elif selected == "View Applied Jobs":
        st.header("Your Applied Jobs", divider="blue")
        st.info("This feature is coming soon! Stay tuned.")

    elif selected == "Chatbot":
        st.header("Chat with Your CV", divider="blue")
        st.info("This feature is coming soon! Stay tuned.")

    elif selected == "ATS Evaluation":
        st.header("ATS Evaluation of Your CV", divider="blue")
        st.info("This feature is coming soon! Stay tuned.")

    elif selected == "View Messages":
        st.header("Your Hiring Messages", divider="blue")
        st.info("This feature is coming soon! Stay tuned.")

    elif selected == "Manage Profile":
        manageprofile_col1, manageprofile_col2 = st.columns([0.30, 0.70])
        with manageprofile_col1:
            st.image("static/manageprofile.png", width=400)

        with manageprofile_col2:
            st.header("Manage Your Profile", divider="blue")
            try:
                updated_full_name = st.text_input("Full Name", value=full_name, key="profile_full_name")
                updated_email = st.text_input("Email", value=email, key="profile_email")
                new_password = st.text_input("New Password (optional)", type="password", key="profile_password")
    
                if st.button("Save Changes"):
                    if not updated_full_name or not updated_email:
                        st.warning("Full Name and Email cannot be empty.")
                    elif not auth_service.is_valid_email(updated_email):
                        st.error("Invalid email format. Please enter a valid email.")
                    elif new_password and not auth_service.is_valid_password(new_password):
                        st.error(
                            "Password does not meet the criteria. "
                            "It must be at least 8 characters long, contain letters, numbers, and at least one special character."
                        )
                    else:
                        auth_service.update_user(
                            account_id=user_id,
                            full_name=updated_full_name,
                            email=updated_email,
                            password=new_password if new_password else None,
                        )
                        st.session_state["user"]["name"] = updated_full_name
                        st.session_state["user"]["email"] = updated_email
                        st.success("Profile updated successfully.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

    elif selected == "CV Builder":
        st.header("Build Your CV", divider="blue")
        st.info("This feature is coming soon! Stay tuned.")

    elif selected == "Logout":
        st.session_state.clear()
        st.rerun()