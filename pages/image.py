import streamlit as st

@st.cache_data
def generate_image(image_prompt):
    client = OpenAI(api_key=st.session_state['OPENAI_API_KEY'])
    response = client.images.generate(
      model="dall-e-3",
      prompt=image_prompt,
    )
    image_url = response.data[0].url
    return image_url

st.session_state['image_prompt'] = st.text_input("어떤 그림을 원하시나요?",value=st.session_state.get("image_prompt",''))

if st.button("Run"):
  with st.spinner("Generating..."):
    image_url = generate_image(st.session_state['image_prompt'])
    st.markdown(f"![{st.session_state['image_prompt']}]({image_url})")
