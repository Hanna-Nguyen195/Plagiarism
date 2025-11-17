# drop_tables.py
from database import engine
from models import Base

print("Đang xóa bảng pdf_files và fingerprints ...")
Base.metadata.drop_all(engine)
print("Đã xóa thành công 2 bảng!")
