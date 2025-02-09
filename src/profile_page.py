import streamlit as st
from database import update_user_profile

def profile_page():
    # Custom CSS for styling
    st.markdown(
        """
        <style>
        .custom-header {
            font-size: 36px;
            color: #4F8BF9;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        .custom-button {
            background-color: #4F8BF9;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .custom-button:hover {
            background-color: #3a6bbf;
        }
        .custom-input {
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            width: 100%;
        }
        .custom-textarea {
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            width: 100%;
            height: 100px;
        }
        .custom-divider {
            border-top: 2px solid #4F8BF9;
            margin: 20px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Page Header
    st.markdown('<div class="custom-header">User Profile</div>', unsafe_allow_html=True)

    # User Information Section
    st.markdown("### User Information")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://via.placeholder.com/150", caption="Profile Picture", width=150)
    with col2:
        st.write(f"**Username:** {st.session_state['username']}")
        if 'display_name' not in st.session_state:
            st.session_state['display_name'] = st.session_state['username']
        if 'bio' not in st.session_state:
            st.session_state['bio'] = "No bio yet."
        st.write(f"**Display Name:** {st.session_state['display_name']}")
        st.write(f"**Bio:** {st.session_state['bio']}")

    # Divider
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Change Display Name Section
    st.markdown("### Change Display Name")
    if st.button("Change Display Name", key="change_display_name"):
        st.session_state['show_display_name_input'] = True

    if 'show_display_name_input' in st.session_state and st.session_state['show_display_name_input']:
        new_display_name = st.text_input("Enter a new display name", st.session_state['display_name'], key="new_display_name")
        if st.button("Save Display Name", key="save_display_name"):
            if new_display_name.strip():
                # Update both session state and database
                st.session_state['display_name'] = new_display_name
                update_user_profile(st.session_state['username'], display_name=new_display_name)
                st.session_state['show_display_name_input'] = False
                st.success("Display name updated successfully!")
            else:
                st.error("Display name cannot be empty.")

    # Divider
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Change Bio Section
    st.markdown("### Change Bio")
    if st.button("Change Bio", key="change_bio"):
        st.session_state['show_bio_input'] = True

    if 'show_bio_input' in st.session_state and st.session_state['show_bio_input']:
        bio = st.text_area("Write something about yourself", st.session_state['bio'], key="new_bio")
        if st.button("Save Bio", key="save_bio"):
            # Update both session state and database
            st.session_state['bio'] = bio
            update_user_profile(st.session_state['username'], bio=bio)
            st.session_state['show_bio_input'] = False
            st.success("Bio updated successfully!")

    # Divider
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Back and Logout Buttons
    col3, col4 = st.columns([1, 1])
    with col3:
        if st.button("Back to Main Page", key="back_button"):
            st.session_state['page'] = 'main'
            st.rerun()
    with col4:
        if st.button("Logout", key="logout_button"):
            st.session_state.clear()
            st.rerun() 