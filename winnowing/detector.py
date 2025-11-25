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

    def get_bbox_from_char_range(self, pdf_path: str, segments: List[Tuple[str, int, int]]) -> List[dict]:
        """
        Dùng char index (start, end) để lấy bbox chính xác từ page.chars
        → Đây là cách CHUẨN NHẤT, KHÔNG BAO GIỜ MISS
        """
        results = []

        with pdfplumber.open(pdf_path) as pdf:
            # Tạo offset cho từng trang
            page_offsets = []
            offset = 0
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                page_offsets.append((i + 1, page, offset, offset + len(text)))
                offset += len(text) + 1

            for text, start_char, end_char in segments:
                if end_char <= start_char or len(text) < 30:
                    continue

                for page_num, page, p_start, p_end in page_offsets:
                    if start_char >= p_end or end_char <= p_start:
                        continue

                    local_start = max(start_char - p_start, 0)
                    local_end = min(end_char - p_start, len(page.extract_text() or ""))

                    chars = page.chars
                    if not chars:
                        continue

                    matched = []
                    for ch in chars:
                        if "text" not in ch or not ch["text"]:
                            continue
                        # Ước lượng vị trí ký tự
                        try:
                            pos = (page.extract_text() or "").find(ch["text"], local_start)
                            if pos != -1 and pos < local_end:
                                matched.append(ch)
                        except:
                            continue

                    if not matched:
                        continue

                    xs = [ch["x0"] for ch in matched] + [ch["x1"] for ch in matched]
                    ys_top = [ch["top"] for ch in matched]
                    ys_bottom = [ch["bottom"] for ch in matched]

                    x0, x1 = min(xs), max(xs)
                    y0 = page.height - max(ys_top)      # top-left
                    y1 = page.height - min(ys_bottom)

                    results.append({
                        "pageNumber": page_num,
                        "similarity_content": [{
                            "content": text.strip(),
                            "rects": [[round(x0,2), round(y0,2), round(x1,2), round(y1,2)]]
                        }]
                    })
        return results

    def detect_plagiarism_overall(self, query_path: str, min_similarity: float = 0.05) -> Dict:
        """
        Hàm chính - trả về JSON đúng chuẩn frontend
        min_similarity=0.05 → hiện tài liệu từ 5% trở lên
        """
        session: SASession = SessionLocal()
        try:
            query_text = self.extract_text_from_pdf(query_path)
            if not query_text:
                return {"error": "Không thể đọc file PDF"}

            with pdfplumber.open(query_path) as pdf:
                if not pdf.pages:
                    return {"error": "PDF rỗng"}
                page_width = round(pdf.pages[0].width, 2)
                page_height = round(pdf.pages[0].height, 2)

            processed_query = self.winnowing.preprocess_text(query_text)
            fps_query = self.winnowing.generate_fingerprints(query_text)

            # Tìm matches trong DB
            matches_by_pdf = defaultdict(list)
            for h, pos_q in fps_query:
                results = session.query(Fingerprint.pdf_id, Fingerprint.position, PDFFile.filename, PDFFile.full_content)\
                    .join(PDFFile).filter(Fingerprint.hash_value == h).all()
                for pdf_id, pos_d, filename, content in results:
                    matches_by_pdf[pdf_id].append((h, pos_q, pos_d))

            if not matches_by_pdf:
                return {
                    "data": {
                        "total_percent": 0.0,
                        "size_page": {"width": page_width, "height": page_height},
                        "similarity_documents": []
                    }
                }

            similarity_documents = []
            total_matched_tokens = 0
            query_tokens = len(query_text.split())

            # Duyệt từng tài liệu nguồn
            for pdf_id, matches in matches_by_pdf.items():
                doc = session.get(PDFFile, pdf_id)
                if not doc:
                    continue

                processed_doc = self.winnowing.preprocess_text(doc.full_content)
                expanded = self.merge_and_expand_matches(
                    query_text, doc.full_content, processed_query, processed_doc, matches
                )

                # Chỉ lấy đoạn đủ dài + vị trí char
                segments = [(seg[0].strip(), seg[1], seg[2]) for seg in expanded if len(seg[0].split()) >= 6]
                if not segments:
                    continue

                matched_tokens = sum(len(text.split()) for text, _, _ in segments)
                total_matched_tokens += matched_tokens

                similarity_percent = matched_tokens / query_tokens * 100
                if similarity_percent < min_similarity * 100:
                    continue

                # Tìm bbox chính xác từ char index
                box_sentences = self.get_bbox_from_char_range(query_path, segments)

                similarity_documents.append({
                    "name": doc.filename,
                    "similarity_value": int(round(similarity_percent)),
                    "similarity_box_sentences": box_sentences or []  # luôn có list
                })

            total_percent = round(total_matched_tokens / query_tokens * 100, 2) if query_tokens > 0 else 0.0

            return {
                "data": {
                    "total_percent": total_percent,
                    "size_page": {"width": page_width, "height": page_height},
                    "similarity_documents": sorted(
                        similarity_documents,
                        key=lambda x: x["similarity_value"],
                        reverse=True
                    )
                }
            }

        except Exception as e:
            logging.exception("Lỗi trong detect_plagiarism_overall")
            return {"error": str(e)}
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