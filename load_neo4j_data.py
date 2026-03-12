import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from system.database_loader import TrafficLawQADataLoader

def load_data():
    load_dotenv()
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD")

    if not uri or not password:
        print("Lỗi: Không tìm thấy NEO4J_URI hoặc NEO4J_PASSWORD trong file .env!")
        return

    print("Đang kết nối đến Neo4j...")
    loader = TrafficLawQADataLoader(uri, (user, password))

    # Xóa database cũ
    print("Xóa dữ liệu cũ (nếu có)...")
    loader.clear_database()

    # Tạo vector index
    print("Tạo Vector Index mới...")
    loader.create_vector_index()

    # Load file dữ liệu
    data_path = "data/processed/violations_100.json"
    print(f"Bắt đầu load dữ liệu từ {data_path}...")
    
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    violations = data.get("violations", [])
    print(f"Tìm thấy {len(violations)} vi phạm. Bắt đầu đẩy lên Neo4j...")

    success_count = 0
    with loader.driver.session() as session:
        for idx, item in enumerate(violations):
            try:
                session.execute_write(loader.import_data, item)
                success_count += 1
                if success_count % 50 == 0:
                    print(f"Đã load {success_count}/{len(violations)} dữ liệu...")
            except Exception as e:
                print(f"Lỗi khi load item {item.get('id')}: {e}")

    print(f"\n✅ Nạp dữ liệu thành công {success_count}/{len(violations)} dòng vào Neo4j!")
    loader.driver.close()

if __name__ == "__main__":
    load_data()
