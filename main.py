import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import requests
from dotenv import load_dotenv
import os
import base64

# Initialize the OpenAI client
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(OPENAI_API_KEY)

client = OpenAI()

def get_image_url(image_path):
    # Prepend ./ to the image name
    return f"./{image_path}"

def save_uploaded_file(uploaded_file):
    try:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return uploaded_file.name
    except Exception as e:
        return None

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def ask_openai(image, question):
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
    "model": "gpt-4-turbo",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": question
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json())
    response_json = response.json()
    return response_json['choices'][0]['message']['content']

st.title('Educational Image Analysis')

uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'png', 'jpeg'])
if uploaded_file is not None:
    image_path = save_uploaded_file(uploaded_file)
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)

    image_url = get_image_url(image_path)  # Get the URL of the uploaded image
    # Getting the base64 string
    base64_image = encode_image(image_url)

    # refine the question with an additional layer of prompt to be syllabus specific
    question = st.text_input("Enter your question:")
    if st.button('Answer Question'):
        if question:
            refined_prompt = "Answer from first principles. Your answer should be concise and understood by a primary school child and adhere to the Singapore's Primary School Science Syllabus."
            refined_question = question + refined_prompt
            answer = ask_openai(base64_image, refined_question)
            st.write(answer)
        else:
            st.write("Please enter a question.")

    # Additional chat should utilise a cheaper model without having to call the image; perhaps should describe the image first and store the description as a memory

    # # Additional chat functionality
    # st.header("Further Questions")
    # further_question = st.text_input("Ask more about this image:")
    # if st.button('Submit Question'):
    #     if further_question:
    #         additional_answer = ask_openai(image_url, further_question)
    #         st.write(additional_answer)
    #     else:
    #         st.write("Please enter a further question.")
