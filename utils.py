import os
import streamlit as st
from PIL import Image
import io
import tempfile
import pdf2image

def get_file_extension(filename):
    """Get the file extension from a filename."""
    return os.path.splitext(filename)[1][1:].lower()

def is_valid_file_type(file_extension):
    """Check if the file type is supported by the application."""
    valid_types = ['jpg', 'jpeg', 'png', 'pdf', 'txt']
    return file_extension.lower() in valid_types

def display_document_preview(uploaded_file, file_extension):
    """
    Display a preview of the uploaded document.
    
    Args:
        uploaded_file: The uploaded file object
        file_extension (str): The file extension
    """
    try:
        if file_extension.lower() in ['jpg', 'jpeg', 'png']:
            # For image files, display directly
            image = Image.open(uploaded_file)
            st.image(image, caption="Document Preview", use_column_width=True)
            
        elif file_extension.lower() == 'pdf':
            # For PDF files, convert first page to image and display
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_file_path = tmp_file.name
            
            # Convert first page of PDF to image
            try:
                pages = pdf2image.convert_from_path(temp_file_path, first_page=1, last_page=1)
                if pages:
                    # Display the first page
                    st.image(pages[0], caption="PDF First Page", use_column_width=True)
                else:
                    st.warning("Could not generate PDF preview.")
            except Exception as e:
                st.warning(f"Could not generate PDF preview: {str(e)}")
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
        elif file_extension.lower() == 'txt':
            # For text files, show first few lines
            content = uploaded_file.getvalue().decode('utf-8')
            preview_lines = '\n'.join(content.split('\n')[:10])
            st.text_area("Text Preview (first 10 lines)", preview_lines, height=150)
            
        else:
            st.warning(f"Preview not available for {file_extension.upper()} files.")
            
    except Exception as e:
        st.error(f"Error displaying preview: {str(e)}")
