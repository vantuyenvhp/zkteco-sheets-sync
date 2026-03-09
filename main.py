import requests
from zk import ZK
from datetime import datetime

# Cấu hình Webhook và IP
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxq6sHIqE_NmNk2Cs47-t0oPQkgFeQ4FAJg1YCvBxiKoc_RQ2ukOzSAFPHJYXWAOhDk/exec"
IP_ADDRESS = '115.79.199.64'

def main():
    # Giữ nguyên các tham số tối ưu để chạy ổn định trên Cloud/Colab
    zk = ZK(IP_ADDRESS, port=4370, timeout=20, password=0, force_udp=True, ommit_ping=True)
    conn = None

    try:
        conn = zk.connect()
        conn.disable_device()

        # Lấy danh sách người dùng và dữ liệu chấm công
        users = conn.get_users()
        user_dict = {user.user_id: user.name for user in users}
        
        # Sắp xếp dữ liệu chấm công theo thời gian tăng dần để đảm bảo lấy được bản ghi sớm nhất trước
        attendance = sorted(conn.get_attendance(), key=lambda x: x.timestamp)
        
        today = datetime.now().date()
        
        # Tập hợp để lưu trữ những ID đã được đẩy lên Google Sheet trong ngày hôm nay
        processed_users = set()

        if attendance:
            for record in attendance:
                # 1. Chỉ xử lý các bản ghi trong ngày hiện tại
                if record.timestamp.date() == today:
                    user_id = record.user_id
                    
                    # 2. Kiểm tra xem user_id này đã được ghi nhận trước đó chưa
                    if user_id not in processed_users:
                        user_name = user_dict.get(user_id, "Unknown")
                        payload = {
                            "user_id": user_id,
                            "user_name": user_name,
                            "timestamp": record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        # Đẩy dữ liệu lên Google Sheets
                        try:
                            requests.post(WEBHOOK_URL, json=payload, timeout=10)
                            # 3. Sau khi gửi thành công, thêm ID vào danh sách đã xử lý để bỏ qua các lần sau
                            processed_users.add(user_id)
                        except:
                            pass 

        conn.enable_device()

    except:
        pass 
    finally:
        if conn:
            try:
                conn.disconnect()
            except:
                pass

if __name__ == "__main__":
    main()
