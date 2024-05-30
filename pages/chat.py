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
    del st.session_state['messages']
    if "thread" in st.session_state:
        del st.session_state['thread']
        try:
            response = client.beta.threads.delete(st.session_state['thread'].id)
        except:
            pass

def delete_assistant():
    if "assistant" in st.session_state:
        response = client.beta.assistants.delete(st.session_state['assistant'].id)
        del st.session_state['assistant']


if st.button("Start a new thread"):
    delete_thread()

if st.button("Leave"):
    delete_thread()
    delete_assistant()

# setup tools
tools = [
    {
        "type":"function",
        "function": {
            "name":"generate_image",
            "description":"Generate image and return url of the image",
            "parameters": {
                "type":"object",
                "properties": {"image_prompt":{"type":"string", "description":"prompt for image generation"}}
            }
        }
    },
    {"type": "code_interpreter"}
]

# setup assistant, thread, memory
if "assistant" in st.session_state:
    assistant = st.session_state["assistant"]
else:
    assisant = client.beta.assistants.create(
        model="gpt-4-1106-preview",
        tools = tools
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


# main chat UI

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
    # check run step - check tools
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=thread.id,
        run_id=run.id
    )
    tools_info = {}
    for i,run_step in enumerate(run_steps.data):
        if run_step.step_details.type == 'tool_calls':
            for tool_call in run_step.step_details.tool_calls:
                if tool_call.type == 'code_interpreter':
                    with st.expander("Code"):
                        tools_info[tool_call.type] = tool_call.code_interpreter.input

    thread_messages = client.beta.threads.messages.list(thread.id, limit=1)
    response = thread_messages.data[0].content[0].text.value

    for k,v in tools_info:
        response += """
[Tool: {k}]
{v}
"""

    # show assistant message
    with st.chat_message("assistant"):
        st.markdown(response)

    # save assistant message in memory
    st.session_state.messages.append({"role":"assistant", "content": response})

