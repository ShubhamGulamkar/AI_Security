import streamlit as st
import requests

BASE_URL = "https://localhost:8000"

st.set_page_config(
    page_title="AI Security Portal",
    layout="wide"
)

st.title("AI Security Portal")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Register",
        "Login",
        "Upload Document",
        "Download Document",
        "Generate Summary"
    ]
)

if menu == "Register":

    st.header("Register")

    username = st.text_input("Username")
    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    role = st.selectbox(
        "Role",
        [
            "Doctor",
            "Admin",
            "Patient"
        ]
    )

    if st.button("Register"):

        payload = {
            "username": username,
            "email": email,
            "password": password,
            "role": role
        }

        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=payload,
            verify=False
        )

        st.write(response.json())

if menu == "Login":

    st.header("Login")

    username = st.text_input("Username")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": username,
                "password": password
            },
            verify=False
        )

        result = response.json()

        if response.status_code == 200:

            st.session_state["token"] = result["access_token"]

            st.success("Login Successful")

            st.code(result["access_token"])

        else:

            st.error(result)

if menu == "Upload Document":

    st.header("Upload Document")

    token = st.session_state.get("token")

    if not token:
        st.error("Login First")
        st.stop()

    file = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if st.button("Upload"):

        files = {
            "file": (
                file.name,
                file,
                "application/pdf"
            )
        }

        headers = {
            "Authorization":
            f"Bearer {token}"
        }

        response = requests.post(
            f"{BASE_URL}/auth/upload",
            files=files,
            headers=headers,
            verify=False
        )

        st.write(response.json())

if menu == "Download Document":

    token = st.session_state.get("token")

    if not token:
        st.error("Login First")
        st.stop()

    document_id = st.text_input(
        "Document ID"
    )

    if st.button("Download"):

        headers = {
            "Authorization":
            f"Bearer {token}"
        }

        response = requests.get(
            f"{BASE_URL}/auth/{document_id}",
            headers=headers,
            verify=False
        )

        if response.status_code == 200:

            st.download_button(
                "Download PDF",
                response.content,
                "document.pdf"
            )

        else:

            st.error(response.text)

if menu == "Generate Summary":

    st.header("Generate AI Summary")

    token = st.session_state.get("token")

    if not token:
        st.error("Login First")
        st.stop()

    document_id = st.text_input(
        "Document ID"
    )

    if st.button("Generate Summary"):

        headers = {
            "Authorization":
            f"Bearer {token}"
        }

        response = requests.post(
            f"{BASE_URL}/rag/summary/{document_id}",
            headers=headers,
            verify=False
        )

        if response.status_code == 200:

            result = response.json()

            st.success(
                "Summary Generated Successfully"
            )

            st.subheader(
                "AI Summary"
            )

            st.write("Full API Response:")
            st.json(result)

        else:

            st.error(
                response.text
            )