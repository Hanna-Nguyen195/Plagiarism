# import random
# import re
# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import SimpleDocTemplate, Paragraph
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# import random
# SRC_PDF = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\doccheck\bc_23-4.pdf"
# OUTPUT_PDF_ORIGINAL = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\doccheck\test_case_original.pdf"
# OUTPUT_PDF_SHUFFLED = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\doccheck\test_case_shuffled.pdf"
# PDF_ID = 2
# START_IDX = 2
# N_SENTENCES = 20

# FONT_FILE = r"C:\Windows\Fonts\Arial.ttf"  
# FONT_SIZE = 12
# MM2PT = 72.0 / 25.4
# MARGIN_PT = 20 * MM2PT

# def make_pdf_reportlab(text, out_path):
#     pdfmetrics.registerFont(TTFont('Arial', r"C:\Windows\Fonts\arial.ttf"))
#     doc = SimpleDocTemplate(out_path, pagesize=A4)
#     styles = getSampleStyleSheet()
#     style = styles['Normal']
#     style.fontName = 'Arial'
#     style.fontSize = 12
#     style.leading = 16
#     para = Paragraph(text, style)
#     doc.build([para])
#     print(f"Xuất PDF với ReportLab: {out_path}")


# file_path = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\doccheck\bc_23-4.pdf"

# import re
# import string
# # testcase1: Lấy trong database 20 câu liên tiếp và bên ngoài 20 câu 
# output_tc1 = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\winnowing\database_testcase\test_case_1.pdf"
# text1 ="Ta có thể thấy, trong kiến trúc monolithic truyền thống, toàn bộ ứng dụng được đóng gói thành một khối duy nhất. Điều này có nghĩa là mỗi lần triển khai, toàn bộ ứng dụng phải được build lại từ đầu, kiểm thử và triển khai nguyên khối. Đây là một quy trình tương đối đơn giản, không đòi hỏi quá nhiều về tự động hóa. Tuy nhiên, khi chuyển sang kiến trúc microservices, mọi thứ trở nên phức tạp hơn nhiều. Hãy tưởng tượng ứng dụng của bạn bây giờ không còn là một ngôi nhà một tầng nữa, mà là một tòa chung cư cao tầng với hàng chục, hàng trăm căn hộ. Việc xây dựng và duy tu những tòa nhà như vậy chắc chắn cần một quy trình chặt chẽ, đồng bộ và tự động hóa cao.Thứ nhất, do các service phát triển độc lập, việc tích hợp chúng trở nên cực kỳ khó khăn. Không có cơ chế rõ ràng để đảm bảo chúng làm việc đúng với nhau. Đó là lý do tại sao chúng ta cần Continuous Integration (CI) - tích hợp liên tục. Qua đó, mỗi thay đổi trong code sẽ được build, kiểm tra và tích hợp ngay lập tức. Nếu có lỗi xảy ra ở một service nào đó, nó sẽ được phát hiện ngay từ đầu, tránh ảnh hưởng lan rộng. CI là một phương pháp phát triển phần mềm trong đó nhà phát triển liên tục hợp nhất nhánh làm việc của họ vào nhánh chính thường xuyên (ít nhất mỗi ngày một lần) để đảm bảo tính tương thích trong phát triển. Ngày nay có nhiều công cụ cung cấp dịch vụ này, ví dụ như Jenkins, Travis, TeamCity. CI được kích hoạt khi ai đó đẩy một commit lên hệ thống quản lý phiên bản phân tán (DVCS) như Github, điều này kích hoạt công cụ CI. CI sau đó sẽ build ứng dụng từ mã nguồn và chạy các bài kiểm thử. Nếu có bất kỳ vấn đề nào, mã sẽ không được triển khai và các lỗi phải được khắc phục. Nếu mã vượt qua tất cả cấu hình build và kiểm thử, nó sẽ được triển khai lên DVCS. Theo K. Gallaba và S. McIntosh , CI thường được chia thành ba bước (xem hình dưới). Đầu tiên, tạo job để đảm bảo chương trình sẽ biên dịch được, để không lãng phí thời gian của người review. Ngày 16/10, Sở Xây dựng Khánh Hòa cho biết: Do mưa lớn kéo dài, sáng cùng ngày, trên tuyến đường Phạm Văn Đồng (đoạn gần khu vực Lương Sơn, phường Bắc Nha Trang) đã xảy ra sạt lở đất, đá. Hạt quản lý đường bộ Nha Trang 1 đã đặt rào chắn, biển cảnh báo và sẽ thu dọn khi trời ngớt mưa. Cùng thời điểm, nhiều tuyến đường tại Nha Trang bị ngập cục bộ do nước thoát không kịp, đặc biệt là đường 23 Tháng 10, 2 Tháng 4 và Nguyễn Tất Thành. Mưa lớn khiến nhiều phương tiện bị chết máy, gây ùn tắc cục bộ. Sở Xây dựng khuyến cáo người dân hạn chế đi lại qua các khu vực ngập sâu, sạt lở để đảm bảo an toàn. Trong khi đó, Sở Nông nghiệp và Môi trường Khánh Hoà đề nghị các địa phương rà soát khu vực xung yếu, nguy cơ sạt lở, lũ quét, ngập lụt; chủ động sơ tán người dân, bảo vệ sản xuất, gia cố lồng bè, ao nuôi thủy sản và hoa màu. Các lực lượng chức năng được yêu cầu chốt chặn tại khu vực ngập sâu, nước chảy xiết để đảm bảo an toàn cho người dân. Sau khi nhận tin báo, lực lượng thuộc Trạm Cảnh sát giao thông Đakrông, Công an xã Tà Rụt phối hợp lực lượng quản lý đường bộ khẩn trương có mặt tại hiện trường để phân luồng, khắc phục bảo đảm lưu thông trên tuyến. Hiện chính quyền địa phương đang chỉ đạo các đơn vị liên quan lập chốt chặn tại các điểm xung yếu để cảnh báo, nhắc nhở người và phương tiện lưu thông đảm bảo an toàn giao thông."
# make_pdf_reportlab(text1, output_tc1)

