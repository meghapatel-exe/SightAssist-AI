# pip install -r requirements.txt
# export OPENAI_API_KEY=your-own-key   (Included in the .env file - gitignore file) 
# streamlit run app.py

# The above lines of code are showcased to run the code and display it in a dedicated browser based web application. 
# Streamlit is thus used to showcase the actual demo interface for the users


"""SightAssist: AI image descriptions for blind and low-vision users.

Run with:  streamlit run app.py
"""
import base64
import hashlib
import os

# Interface libs
import streamlit as st 

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

WARNING = (
    "AI-generated descriptions can contain mistakes. "
    "Check anything important (medicine, safety, money, legal text) with another source."
)

SYSTEM_PROMPT = """You describe images for blind and low-vision users.
Rules:
- Give useful context, not just a list of objects: what the scene is, how things are arranged \
(left/right, near/far), and anything safety-relevant, mentioned first.
- Only state what is visible. If something is unclear, blurry, hidden or cannot be known from \
a photo (for example whether a hob is hot), say so plainly instead of guessing.
- Read visible text exactly if legible. If it is not legible, say which part you cannot read.
- Do not give medical, legal or financial advice. Say what the image shows and suggest checking \
a reliable source or a trusted person.
- Use plain language. No emojis, no markdown tables."""

MODE_INSTRUCTIONS = {
    "Concise": "Describe this image in one to two short sentences (under 40 words).",
    "Detailed": "Describe this image in one clear paragraph (under 150 words), "
    "covering layout, context and anything safety-relevant first.",
}


def demo_reply(kind: str, mode: str = "Concise", question: str = "") -> str:
    """SIMULATED responses so the interface can be inspected without an API key."""
    if kind == "describe":
        if mode == "Concise":
            return "[Demo] A white and blue box of tablets on a table. Some printed text is visible on the front."
        return (
            "[Demo] A small white and blue medicine box sits in the centre of a wooden table. "
            "Printed text is visible across the front, including a product name. The right edge "
            "of the box is slightly out of focus, so smaller text there is not legible."
        )
    return (
        f"[Demo] You asked: \"{question}\". In real mode I would answer from the image only, "
        "and say if the detail is not visible or I am unsure."
    )


def call_model(history, image_bytes, mime, mode, api_key):
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    data_url = f"data:{mime};base64,{base64.b64encode(image_bytes).decode()}"
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for i, m in enumerate(history):
        if i == 0:
            # The first user turn always carries the image so follow-ups stay grounded in it.
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": MODE_INSTRUCTIONS[mode]},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            )
        else:
            messages.append(m)
    resp = client.chat.completions.create(model=MODEL, messages=messages, max_tokens=500)
    return resp.choices[0].message.content.strip()


def reset_state():
    st.session_state.messages = []  # list of {"role", "content"}; index 0 is the image request


st.set_page_config(page_title="SightAssist", layout="centered")
if "messages" not in st.session_state:
    reset_state()

st.title("SightAssist")
st.write("Upload a photo and get a spoken-friendly description. You choose how much detail you want and can ask follow-up questions.")

with st.sidebar:
    st.header("Settings")
    key_input = st.text_input(
        "OpenAI API key (kept in this session only)", type="password",
        help="Or set the OPENAI_API_KEY environment variable before starting the app.",
    )
    api_key = key_input or os.getenv("OPENAI_API_KEY", "")
    demo = st.checkbox(
        "Demo mode (simulated responses, no API call)", value=not api_key,
        help="Lets you inspect the interface without a key. Responses are canned, not from a model.",
    )
    if demo:
        st.info("Demo mode is on. Descriptions are simulated.")
    elif not api_key:
        st.error("Enter an API key or turn on demo mode.")

file = st.file_uploader("Choose an image (PNG, JPG or WebP)", type=["png", "jpg", "jpeg", "webp"])

if file is None:
    reset_state()
    st.stop()

image_bytes = file.getvalue()
img_hash = hashlib.sha256(image_bytes).hexdigest()
if st.session_state.get("img_hash") != img_hash:
    st.session_state.img_hash = img_hash
    reset_state()

st.image(image_bytes, caption=f"Uploaded image: {file.name}", use_container_width=True)

mode = st.radio("Description length", list(MODE_INSTRUCTIONS), horizontal=True)

if st.button("Describe image", type="primary", disabled=(not demo and not api_key)):
    reset_state()
    st.session_state.messages.append({"role": "user", "content": MODE_INSTRUCTIONS[mode]})
    with st.spinner("Describing the image..."):
        try:
            reply = (
                demo_reply("describe", mode)
                if demo
                else call_model(st.session_state.messages, image_bytes, file.type, mode, api_key)
            )
        except Exception as e:  # network, auth, rate limit
            st.session_state.messages.pop()
            st.error(f"Could not describe the image: {e}")
            reply = None
    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})

# Conversation (index 0 is the hidden image request, so skip it in the display)
for i, m in enumerate(st.session_state.messages):
    if i == 0:
        continue
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m["role"] == "assistant":
            if i == 1:
                st.warning(WARNING)
            else:
                st.caption("AI answers can be wrong. Check important details.")

if len(st.session_state.messages) >= 2:
    question = st.chat_input("Ask a follow-up question about this image")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply = (
                        demo_reply("followup", question=question)
                        if demo
                        else call_model(st.session_state.messages, image_bytes, file.type, mode, api_key)
                    )
                except Exception as e:
                    st.session_state.messages.pop()
                    st.error(f"Could not answer: {e}")
                    reply = None
            if reply:
                st.write(reply)
                st.caption("AI answers can be wrong. Check important details.")
                st.session_state.messages.append({"role": "assistant", "content": reply})
