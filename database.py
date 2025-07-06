import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///mydatabase.db')

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

# Define DocumentAnalysis model
class DocumentAnalysis(Base):
    __tablename__ = 'document_analyses'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size = Column(Float, nullable=False)  # Size in KB
    upload_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    extracted_text = Column(Text, nullable=True)
    classification_result = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)  # Confidence percentage
    compliance_issues_count = Column(Integer, nullable=True)
    is_compliant = Column(Boolean, nullable=True)
    
    def __repr__(self):
        return f"<DocumentAnalysis(id={self.id}, filename='{self.filename}', classification='{self.classification_result}')>"

# Create all tables
Base.metadata.create_all(engine)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to get database session
def get_db_session():
    db = SessionLocal()
    try:
        return db
    except:
        db.close()
        raise

# Function to add document analysis to database
def save_document_analysis(
    filename, 
    file_type, 
    file_size, 
    extracted_text=None, 
    classification_result=None, 
    confidence_score=None, 
    compliance_issues_count=None, 
    is_compliant=None
):
    """
    Save document analysis results to the database
    
    Args:
        filename: Name of the uploaded file
        file_type: File extension (jpg, png, pdf, txt)
        file_size: File size in KB
        extracted_text: Extracted text content
        classification_result: Classification result (legal/illegal)
        confidence_score: Classification confidence percentage
        compliance_issues_count: Number of compliance issues
        is_compliant: Boolean indicating if document is compliant
        
    Returns:
        The created DocumentAnalysis object
    """
    db = get_db_session()
    try:
        # Create new document analysis
        doc_analysis = DocumentAnalysis(
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            extracted_text=extracted_text,
            classification_result=classification_result,
            confidence_score=confidence_score,
            compliance_issues_count=compliance_issues_count,
            is_compliant=is_compliant
        )
        
        # Add to database
        db.add(doc_analysis)
        db.commit()
        db.refresh(doc_analysis)
        
        return doc_analysis
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Function to get all document analyses
def get_all_document_analyses(limit=100):
    """
    Get all document analyses from database
    
    Args:
        limit: Maximum number of records to return
        
    Returns:
        List of DocumentAnalysis objects
    """
    db = get_db_session()
    try:
        return db.query(DocumentAnalysis).order_by(DocumentAnalysis.upload_timestamp.desc()).limit(limit).all()
    finally:
        db.close()

# Function to get analysis by ID
def get_document_analysis_by_id(analysis_id):
    """
    Get document analysis by ID
    
    Args:
        analysis_id: ID of the document analysis
        
    Returns:
        DocumentAnalysis object or None if not found
    """
    db = get_db_session()
    try:
        return db.query(DocumentAnalysis).filter(DocumentAnalysis.id == analysis_id).first()
    finally:
        db.close()

# Function to get statistics
def get_analysis_statistics():
    """
    Get statistics about document analyses
    
    Returns:
        Dictionary with statistics
    """
    db = get_db_session()
    try:
        total_count = db.query(DocumentAnalysis).count()
        legal_count = db.query(DocumentAnalysis).filter(DocumentAnalysis.classification_result == 'legal').count()
        illegal_count = db.query(DocumentAnalysis).filter(DocumentAnalysis.classification_result == 'illegal').count()
        compliant_count = db.query(DocumentAnalysis).filter(DocumentAnalysis.is_compliant == True).count()
        non_compliant_count = db.query(DocumentAnalysis).filter(DocumentAnalysis.is_compliant == False).count()
        
        return {
            'total_count': total_count,
            'legal_count': legal_count,
            'illegal_count': illegal_count,
            'compliant_count': compliant_count,
            'non_compliant_count': non_compliant_count
        }
    finally:
        db.close()