# text2 = "Ta có thể thấy, trong kiến trúc monolithic truyền thống, toàn bộ ứng dụng được đóng gói thành một khối duy nhất. Điều này có nghĩa là mỗi lần triển khai, toàn bộ ứng dụng phải được build lại từ đầu, kiểm thử và triển khai nguyên khối. Ngày 16/10, Sở Xây dựng Khánh Hòa cho biết: Do mưa lớn kéo dài, sáng cùng ngày, trên tuyến đường Phạm Văn Đồng (đoạn gần khu vực Lương Sơn, phường Bắc Nha Trang) đã xảy ra sạt lở đất, đá. Hạt quản lý đường bộ Nha Trang 1 đã đặt rào chắn, biển cảnh báo và sẽ thu dọn khi trời ngớt mưa. Đây là một quy trình tương đối đơn giản, không đòi hỏi quá nhiều về tự động hóa. Tuy nhiên, khi chuyển sang kiến trúc microservices, mọi thứ trở nên phức tạp hơn nhiều. Cùng thời điểm, nhiều tuyến đường tại Nha Trang bị ngập cục bộ do nước thoát không kịp, đặc biệt là đường 23 Tháng 10, 2 Tháng 4 và Nguyễn Tất Thành. Mưa lớn khiến nhiều phương tiện bị chết máy, gây ùn tắc cục bộ. Sở Xây dựng khuyến cáo người dân hạn chế đi lại qua các khu vực ngập sâu, sạt lở để đảm bảo an toàn. Hãy tưởng tượng ứng dụng của bạn bây giờ không còn là một ngôi nhà một tầng nữa, mà là một tòa chung cư cao tầng với hàng chục, hàng trăm căn hộ. Việc xây dựng và duy tu những tòa nhà như vậy chắc chắn cần một quy trình chặt chẽ, đồng bộ và tự động hóa cao.Thứ nhất, do các service phát triển độc lập, việc tích hợp chúng trở nên cực kỳ khó khăn. Không có cơ chế rõ ràng để đảm bảo chúng làm việc đúng với nhau. Trong khi đó, Sở Nông nghiệp và Môi trường Khánh Hoà đề nghị các địa phương rà soát khu vực xung yếu, nguy cơ sạt lở, lũ quét, ngập lụt; chủ động sơ tán người dân, bảo vệ sản xuất, gia cố lồng bè, ao nuôi thủy sản và hoa màu. Các lực lượng chức năng được yêu cầu chốt chặn tại khu vực ngập sâu, nước chảy xiết để đảm bảo an toàn cho người dân. Đó là lý do tại sao chúng ta cần Continuous Integration (CI) - tích hợp liên tục. Qua đó, mỗi thay đổi trong code sẽ được build, kiểm tra và tích hợp ngay lập tức. Nếu có lỗi xảy ra ở một service nào đó, nó sẽ được phát hiện ngay từ đầu, tránh ảnh hưởng lan rộng. Sau khi nhận tin báo, lực lượng thuộc Trạm Cảnh sát giao thông Đakrông, Công an xã Tà Rụt phối hợp lực lượng quản lý đường bộ khẩn trương có mặt tại hiện trường để phân luồng, khắc phục bảo đảm lưu thông trên tuyến. CI là một phương pháp phát triển phần mềm trong đó nhà phát triển liên tục hợp nhất nhánh làm việc của họ vào nhánh chính thường xuyên (ít nhất mỗi ngày một lần) để đảm bảo tính tương thích trong phát triển. Ngày nay có nhiều công cụ cung cấp dịch vụ này, ví dụ như Jenkins, Travis, TeamCity. CI được kích hoạt khi ai đó đẩy một commit lên hệ thống quản lý phiên bản phân tán (DVCS) như Github, điều này kích hoạt công cụ CI. Hiện chính quyền địa phương đang chỉ đạo các đơn vị liên quan lập chốt chặn tại các điểm xung yếu để cảnh báo, nhắc nhở người và phương tiện lưu thông đảm bảo an toàn giao thông. CI sau đó sẽ build ứng dụng từ mã nguồn và chạy các bài kiểm thử. Nếu có bất kỳ vấn đề nào, mã sẽ không được triển khai và các lỗi phải được khắc phục. Nếu mã vượt qua tất cả cấu hình build và kiểm thử, nó sẽ được triển khai lên DVCS. Theo K. Gallaba và S. McIntosh , CI thường được chia thành ba bước (xem hình dưới). Đầu tiên, tạo job để đảm bảo chương trình sẽ biên dịch được, để không lãng phí thời gian của người review."
# output_tc2 = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\winnowing\database_testcase\test_case_2.pdf"
# make_pdf_reportlab(text2, output_tc2)



