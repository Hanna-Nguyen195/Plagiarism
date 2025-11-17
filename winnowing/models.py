# models.py
from sqlalchemy import Column, Integer, String, BigInteger, Index, Text, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PDFFile(Base):
    __tablename__ = "pdf_files"
    pdf_id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    total_fingerprints = Column(Integer, default=0)
    full_content = Column(Text)

class Fingerprint(Base):
    __tablename__ = "fingerprints"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pdf_id = Column(Integer, ForeignKey("pdf_files.pdf_id"), nullable=False)
    hash_value = Column(String(64), nullable=False)
    position = Column(Integer, nullable=False)

    __table_args__ = (
        Index("idx_pdf_id", "pdf_id"),
        Index("idx_pdf_hash", "pdf_id", "hash_value"),
    )