import streamlit as st
from pdf2docx import Converter
from io import BytesIO
import tempfile

# Set the page configuration
st.set_page_config(page_title="PDF to Word Converter", page_icon="📄")

# Add a title and a subtitle
st.title("PDF to Word Converter")
st.write("Upload a PDF file to convert it to a Word document.")

# Upload PDF file
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner('Converting...'):
        # Save the uploaded PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
            temp_pdf_file.write(uploaded_file.read())
            temp_pdf_file.seek(0)
            temp_pdf_path = temp_pdf_file.name

        # Convert PDF to Word
        word_file = BytesIO()
        converter = Converter(temp_pdf_path)
        converter.convert(word_file)
        converter.close()
        
        word_file.seek(0)
        
        # Offer download of the Word file
        st.success('Conversion Successful!')
        st.download_button(
            label="Download Word document",
            data=word_file,
            file_name="converted.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        # Offer download of the original PDF file
        st.download_button(
            label="Download Original PDF",
            data=open(temp_pdf_path, "rb"),
            file_name=uploaded_file.name,
            mime="application/pdf"
        )

# Add some styling to make the app look professional
st.markdown("""
    <style>
        .reportview-container {
            background: #f0f0f5;
        }
        .sidebar .sidebar-content {
            background: #f0f0f5;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            transition-duration: 0.4s;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: white;
            color: black;
            border: 2px solid #4CAF50;
        }
    </style>
    """, unsafe_allow_html=True)

# Hide Streamlit footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
