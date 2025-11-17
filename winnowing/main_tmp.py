# main.py
import os
import shutil
import time
from corpus import CorpusCreator
from detector import WinnowingPlagiarismDetector
import utils
import logging
import glob
from PyPDF2 import PdfReader 
from concurrent.futures import ProcessPoolExecutor, as_completed

def process_pdf(query_file, detector, output_dir):
    import time, os, utils
    from PyPDF2 import PdfReader

    starttime = time.time()
    reader = PdfReader(query_file)
    num_pages = len(reader.pages)
    if num_pages > 40:
        return {"file": query_file, "skipped": True, "reason": f"{num_pages} pages"}
    
    results = detector.detect_plagiarism_overall(query_file)
    endtime = time.time()
    results['time_to_check'] = endtime - starttime
    
    base_name = os.path.splitext(os.path.basename(query_file))[0]
    output_path = os.path.join(output_dir, f"{base_name}.json")
    utils.export_results_to_json(results, output_path)
    return {"file": query_file, "time": endtime - starttime, "output": output_path}

def main():
    print("=== PLAGIARISM DETECTION PIPELINE USING WINNOWING ===")
    print("Options:")
    print("1. Push data to database (build corpus from folder)")
    print("2. Check plagiarism between one document and database")
    choice = input("Enter choice (1/2): ").strip()

    # k_input = input("k-gram size (default 50): ").strip()
    # w_input = input("Window size (default 100): ").strip()
    k_input = "50"
    w_input = "30"
    k = int(k_input) if k_input.isdigit() else 50
    w = int(w_input) if w_input.isdigit() else 100

    if choice == "1":
        folder_path = input("Enter folder path: ").strip()
        if not folder_path:
            folder_path = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\database\DoAn8"
        creator = CorpusCreator(k=k, w=w)
        creator.create_corpus(folder_path)
    elif choice == "2":
        finish_dir = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\winnowing\finish"
        folder_file_check = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\winnowing\database_testcase"
        pdf_files = glob.glob(os.path.join(folder_file_check, "**/*.pdf"), recursive=True)
        output_dir = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\winnowing\result_testcase"
        detector = WinnowingPlagiarismDetector(k=k, w=w)
        with ProcessPoolExecutor(max_workers=2) as executor:  
            futures = {executor.submit(process_pdf, f, detector, output_dir): f for f in pdf_files}
            for future in as_completed(futures):
                result = future.result()
                if result.get("skipped"):
                    print(f"Skipped {result['file']}: {result['reason']}")
                else:
                    print(f"Processed {result['file']} in {result['time']:.2f} seconds. Output: {result['output']}")
                shutil.move(result['file'], finish_dir)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    
    required_libs = ["pdfplumber", "reportlab", "sqlalchemy", "psycopg2", "tqdm"]
    missing_libs = []
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            missing_libs.append(lib)

    if missing_libs:
        print("Missing libraries. Install with:")
        print("pip install " + " ".join(missing_libs))
    else:
        main()
        
        
# check performance, độ chính xác, test bằng tay và test bằng code --> phần trăm giống nhau, 4 -5 test case
# thời gian chạy, test trên đồ ấn thực tế 60 trang --> check cả quá trình bn s
# cần tích hợp vào backend.