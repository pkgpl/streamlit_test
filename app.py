import streamlit as st
from openai import OpenAI

@st.cache_data
def ask_llm(prompt):
    client = OpenAI(api_key=st.session_state['OPENAI_API_KEY'])
    response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[{"role": "user", "content": prompt}]  
    )
    return response.choices[0].message.content

st.header("Hello World !!")

st.session_state['OPENAI_API_KEY'] = st.text_input("Your OpenAI API Key", type="password", value=st.session_state.get("OPENAI_API_KEY",''))
st.session_state['text_prompt'] = st.text_input("질문?",value=st.session_state.get("text_prompt",''))


if st.button("Run"):
  with st.spinner("Generating..."):
    answer = ask_llm(st.session_state['text_prompt'])
    st.markdown(f"응답: {answer}")