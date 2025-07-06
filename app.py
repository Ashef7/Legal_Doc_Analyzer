import streamlit as st
import os
import tempfile
from pathlib import Path
import time

from document_analyzer import extract_text_from_document
from document_classifier import classify_document
from document_compliance import analyze_compliance
from utils import get_file_extension, is_valid_file_type, display_document_preview
from database import save_document_analysis

# Set page config
st.set_page_config(
    page_title="Indian Legal Document Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application title and description
st.title("Document Analyzer")
st.markdown("""
This application helps you analyze documents under Indian legal standards.
Upload your document to extract text, classify it, and identify any non-compliant content.
""")

# Sidebar for upload and options
with st.sidebar:
    st.header("Document Upload")
    uploaded_file = st.file_uploader(
        "Choose a document file", 
        type=["jpg", "jpeg", "png", "pdf", "txt"],
        help="Upload document files in JPG, PNG, PDF, or TXT format."
    )
    
    st.subheader("Analysis Options")
    perform_classification = st.checkbox("Classify Document", value=True)
    perform_compliance_check = st.checkbox("Check for Non-Compliance", value=True)
    save_to_database = st.checkbox("Save Analysis to Database", value=True)
    
    st.subheader("Navigation")
    st.page_link("pages/01_Document_History.py", label="📋 View Document History", icon="📋")
    
    st.subheader("About")
    st.info("""
    This tool uses:
    - Tesseract OCR for text extraction
    - Machine Learning for document classification
    - NLP for compliance analysis
    - PostgreSQL for storing analysis history
    """)

# Main content area
if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    
    # Display file info
    with col1:
        st.subheader("Document Information")
        file_extension = get_file_extension(uploaded_file.name)
        
        if not is_valid_file_type(file_extension):
            st.error(f"Invalid file type: {file_extension}. Please upload a JPG, PNG, PDF, or TXT file.")
            st.stop()
            
        file_size_kb = uploaded_file.size / 1024
        file_details = {
            "Filename": uploaded_file.name,
            "File Type": file_extension.upper(),
            "File Size": f"{file_size_kb:.2f} KB"
        }
        
        for key, value in file_details.items():
            st.write(f"**{key}:** {value}")
    
    # Document preview
    with col2:
        st.subheader("Document Preview")
        display_document_preview(uploaded_file, file_extension)
    
    # Process the document
    with st.spinner("Processing document..."):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_file_path = tmp_file.name
        
        # Extract text with progress indicator
        extraction_progress = st.progress(0)
        st.text("Extracting text...")
        
        for i in range(0, 101, 20):
            time.sleep(0.1)  # Simulate processing time
            extraction_progress.progress(i/100)
        
        extracted_text = extract_text_from_document(temp_file_path, file_extension)
        extraction_progress.progress(1.0)
        
        # Remove temporary file
        os.unlink(temp_file_path)
    
    # Display extracted text in expandable section
    with st.expander("Extracted Text", expanded=False):
        if extracted_text:
            st.text_area("", extracted_text, height=200)
        else:
            st.warning("No text could be extracted from the document.")
    
    # Initialize variables for database storage
    classification_result = None
    confidence = None
    compliance_issues = None
    is_compliant = None
    
    # Perform document classification if selected
    if perform_classification and extracted_text:
        st.subheader("Document Classification")
        with st.spinner("Classifying document..."):
            classification_result, confidence = classify_document(extracted_text)
            
            # Display classification result with appropriate styling
            if classification_result == "legal":
                st.success(f"✅ Document appears to be legal (Confidence: {confidence:.2f}%)")
            else:
                st.error(f"❌ Document appears to be illegal (Confidence: {confidence:.2f}%)")
                
            # Display gauge chart for confidence
            st.progress(confidence/100)
    
    # Perform compliance analysis if selected
    if perform_compliance_check and extracted_text:
        st.subheader("Compliance Analysis")
        with st.spinner("Analyzing compliance..."):
            compliance_issues = analyze_compliance(extracted_text)
            is_compliant = len(compliance_issues) == 0
            
            if compliance_issues:
                st.warning(f"Found {len(compliance_issues)} potential compliance issues")
                
                for issue in compliance_issues:
                    with st.expander(f"Issue: {issue['category']}"):
                        st.write(f"**Description:** {issue['description']}")
                        st.write("**Text:**")
                        
                        # Display the problematic text with highlighting
                        highlighted_text = issue['text']
                        st.markdown(f"<div style='background-color: #FFE0E0; padding: 10px; border-radius: 5px;'>{highlighted_text}</div>", unsafe_allow_html=True)
                        
                        st.write(f"**Recommendation:** {issue['recommendation']}")
            else:
                st.success("✅ No compliance issues detected")
    
    # Summary section
    if perform_classification and perform_compliance_check and extracted_text:
        st.subheader("Analysis Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Classification", 
                value="Legal" if classification_result == "legal" else "Illegal",
                delta=f"{confidence:.2f}% Confidence"
            )
        
        with col2:
            compliance_count = len(compliance_issues) if compliance_issues else 0
            st.metric(
                label="Compliance Issues", 
                value=compliance_count,
                delta="-" if compliance_count == 0 else f"{compliance_count} Issues Found",
                delta_color="normal" if compliance_count == 0 else "inverse"
            )
    
    # Save to database if selected
    if save_to_database and extracted_text:
        try:
            # Save document analysis to database
            doc_analysis = save_document_analysis(
                filename=uploaded_file.name,
                file_type=file_extension,
                file_size=file_size_kb,
                extracted_text=extracted_text,
                classification_result=classification_result,
                confidence_score=confidence,
                compliance_issues_count=len(compliance_issues) if compliance_issues else 0,
                is_compliant=is_compliant
            )
            
            # Display success message with the database ID
            st.success(f"Analysis saved to database with ID: {doc_analysis.id}")
            st.markdown(f"[View in Document History](pages/01_Document_History)")
            
        except Exception as e:
            st.error(f"Error saving to database: {str(e)}")

else:
    # Display instructions when no file is uploaded
    st.info("👆 Please upload a document to begin analysis")
    
    # Display example layout with empty placeholders
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Document Information")
        st.write("File details will appear here")
    
    with col2:
        st.subheader("Document Preview")
        st.write("Document preview will appear here")
    
    st.subheader("Extracted Text")
    st.write("Document text will appear here")
    
    st.subheader("Analysis Results")
    st.write("Classification and compliance results will appear here")
    
    # Add link to document history
    st.markdown("### View Previous Analyses")
    st.write("Check your document analysis history to review past results.")
    st.page_link("pages/01_Document_History.py", label="📋 View Document History", icon="📋")
