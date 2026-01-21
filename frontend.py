#Step1: Setup Streamlit 
import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000/ask"

st.set_page_config(page_title="Ai Mental Health Therapist", layout="wide")
st.title("🧠 Ai Mental Health Support Companion")

#Initialize chat history in session state 
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

#Step2: User is able to ask question
#Chat input
user_input = st.chat_input("What's on your mind today?")
if user_input:
    #Append user message 
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    #Ai Agent exists here 
    response = requests.post(BACKEND_URL, json={"message": user_input})
    try:
        data = response.json()
        assistant_reply = data.get("response", "No response from backend")
        
    except ValueError:
        assistant_reply = "Backend returned an invalid response."
        

    st.session_state.chat_history.append({
    "role": "assistant",
    "content": f"{assistant_reply}"
    })


for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])