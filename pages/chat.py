import streamlit as st
from openai import OpenAI

if not "OPENAI_API_KEY" in st.session_state or len(st.session_state['OPENAI_API_KEY'].strip())==0:
    st.write("Enter your OpenAI API Key")
    st.stop()

client = OpenAI(api_key=st.session_state['OPENAI_API_KEY'])


@st.cache_data
def generate_image(image_prompt):
    response = client.images.generate(
      model="dall-e-3",
      prompt=image_prompt,
    )
    image_url = response.data[0].url
    return image_url

def delete_thread():
    if "thread" in st.session_state:
        response = client.beta.threads.delete(st.session_state['thread'].id)
        del st.session_state['thread']

def delete_assistant():
    if "assistant" in st.session_state:
        response = client.beta.assistants.delete(st.session_state['assistant'].id)
        del st.session_state['assistant']


if st.button("Start a new thread"):
    delete_thread()

if st.button("Leave"):
    delete_thread()
    delete_assistant()


if "assistant" in st.session_state:
    assistant = st.session_state["assistant"]
else:
    assisant = client.beta.assistants.create(
        model="gpt-4-1106-preview"
    )
    st.session_state['assistant'] = assisant

if "thread" in st.session_state:
    thread = st.session_state["thread"]
else:
    thread = client.beta.threads.create()
    st.session_state['thread'] = thread

if "messages" not in st.session_state:
    st.session_state['messages'] = []


for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

if prompt := st.chat_input("What is up?"):
    # show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    # save user message in memory
    st.session_state.messages.append({"role":"user", "content": prompt})

    ##  ask llm
    new_message = client.beta.threads.messages.create(
        thread_id = thread.id,
        role="user",
        content=prompt
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    thread_messages = client.beta.threads.messages.list(thread.id, limit=1)
    response = thread_messages.data[0].content[0].text.value

    # show assistant message
    with st.chat_message("assistant"):
        st.markdown(response)
    # save assistant message in memory
    st.session_state.messages.append({"role":"assistant", "content": response})

