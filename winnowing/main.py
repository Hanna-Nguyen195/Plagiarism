# main.py
import os
import time
from corpus import CorpusCreator
from detector import WinnowingPlagiarismDetector
import utils
import logging
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
    k = int(k_input) 
    w = int(w_input) 
    if choice == "1":
        folder_path = input("Enter folder path: ").strip()
        if not folder_path:
            folder_path = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\database\DoAn8"
        creator = CorpusCreator(k=k, w=w)
        creator.create_corpus(folder_path)
    elif choice == "2":
        query_file = input("Enter query PDF path: ").strip()
        if not os.path.exists(query_file):
            print("File not found!")
            return
        starttime = time.time()
        detector = WinnowingPlagiarismDetector(k=k, w=w)
        results = detector.detect_plagiarism_overall(query_file)
        endtime = time.time()
        print(f"Plagiarism detection completed in {endtime - starttime:.2f} seconds.")
        utils.print_overall_results(results)
        save_report = input("Save summary report to PDF? (y/n): ").lower().strip()
        if save_report == "y":
            if results:
                base_name = os.path.splitext(os.path.basename(query_file))[0]
                output_dir = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\winnowing\result_testcase"
                output_path = os.path.join(output_dir, f"{base_name}.json")
                utils.export_results_to_json(results, output_path)
                print("Report generated:", output_path)
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