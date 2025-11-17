# corpus.py
import logging
import os
import glob
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from database import engine, SessionLocal
from models import PDFFile, Fingerprint
from winnowing import WinnowingProcessor
import pdfplumber
import re
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class CorpusCreator:
    def __init__(self, k=50, w=100):
        self.winnowing = WinnowingProcessor(k=k, w=w)
        self.engine = engine

    def get_session(self) -> SessionLocal:
        return SessionLocal()

    def clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def read_pdf(self, file_path: str) -> str:
        try:
            logging.info(f"Reading PDF: {file_path}")
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text(layout=True)
                    if page_text:
                        text += page_text + "\n"
            text = re.sub(r"\n+", "\n", text).strip()
            text = re.sub(r" +", " ", text)
            return text
        except Exception as e:
            logging.error(f"Error reading PDF {file_path}: {e}")
            return ""

    def process_document(self, file_path: str) -> tuple[str, list[tuple[int, int]]]:
        if not self.check_file_exists(file_path):
            logging.info(f"File {file_path} already exists in database, skipping...")
            return "", []
        start_time = time.time()
        content = self.read_pdf(file_path)
        read_time = time.time() - start_time
        logging.info(f"Read {file_path} in {read_time:.2f}s")
        if not content:
            return "", []

        start_encode = time.time()
        fingerprints = self.winnowing.generate_fingerprints(content)
        encode_time = time.time() - start_encode
        logging.info(f"Generated {len(fingerprints)} fingerprints for {file_path} in {encode_time:.2f}s")

        return content, fingerprints

    def insert_data(self, filename: str, file_path: str, content: str, fingerprints: list[tuple[int, int]]) -> int:
        start_time = time.time()
        session = self.get_session()

        try:
            pdf_file = PDFFile(filename=filename, file_path=file_path, total_fingerprints=len(fingerprints), full_content=content)
            session.add(pdf_file)
            session.flush()

            batch_size = 1000
            for i in range(0, len(fingerprints), batch_size):
                batch = fingerprints[i : i + batch_size]
                fp_objects = [Fingerprint(pdf_id=pdf_file.pdf_id, hash_value=str(hash_val), position=pos) for hash_val, pos in batch]
                session.bulk_save_objects(fp_objects)
                session.flush()

            session.commit()
            total_time = time.time() - start_time
            logging.info(f"Inserted {filename} ({len(fingerprints)} fingerprints) in {total_time:.2f}s")
            return pdf_file.pdf_id

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Database error inserting {filename}: {str(e)}")
            raise
        except Exception as e:
            session.rollback()
            logging.error(f"Error inserting {filename}: {str(e)}")
            raise
        finally:
            session.close()

    def get_pdf_by_filename(self, filename: str) -> PDFFile | None:
        session = self.get_session()
        try:
            return session.query(PDFFile).filter(PDFFile.filename == filename).first()
        finally:
            session.close()

    def check_file_exists(self, file_path: str) -> bool:
        filename = os.path.basename(file_path)
        session = self.get_session()
        existing_file = session.query(PDFFile).filter(PDFFile.filename == filename).first()
        session.close()

        if existing_file:
            return False
        return True
            
    def save_to_databases(self, file_path: str, content: str, fingerprints: list[tuple[int, int]]) -> bool:
        try:
            filename = os.path.basename(file_path)
            session = self.get_session()
            existing_file = session.query(PDFFile).filter(PDFFile.filename == filename).first()
            session.close()

            if existing_file:
                logging.info(f"File {filename} already exists in database, skipping...")
                return False

            self.insert_data(filename, file_path, content, fingerprints)
            return True
        except Exception as e:
            logging.error(f"Error saving document {file_path}: {str(e)}")
            return False

    def process_pdf_batch(self, pdf_files: list[str]) -> None:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self.process_document, pdf_file): pdf_file for pdf_file in pdf_files}

            for future in futures:
                pdf_file = futures[future]
                try:
                    content, fingerprints = future.result()
                    if fingerprints:
                        self.save_to_databases(pdf_file, content, fingerprints)
                except Exception as e:
                    logging.error(f"Error processing {pdf_file}: {str(e)}")

    def create_corpus(self, folder_path: str):
        pdf_files = glob.glob(os.path.join(folder_path, "**/*.pdf"), recursive=True)
        if not pdf_files:
            logging.info(f"No PDF files found in {folder_path}")
            return

        logging.info(f"Found {len(pdf_files)} PDF files")

        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logging.info("Successfully connected to PostgreSQL database")

        except Exception as e:
            logging.error(f"Error connecting to database: {e}")
            return

        try:
            batch_size = 4
            with tqdm(total=len(pdf_files), desc="Processing PDFs") as pbar:
                for i in range(0, len(pdf_files), batch_size):
                    batch = pdf_files[i : i + batch_size]
                    self.process_pdf_batch(batch)
                    pbar.update(len(batch))

            logging.info("\nCorpus creation completed!")
        except KeyboardInterrupt:
            logging.info("\nProcess interrupted by user. Cleaning up...")
        except Exception as e:
            logging.error(f"\nError during corpus creation: {str(e)}")
            logging.error(traceback.format_exc())