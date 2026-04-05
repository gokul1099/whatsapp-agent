import streamlit as st
import time
from PIL import Image
from typing import TypedDict

class SessionState(TypedDict):
    thread_id: int
    history: list[dict]

def init_session_state() -> SessionState:
    """Initialise session state with type hints"""
    defaults: SessionState = {
        "thread_id": 1,
        "history": []
    }
    for key,value in defaults:
        if key not in st.session_state:
            st.session_state[key] = value
    return st.session_state

session: SessionState = init_session_state()


text_input = st.chat_input("Enter your message")


def process_image_message(message):
    """Proces image inputs"""
    pass

def process_text_message(message):
    """Process text inputs"""
    user_message: str = message.content
    thred_id: int = st.session_state.get("thread_id")
    """
    Should open the local sqlite server for langgraph state memory and should compile the graph the latest human message
    """
    pass

def proess_audio_message(message):
    """Process audio input"""
    pass


# Display chat history
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        print(message,"mesage")
        st.write(message["content"])
        # if message["type"] == "text":
        #     st.write(message["content"])
        # elif message["type"] == "image":
        #     st.write(message["content"], caption="Uploaded image")

image_file = st.file_uploader(
    "Upload an image", type=["jpg", "png", "jpeg"]
)

audio_file= st.file_uploader(
    "Upload audio", type=["mp3", ".wav"]
)

if image_file:
    image = Image.open(image_file)
    st.session_state.history.append({
        "role":"user",
        "type":"image",
        "content": image
    })
    with st.chat_message("user"):
        st.image(image, caption="Uploaded image", width=300)
    process_image_message()


if text_input:
    with st.chat_message("user"):
        st.write(text_input)
    st.session_state.history.append({"role": "user", "content": text_input})
    with st.chat_message("assistant"):
        response = st.write_stream(process_text_message(text_input))
    st.session_state.history.append({"role":"assistant", "content":response})

