from huggingface_hub import InferenceClient
import streamlit as st
import os
from dotenv import load_dotenv
from types import SimpleNamespace
load_dotenv()


hf_token = os.getenv("HF_TOKEN")

st.set_page_config(page_title="My First AI Model", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# # --- DEBUGGING AUTHENTICATION STATE ---
# if hasattr(st, "user"):
#     print("\n" + "="*50)
#     print("🤖 AUTH STATE DEBUGGER")
#     print(f"   st.user object: {st.user}")
#     print(f"   is_logged_in: {getattr(st.user, 'is_logged_in', False)}")
#     try:
#         print(f"   email: {getattr(st.user, 'email', None) or st.user.get('email', None)}")
#     except Exception as e:
#         print(f"   error reading email: {e}")
#     print("="*50 + "\n")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "user" not in st.session_state:
    st.session_state.user = ""
if "assistant" not in st.session_state:
    st.session_state.assistant = ""
if "temp_msg" not in st.session_state:
    st.session_state.temp_msg = []

def load_css(file_name):
    with open(file_name) as file:
        st.markdown(f"<style>{file.read()}</style>", unsafe_allow_html=True)

css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    load_css(css_path)

def get_user_info():
    if hasattr(st, "user") and st.user and getattr(st.user, "is_logged_in", False):
        try:
            name = st.user.get("name")
        except AttributeError:
            name = getattr(st.user, "name", None)
        name = name or "Google User"

        try:
            email = st.user.get("email")
        except AttributeError:
            email = getattr(st.user, "email", None)
        email = email or "google_user@gmail.com"

        try:
            picture = st.user.get("picture")
        except AttributeError:
            picture = getattr(st.user, "picture", None)
        picture = picture or ""

        return {"name": name, "email": email, "picture": picture, "is_demo": False}
    elif "mock_user" in st.session_state:
        return {**st.session_state.mock_user, "is_demo": True}
    return None

user_info = get_user_info()
user = SimpleNamespace(**user_info) if user_info else None

if user is None:
    # Use st.container(border=True) to trigger the stunning CSS login-card / stVerticalBlockBorderWrapper styling
    with st.container(border=True):
        st.markdown('<h1 class="login-title"><span class="gradient-text">Welcome to AI Workspace</span></h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Securely authenticate to access your customized AI Workspace</p>', unsafe_allow_html=True)
        
        if st.button("🔑 Log in with Google", key="real_login_btn", use_container_width=True):
            st.login()
                        
        st.markdown('<div class="login-divider">— OR —</div>', unsafe_allow_html=True)
                        
        if st.button("🚀 Explore in Demo Mode", key="demo_login_btn", use_container_width=True):
            st.session_state.mock_user = {
                "name": "Demo Explorer",
                "email": "explorer@example.com",
                "picture": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&h=150",
            }
            st.rerun()
    st.stop()

st.markdown(f"Welcome! {user.name}")

# ------------------ PROFILE CARD ------------------
with st.sidebar.container(border=True):
    avatar_img = user.picture if user.picture else "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&h=150"
    st.markdown(f'<img src="{avatar_img}" class="profile-avatar">', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-name">{user.name}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-email">{user.email}</div>', unsafe_allow_html=True)
    
    if user.is_demo:
        st.markdown('<div class="sidebar-status-container"><span class="status-badge"><span class="status-dot demo"></span>Demo Mode</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-status-container"><span class="status-badge"><span class="status-dot secure"></span>Google Secure</span></div>', unsafe_allow_html=True)

    if st.button("Logout 🚪", key="logout_btn", use_container_width=True):
        if "mock_user" in st.session_state:
            del st.session_state.mock_user
        try:
            st.logout()
        except Exception:
            pass
        st.rerun()
    
st.sidebar.markdown("---")

# ------------------ CHAT HEADER ------------------
st.markdown('<h1 class="app-header">🤖 <span class="gradient-text">My First AI Model</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">A premium, highly-styled conversational assistant powered by Hugging Face Inference API</p>', unsafe_allow_html=True)

model_options = ["meta-llama/Llama-3.1-8B-Instruct", "meta-llama/Meta-Llama-3-8B-Instruct", "mistralai/Mistral-7B-Instruct-v0.3"]
model_selected = st.sidebar.selectbox("Model Name", model_options, index=0)   
token_len = st.sidebar.slider("Max Tokens to Generate", min_value=16, max_value=512, value=64, step=16)
client = InferenceClient(model=model_selected, token=hf_token)

if len(st.session_state.messages) > 0:
    if st.sidebar.button("Clear Chat History", key="clear"):
        st.session_state.messages = []
        st.session_state.temp_msg = []
        st.rerun()
    if st.sidebar.button("Hide Previous Chats", key="hide_history"):
        st.session_state.temp_msg = st.session_state.messages.copy()
        st.session_state.messages = []
        st.rerun()
    if st.sidebar.button("Show Previous Chats", key="show_history") and len(st.session_state.temp_msg) > 0:
        st.session_state.temp_msg.extend(st.session_state.messages)
        st.session_state.messages = st.session_state.temp_msg.copy()
        st.session_state.temp_msg = []
        st.rerun()

if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown("Hi! I'm a multilingual chatbot. How can I help you today?")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input("Ask me anything"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=user.picture):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="https://images.unsplash.com/photo-1750096319146-6310519b5af2?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTF8fGJvdCUyMGZhY2V8ZW58MHx8MHx8fDA%3D"):
        with st.spinner("Thinking..."):
            try:
                stream = client.chat_completion(
                    model=model_selected,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    max_tokens=token_len,
                    stream=True,
                )

                def stream_generator():
                    for chunk in stream:
                        if hasattr(chunk, "choices") and chunk.choices:
                            content = chunk.choices[0].delta.content
                            if content:
                                yield content

                response = st.write_stream(stream_generator())
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error calling Hugging Face InferenceClient: {e}")