# output_tc3 = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\winnowing\database_testcase\test_case_3.pdf"
# text3 ="Ta có thể thấy, trong kiến trúc monolithic truyền thống, toàn bộ ứng dụng được đóng gói thành một Sau khi nhận tin báo, lực lượng thuộc Trạm Cảnh sát giao thông Đakrông, Công an xã Tà Rụt phối hợp lực lượng quản lý đường bộ khẩn trương có mặt tại hiện trường để phân luồng"
# make_pdf_reportlab(text3, output_tc3)

# output_tc4 = r"D:\Code\Python\Project_Python\DNU_PlagiarismChecker\winnowing\database_testcase\test_case_4.pdf"
# text4 ="Ta có thể thấy, trong kiến trúc monolithic truyền thống, toàn bộ ứng dụng được đóng gói thành một Sau khi nhận tin báo, lực lượng thuộc Trạm Cảnh sát giao thông Đakrông"
# make_pdf_reportlab(text4, output_tc4)
text4 ="Ta có thể thấy, trong kiến trúc monolithic truyền thống, toàn bộ ứng dụng được đóng gói thành một Sau khi nhận tin báo, lực lượng thuộc Trạm Cảnh sát giao thông Đakrông"
import re
clean_segment = re.sub(r"[^\w]", "", text4)
# print("Original length:", clean_segment)
print(len(clean_segment))

text2 = "Ta có thể thấy, trong kiến trúc monolithic truyền thống, toàn bộ ứng dụng được đóng gói thành một"
import re
text2_slove = re.sub(r"[^\w]", "", text2)
print(len(text2_slove))

print(len(text2) ,len(text4))