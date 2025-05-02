import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# Fetching the key securely from the secrets.toml file
KEY = st.secrets["general"]["FERNET_KEY"]
cipher = Fernet(KEY)

# In-memory data storage (simulating a database)
if "stored_data" not in st.session_state:
    st.session_state.stored_data = {}

if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

# Function to hash the passkey (SHA-256)
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Encrypt text
def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()

# Decrypt text
def decrypt_data(encrypted_text, passkey):
    hashed_passkey = hash_passkey(passkey)

    for enc, value in st.session_state.stored_data.items():
        if value["encrypted_text"] == encrypted_text and value["passkey"] == hashed_passkey:
            st.session_state.failed_attempts = 0  # reset on success
            return cipher.decrypt(encrypted_text.encode()).decode()

    st.session_state.failed_attempts += 1
    return None

# UI Title
st.title("🔐 Secure Data Encryption System")

# Sidebar Navigation
menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.sidebar.selectbox("Navigation", menu)

# Home
if choice == "Home":
    st.subheader("🏠 Welcome to the Secure Data System")
    st.write("You can store and retrieve your data securely using a passkey.")

# Store Data
elif choice == "Store Data":
    st.subheader("📦 Store Data Securely")
    user_data = st.text_area("Enter the data you want to store:")
    passkey = st.text_input("Enter a secret passkey:", type="password")

    if st.button("Encrypt & Save"):
        if user_data and passkey:
            encrypted_text = encrypt_data(user_data)
            hashed_pass = hash_passkey(passkey)
            st.session_state.stored_data[encrypted_text] = {
                "encrypted_text": encrypted_text,
                "passkey": hashed_pass
            }
            st.success("✅ Data encrypted and stored successfully!")
            st.text_area("🔒 Encrypted Text (copy this to retrieve):", value=encrypted_text, height=100)
        else:
            st.error("⚠️ Please fill both fields.")

# Retrieve Data
elif choice == "Retrieve Data":
    st.subheader("🔓 Retrieve Encrypted Data")

    if st.session_state.failed_attempts >= 3:
        st.warning("🚫 Too many failed attempts. Please log in to continue.")
        st.stop()

    if st.session_state.stored_data:
        selected = st.selectbox("Select Encrypted Text", list(st.session_state.stored_data.keys()))
    else:
        selected = st.text_area("Paste Encrypted Text:")

    passkey = st.text_input("Enter your passkey:", type="password")

    if st.button("Decrypt"):
        if selected and passkey:
            result = decrypt_data(selected, passkey)
            if result:
                st.success(f"✅ Decrypted Data: {result}")
            else:
                attempts_left = 3 - st.session_state.failed_attempts
                st.error(f"❌ Incorrect passkey. Attempts left: {attempts_left}")
        else:
            st.error("⚠️ Please provide both encrypted text and passkey.")

# Login (Only shown when needed)
elif choice == "Login":
    st.subheader("🔐 Login Required")
    login_password = st.text_input("Enter master password:", type="password")

    if st.button("Login"):
        if login_password.strip() == "admin123":
            st.session_state.failed_attempts = 0
            st.success("✅ Reauthorized! You can now try again.")
        else:
            st.error("❌ Incorrect password.")
