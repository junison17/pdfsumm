import streamlit as st
from openai import ChatCompletion
import os
import openai
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract


# Load environment variables from a .env file


# Set OpenAI API key
openai.api_key = st.secrets["api_key"]

# Tesseract 실행 파일 경로 설정 (Windows에서만 필요)
# Windows 사용자의 경우 설치 경로에 따라 아래 줄의 주석을 해제하고 경로를 설정하세요.
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to read text from a PDF file
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to read an image file
def read_image(file):
    image = Image.open(file)
    return image

# Function to perform OCR on an image
def ocr_image(image):
    return pytesseract.image_to_string(image)

# Function to analyze a document based on its type (PDF or image)
def analyze_document(file, file_type):
    if file_type == "pdf":
        text = read_pdf(file)  # Extract text from PDF
    elif file_type in ["png", "jpg", "jpeg"]:
        image = read_image(file)  # Read image
        text = ocr_image(image)  # Extract text using OCR
    else:
        text = "Unsupported file type"  # Unsupported file type message
    
    return text

# Function to generate a response using the GPT-4o model
def generate_response(messages):
    response = ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=3000,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

# Streamlit app title
st.title("AI Document Analysis App")

# File upload widgets for reference file and blank form
reference_file = st.file_uploader("Upload a reference file for analysis", type=["pdf", "png", "jpg", "jpeg"])
form_file = st.file_uploader("Upload a blank form", type=["pdf", "png", "jpg", "jpeg"])

# Input fields for document details
doc_name = st.text_input("Document Name")
description = st.text_input("Brief Description of the Form")
content_type = st.selectbox("Content Type", ["Creative", "Balanced", "Precise", "Factual"])
image_needed = st.selectbox("Do you need an image?", ["Yes", "No"])
image_style = st.selectbox("Image Style", ["Realistic", "Illustrative", "Abstract"])

# Analyze the uploaded reference file
if reference_file:
    file_type = reference_file.name.split('.')[-1].lower()  # Get the file extension
    if file_type in ["pdf", "png", "jpg", "jpeg"]:
        analysis_text = analyze_document(reference_file, file_type)  # Analyze the document
        st.text_area("Analysis Result", analysis_text)  # Display the analysis result
    else:
        st.error("Unsupported file type")  # Error message for unsupported file type

# Generate output when the button is clicked
if st.button("Generate Output"):
    # Prepare messages for the GPT-4o model
    if reference_file:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that responds in Markdown."},
            {"role": "user", "content": f"Document Name: {doc_name}\nDescription: {description}\nContent Type: {content_type}\nImage Needed: {image_needed}\nImage Style: {image_style}\n\nContent:\n{analysis_text}"}
        ]
    else:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that responds in Markdown."},
            {"role": "user", "content": f"Document Name: {doc_name}\nDescription: {description}\nContent Type: {content_type}\nImage Needed: {image_needed}\nImage Style: {image_style}\n\nContent:\n"}
        ]

    # Generate a response using the GPT-4o model
    response = generate_response(messages)
    st.markdown(response)  # Display the response in Markdown format
    
    # Process the uploaded form file if it exists
    if form_file:
        form_file_extension = form_file.name.split('.')[-1].lower()  # Get the form file extension
        if form_file_extension in ["pdf", "png", "jpg", "jpeg"]:
            form_stored_path = f"completed_{form_file.name}"  # Define the path to save the completed form
            with open(form_stored_path, "wb") as f:
                f.write(form_file.getbuffer())  # Save the form file
            st.success(f"Completed form saved as {form_stored_path}")  # Success message
        else:
            st.error("Unsupported file type for form upload")  # Error message for unsupported file type
    else:
        st.warning("No form file uploaded")  # Warning if no form file is uploaded