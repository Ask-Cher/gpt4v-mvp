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

client = OpenAI(api_key=OPENAI_API_KEY)

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
    refined_prompt = """You are an expert educator, and are responsible for answering the user's questions.
            Your answer should be concise and understood by a primary school child and adhere to the Singapore's Primary School Science Syllabus.
            Think step by step and answer from first principles.
            For example, high-level concepts such as "air is an insulator" can be better explained as "air is a poor conductor of heat" to better explain it to a child.

            If they ask questions not related to the question, \
            you should politely decline to answer and remind them to stay on topic.

            Here's the question:
            """

    # refine the question with an additional layer of prompt to be syllabus specific
    question = st.text_input("Enter your question:")
    if st.button('Answer Question'):
        if question:
            refined_question = refined_prompt + question
            answer = ask_openai(base64_image, refined_question)
            st.write(answer)
        else:
            st.write("Please enter a question.")
