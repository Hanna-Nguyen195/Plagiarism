# detector.py
import logging
import re
import time
from typing import Dict, List, Tuple
from collections import defaultdict
import pdfplumber
from sqlalchemy.orm import Session as SASession
from database import SessionLocal
from models import PDFFile, Fingerprint
from winnowing import WinnowingProcessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class WinnowingPlagiarismDetector:
    def __init__(self, k=50, w=100):
        self.k = k
        self.w = w
        self.winnowing = WinnowingProcessor(k=k, w=w)

    def find_matches(self, fp1: List[Tuple[str, int]], fp2: List[Tuple[str, int]]) -> List[Tuple[str, int, int]]:
        fp2_dict = defaultdict(list)
        for h, p in fp2:
            fp2_dict[h].append(p)
        matches = []
        for h, p1 in fp1:
            if h in fp2_dict:
                for p2 in fp2_dict[h]:
                    matches.append((h, p1, p2))
        return matches


    def map_processed_to_original(self, processed_pos: int, processed_text: str, original_text: str) -> int:
        processed_count = 0
        original_pos = 0
        while original_pos < len(original_text) and processed_count < processed_pos:
            char = original_text[original_pos].lower()
            if re.match(r"\w", char):
                processed_count += 1
            original_pos += 1
        while original_pos < len(original_text) and not re.match(r"\w", original_text[original_pos].lower()):
            original_pos += 1
        return original_pos

    def merge_and_expand_matches(
        self, original_text1: str, original_text2: str, processed_text1: str, processed_text2: str, matches: List[Tuple[int, int, int]]
    ) -> List[Tuple[str, int, int, int, int]]:
        if not matches:
            return []

        segments = []
        for h, pos1, pos2 in sorted(matches, key=lambda x: x[1]):
            start1_proc = pos1
            start2_proc = pos2

            while start1_proc > 0 and start2_proc > 0 and processed_text1[start1_proc - 1] == processed_text2[start2_proc - 1]:
                start1_proc -= 1
                start2_proc -= 1

            end1_proc = start1_proc + self.k
            end2_proc = start2_proc + self.k
            while end1_proc < len(processed_text1) and end2_proc < len(processed_text2) and processed_text1[end1_proc] == processed_text2[end2_proc]:
                end1_proc += 1
                end2_proc += 1

            start1_orig = self.map_processed_to_original(start1_proc, processed_text1, original_text1)
            end1_orig = self.map_processed_to_original(end1_proc, processed_text1, original_text1)
            start2_orig = self.map_processed_to_original(start2_proc, processed_text2, original_text2)
            end2_orig = self.map_processed_to_original(end2_proc, processed_text2, original_text2)

            segment_text = original_text1[start1_orig:end1_orig].strip()
            if len(segment_text) >= self.k // 2:
                segments.append((segment_text, start1_orig, end1_orig, start2_orig, end2_orig))

        if not segments:
            return []

        segments.sort(key=lambda x: x[1])
        merged = []
        current_text, s1, e1, s2, e2 = segments[0]
        for text, start1, end1, start2, end2 in segments[1:]:
            if start1 < e1 + self.k:
                e1 = max(e1, end1)
                e2 = max(e2, end2)
                current_text = original_text1[s1:e1].strip()
            else:
                merged.append((current_text, s1, e1, s2, e2))
                current_text, s1, e1, s2, e2 = text, start1, end1, start2, end2
        merged.append((current_text, s1, e1, s2, e2))
        return merged

    def calculate_similarity(
        self, original_text1: str, original_text2: str, processed_text1: str, processed_text2: str, matches: List[Tuple[str, int, int, int, int]]
    ) -> Dict:
        len1, len2 = len(processed_text1), len(processed_text2)
        orig_len1, orig_len2 = len(original_text1), len(original_text2)
        if len1 < self.k or len2 < self.k:
            return {
                "similarity": 0.0,
                "matches": [],
                "matched_chars": 0,
                "text1_length": orig_len1,
                "text2_length": orig_len2,
            }

        # marched_chars là tổng số ký tự trùng khớp trong các đoạn đã mở rộng
        # original lengths là độ dài ban đầu của văn bản
        # processed lengths là độ dài của văn bản đã được xử lý
        matched_chars = sum(end1 - start1 for _, start1, end1, _, _ in matches)
        similarity = (matched_chars / orig_len1) * 100 if orig_len1 > 0 else 0.0
        logging.info(
            f"Matched chars: {matched_chars}, Original Text1 length: {orig_len1}, Original Text2 length: {orig_len2}, Similarity: {similarity:.2f}%"
        )

        return {
            "similarity": similarity,
            "matches": matches,
            "matched_chars": matched_chars,
            "text1_length": orig_len1,
            "text2_length": orig_len2,
        }

    def detect_plagiarism_overall(self, query_path: str) -> Dict:
        session: SASession = SessionLocal()
        try:
            query_text = self.extract_text_from_pdf(query_path)
            if not query_text:
                return {"error": "Không thể trích xuất nội dung từ file PDF"}

            processed_query = self.winnowing.preprocess_text(query_text)
            fps_query = self.winnowing.generate_fingerprints(query_text)

            # Tìm tất cả hash trùng trong database
            all_matches = []
            for h, pos_q in fps_query:
                db_matches = session.query(Fingerprint.pdf_id, Fingerprint.position).filter(Fingerprint.hash_value == str(h)).all()

                for pdf_id, pos_d in db_matches:
                    all_matches.append((h, pos_q, pos_d, pdf_id))

            if not all_matches:
                return {
                    "overall_similarity": 0.0,
                    "total_matched_chars": 0,
                    "text_length": len(query_text),
                    "matches": [],
                }

            # Gom match theo từng pdf để mở rộng đoạn
            matches_by_pdf = defaultdict(list)
            for h, pos_q, pos_d, pdf_id in all_matches:
                matches_by_pdf[pdf_id].append((h, pos_q, pos_d))

            merged_matches = []
            for pdf_id, matches in matches_by_pdf.items():
                doc = session.get(PDFFile, pdf_id)
                if not doc:
                    continue
                processed_doc = self.winnowing.preprocess_text(doc.full_content)
                expanded = self.merge_and_expand_matches(
                    query_text, doc.full_content, processed_query, processed_doc, matches
                )
                for text, s1, e1, s2, e2 in expanded:
                    merged_matches.append({
                        "text": text,
                        "start": s1,
                        "end": e1,
                        "pdf_id": pdf_id,
                        "filename": doc.filename
                    })

            # Gộp các vùng trùng lặp trên văn bản query để tránh đếm 2 lần
            merged_intervals = []
            for m in sorted(merged_matches, key=lambda x: x["start"]):
                if not merged_intervals or m["start"] > merged_intervals[-1][1]:
                    merged_intervals.append([m["start"], m["end"]])
                else:
                    merged_intervals[-1][1] = max(merged_intervals[-1][1], m["end"])

            # Đếm tổng số ký tự chữ/số (loại bỏ ký tự đặc biệt) trong các đoạn trùng
            total_matched_chars = 0
            for s, e in merged_intervals:
                segment = query_text[s:e]
                # Loại bỏ ký tự không phải chữ/số
                # clean_segment = re.sub(r"[^\w]", " ", segment)
                tokens = segment.split()
                total_matched_chars += len(tokens)

            # Tính độ dài "sạch" của toàn văn bản query (chỉ chữ/số)
            # clean_query_text = re.sub(r"[^\w]", " ", query_text)
            all_text_query = query_text.split()
            clean_text_length = len(all_text_query)

            overall_similarity = (total_matched_chars / clean_text_length) * 100 if clean_text_length > 0 else 0

            logging.info(
                f"Tổng số ký tự trùng: {total_matched_chars}/{(clean_text_length)} ({overall_similarity:.2f}%)"
            )

            return {
                "overall_similarity": round(overall_similarity, 2),
                "total_matched_chars": total_matched_chars,
                "text_length": len(query_text),
                "matches": merged_matches,
            }

        finally:
            session.close()


    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            start_time = time.time()
            texts = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text(layout=True)
                    if page_text:
                        texts.append(page_text)
            text = "\n".join(texts)
            text = re.sub(r"\n+", "\n", text).strip()
            text = re.sub(r" +", " ", text)
            end_time = time.time()
            logging.info(f"Extracted text from {pdf_path} in {end_time - start_time:.2f}s ({len(text)} chars)")
            return text
        except Exception as e:
            logging.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return ""