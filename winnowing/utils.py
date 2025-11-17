import json
import re
import logging
from typing import Dict, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def print_single_results(results: Dict):
    """Hiển thị kết quả khi so sánh giữa 2 văn bản cụ thể"""
    print("\n" + "=" * 50)
    print("ANALYSIS RESULTS")
    print("=" * 50)
    print(f"Similarity: {results['similarity']:.1f}%")
    print(f"Total matched characters: {results['matched_chars']:,}")
    print(f"Text 1 length: {results['text1_length']:,}")
    print(f"Text 2 length: {results['text2_length']:,}")

    if results.get("matches"):
        print("\nMATCHED SEGMENTS:")
        print("-" * 50)
        for i, (text, start1, end1, start2, end2) in enumerate(results["matches"], 1):
            print(f"\nSegment {i} (Length: {len(text):,} characters):")
            print(f"  Position in text 1: {start1:,} - {end1:,}")
            print(f"  Position in text 2: {start2:,} - {end2:,}")
            preview = re.sub(r"\s+", " ", text[:200]) + "..." if len(text) > 200 else text
            print(f"  Content: {preview}")
    else:
        print("\nNo matched segments found.")


def print_overall_results(result: Dict):
    """In kết quả tổng thể khi kiểm tra 1 văn bản với toàn bộ DB"""
    print("\n" + "=" * 70)
    print("PLAGIARISM CHECK — OVERALL DATABASE RESULT")
    print("=" * 70)

    if "error" in result:
        print(result["error"])
        return

    overall = result.get("overall_similarity", 0.0)
    matched = result.get("total_matched_chars", 0)
    total = result.get("text_length", 1)

    print(f"\nTổng độ trùng lặp: {overall:.2f}%")
    print(f"Tổng số ký tự trùng: {matched:,} / {total:,}")

    matches = result.get("matches", [])
    if not matches:
        print("\nKhông phát hiện đoạn trùng lặp nào trong cơ sở dữ liệu.")
        return

    print(f"\nPhát hiện {len(matches)} đoạn trùng lặp trong cơ sở dữ liệu:\n")
    for i, m in enumerate(matches[:10], 1):  # chỉ in top 10 đoạn đầu
        snippet = (m['text'][:200] + "...") if len(m['text']) > 200 else m['text']
        print(f"{i}. [Tài liệu: {m['filename']}]")
        print(f"   Vị trí trong file kiểm tra: {m['start']} - {m['end']}")
        print(f"   Nội dung: {re.sub(r'\\s+', ' ', snippet)}\n")


def export_results_to_json(result: Dict, output_path: str):
    """Xuất kết quả tổng thể sang file JSON"""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"Kết quả đã được lưu vào file: {output_path}")
    except Exception as e:
        logging.error(f"Lỗi khi lưu file JSON: {e}")


