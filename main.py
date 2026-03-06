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
        attendance = conn.get_attendance()
        today = datetime.now().date()

        if attendance:
            for record in attendance:
                # Chỉ xử lý các bản ghi trong ngày hiện tại
                if record.timestamp.date() == today:
                    user_name = user_dict.get(record.user_id, "Unknown")
                    payload = {
                        "user_id": record.user_id,
                        "user_name": user_name,
                        "timestamp": record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    # Đẩy dữ liệu lên Google Sheets
                    try:
                        requests.post(WEBHOOK_URL, json=payload, timeout=10)
                    except:
                        pass # Bỏ qua nếu lỗi gửi để tiếp tục bản ghi tiếp theo

        conn.enable_device()

    except:
        pass # Không in lỗi ra màn hình
    finally:
        if conn:
            try:
                conn.disconnect()
            except:
                pass

if __name__ == "__main__":
    main()