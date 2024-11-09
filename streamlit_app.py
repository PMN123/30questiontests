import streamlit as st
import PyPDF2
import re
import pandas as pd
from io import BytesIO

# Function to extract pages with the first 30 questions
def extract_pages_with_first_30_questions(input_pdf, num_questions=30):
    reader = PyPDF2.PdfReader(input_pdf)
    writer = PyPDF2.PdfWriter()
    question_count = 0
    extracted_text = ""
    
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        extracted_text += page_text
        
        # Count questions on the page
        questions_on_page = re.findall(r"\b\d+\.\s", page_text)
        question_count += len(questions_on_page)
        
        # Add the page to the writer
        writer.add_page(page)
        
        # Stop once we've captured the first 30 questions
        if question_count >= num_questions:
            break
    
    # Save the extracted pages to an in-memory BytesIO object for download
    output_pdf = BytesIO()
    writer.write(output_pdf)
    output_pdf.seek(0)
    
    return output_pdf, extracted_text

# Function to extract answers by searching through the entire PDF text
def extract_answers(input_pdf, num_answers=30):
    reader = PyPDF2.PdfReader(input_pdf)
    full_text = ""
    
    # Concatenate text from all pages
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + "\n"
    
    # Regex to match answers in the format "1. A", "2. B", etc.
    answers = re.findall(r"\d+\.\s([A-D])", full_text)  # Capture only the letter (answer choice)
    
    return answers[:num_answers]

# Streamlit Interface
st.title("Extract First 30 Questions and Answers from PDF")

# File upload
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
if uploaded_file is not None:
    st.write("Processing your file...")

    # Extract pages containing the first 30 questions
    output_pdf, extracted_text = extract_pages_with_first_30_questions(uploaded_file)
    
    # Display download button for the resulting PDF
    st.subheader("Download the PDF with the First 30 Questions")
    st.download_button(
        label="Download Extracted PDF",
        data=output_pdf,
        file_name="first_30_questions.pdf",
        mime="application/pdf"
    )
    
    # Extract and display answers in a single-column table format
    answers = extract_answers(uploaded_file)
    answers_df = pd.DataFrame(answers, columns=["Answer"])  # Only include the "Answer" column
    
    st.subheader("First 30 Answers")
    st.table(answers_df)
    
    # Provide option to download answers as CSV
    csv_data = answers_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Answers as CSV", csv_data, file_name="answers.csv")
