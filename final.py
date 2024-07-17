import streamlit as st
import fitz  # PyMuPDF
import ollama
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json

# Initialize Ollama client
client = ollama.Client()

# Function to get response from Ollama model
def get_ollama_response(prompt, text):
    complete_prompt = f"{prompt}\n\n{text}"
    try:
        response = client.chat(model='llama3', messages=[{'role': 'user', 'content': complete_prompt}])
        st.write("Ollama response:", response)  # Log the response for debugging
        
        # Check the structure of the response and extract the content
        if 'message' in response and 'content' in response['message']:
            return response['message']['content'].strip()
        else:
            return "Failed to get a valid response structure from the model."
    except json.JSONDecodeError:
        return "Failed to parse JSON response from the model."
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return "Failed to get a response from the model."

def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

def generate_pdf(content, output_path):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, height - 30, "Visvesvaraya Technological University, Belagavi.")
    c.setFont("Helvetica", 12)
    c.drawString(30, height - 50, "Model Question Paper-I with effect from 2022-23 (CBCS Scheme)")
    c.drawString(30, height - 70, "First/Second Semester B.E. Degree Examination")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, height - 90, "Introduction to Nanotechnology")
    c.setFont("Helvetica", 12)
    c.drawString(30, height - 110, "TIME: 03 Hours  Max. Marks: 100")
    c.drawString(30, height - 130, "Note: Answer any FIVE full questions, choosing at least ONE question from each Module.")

    # Split the content into lines and draw them
    y = height - 150
    lines = content.split('\n')
    for line in lines:
        if y < 40:
            c.showPage()
            y = height - 30
        c.drawString(30, y, line)
        y -= 20

    c.save()
    buffer.seek(0)
    return buffer

def main():
    st.title("PDF Text Analysis with Llama 3")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)
        st.text_area("Extracted Text", text, height=300)
        
        prompt = st.text_area("Enter your prompt for Llama 3", '''Design a model exam paper for a course on computer science, with 5 modules, each having 2 main questions (Q1/Q2, Q3/Q4, etc.). Each main question should have sub-parts with specific mark allocations. Ensure questions cover key concepts from the syllabus and include problem-solving, diagrams, protocols, and algorithms as applicable. Follow the format:
Module 1
Q1 (a) [10 marks] (b) [10 marks]
Q2 (a) [7 marks] (b) [8 marks] (c) [5 marks]
Module 2
Q3 (a) [10 marks] (b) [10 marks]
Q4 (a) [7 marks] (b) [8 marks] (c) [5 marks]
... (similar format for Modules 3-5)
Note: The marks allocation is indicative and can be adjusted according to specific requirements
''')
        if st.button("Run Llama 3"):
            output = get_ollama_response(prompt, text)
            st.text_area("Llama 3 Output", output, height=300)
            
            pdf_buffer = generate_pdf(output, "output.pdf")
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name="Model_Question_Paper.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
