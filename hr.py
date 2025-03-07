import streamlit as st
from streamlit_option_menu import option_menu


def hr_view(auth_service):
    user = st.session_state.get("user", {})
    if not user:
        st.error("User information is missing. Please log in again.")
        st.stop()

    hr_id = user.get("id")
    full_name = user.get("name")
    email = user.get("email")

    with st.sidebar:
        selected = option_menu(
            menu_title="HR Menu",
            options=["Post Job", "View Posted Jobs", "Evaluate Resumes", "Manage Profile", "Logout"],
            icons=["briefcase", "list", "clipboard-check", "person", "box-arrow-right"],
            menu_icon="people",
            default_index=0,
            orientation="vertical",
        )

    if selected == "Post Job":
        st.header("Post a New Job", divider="blue")
        st.info("This feature is coming soon! Stay tuned.")


    elif selected == "View Posted Jobs":
        st.header("View Posted Jobs", divider="blue")
        st.info("This feature is coming soon! Stay tuned.")

    elif selected == "Evaluate Resumes":
        st.header("Evaluate Candidates for a Job", divider="blue")
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
                        st.error("Invalid or already registered email.")
                    elif new_password and not auth_service.is_valid_password(new_password):
                        st.error(
                            "Password does not meet the criteria. "
                            "It must be at least 8 characters long, contain letters, numbers, and at least one special character."
                        )
                    else:
                        auth_service.update_user(
                            account_id=hr_id,
                            full_name=updated_full_name,
                            email=updated_email,
                            password=new_password if new_password else None,
                        )
                        st.session_state["user"]["name"] = updated_full_name
                        st.session_state["user"]["email"] = updated_email
                        st.success("Profile updated successfully.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    

    elif selected == "Logout":
        st.session_state.clear()
        st.rerun()