import streamlit as st
import os
import pandas as pd
from datetime import datetime

from database import get_all_document_analyses, get_document_analysis_by_id, get_analysis_statistics

# Set page config
st.set_page_config(
    page_title="Document Analysis History",
    page_icon="📋",
    layout="wide"
)

# Page title
st.title("Document Analysis History")
st.markdown("View past document analyses and their results")

# Get analysis statistics
try:
    stats = get_analysis_statistics()
    
    # Display statistics in columns
    st.subheader("Analysis Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Documents", stats['total_count'])
    
    with col2:
        st.metric("Legal Documents", stats['legal_count'], 
                 f"{stats['legal_count']/stats['total_count']*100:.1f}%" if stats['total_count'] > 0 else "0%")
    
    with col3:
        st.metric("Illegal Documents", stats['illegal_count'], 
                 f"{stats['illegal_count']/stats['total_count']*100:.1f}%" if stats['total_count'] > 0 else "0%")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Compliant Documents", stats['compliant_count'], 
                 f"{stats['compliant_count']/stats['total_count']*100:.1f}%" if stats['total_count'] > 0 else "0%")
    
    with col2:
        st.metric("Non-Compliant Documents", stats['non_compliant_count'], 
                 f"{stats['non_compliant_count']/stats['total_count']*100:.1f}%" if stats['total_count'] > 0 else "0%")

except Exception as e:
    st.error(f"Error fetching statistics: {str(e)}")

# Get all document analyses
try:
    analyses = get_all_document_analyses()
    
    if analyses:
        # Create DataFrame for display
        data = []
        for analysis in analyses:
            data.append({
                "ID": analysis.id,
                "Filename": analysis.filename,
                "File Type": analysis.file_type.upper(),
                "Upload Date": analysis.upload_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "Classification": analysis.classification_result.capitalize() if analysis.classification_result else "Unknown",
                "Confidence": f"{analysis.confidence_score:.1f}%" if analysis.confidence_score else "N/A",
                "Issues": analysis.compliance_issues_count if analysis.compliance_issues_count is not None else "N/A",
                "Compliant": "✅" if analysis.is_compliant else "❌" if analysis.is_compliant is not None else "Unknown"
            })
        
        df = pd.DataFrame(data)
        
        # Display table
        st.subheader("Document History")
        st.dataframe(df, use_container_width=True)
        
        # Document details section
        st.subheader("Document Details")
        selected_id = st.selectbox("Select document to view details", 
                                  options=[analysis.id for analysis in analyses],
                                  format_func=lambda x: f"ID: {x} - {next((a.filename for a in analyses if a.id == x), '')}")
        
        if selected_id:
            selected_analysis = get_document_analysis_by_id(selected_id)
            
            if selected_analysis:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Filename:** {selected_analysis.filename}")
                    st.write(f"**File Type:** {selected_analysis.file_type.upper()}")
                    st.write(f"**File Size:** {selected_analysis.file_size:.2f} KB")
                    st.write(f"**Upload Date:** {selected_analysis.upload_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                
                with col2:
                    st.write(f"**Classification:** {selected_analysis.classification_result.capitalize() if selected_analysis.classification_result else 'Unknown'}")
                    st.write(f"**Confidence:** {selected_analysis.confidence_score:.1f}%" if selected_analysis.confidence_score else "N/A")
                    st.write(f"**Compliance Issues:** {selected_analysis.compliance_issues_count if selected_analysis.compliance_issues_count is not None else 'N/A'}")
                    st.write(f"**Compliant:** {'Yes' if selected_analysis.is_compliant else 'No' if selected_analysis.is_compliant is not None else 'Unknown'}")
                
                # Display extracted text
                if selected_analysis.extracted_text:
                    with st.expander("View Extracted Text", expanded=False):
                        st.text_area("", selected_analysis.extracted_text, height=200)
                else:
                    st.info("No extracted text available for this document")
    else:
        st.info("No document analyses found. Upload documents on the main page to start building history.")

except Exception as e:
    st.error(f"Error fetching document analyses: {str(e)}")

# Add a link back to the main page
st.markdown("[Go back to Document Analyzer](./)")