from Student import Student
import socket
import json

class Ekalat(Student):
    def name(self):
        return "PHOMMASENG EKALAT"
    def speak(self):
        return "Toi len la: EKALAT.\nGmail: mrkoong1234@gmail.com"
    def address(self):
        return "TP.THAKHEK - KHAMMOUANE - LAO"
    def telegram_id(self):
        return "6079753756"
    def ip(self):
        # Thay đổi IP thành địa chỉ localhost vì server đang chạy trên máy local
        return "192.168.1.50"  # hoặc "localhost"
    def weather(self, city):
        try:
            # Tạo socket và kết nối đến weather server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 98))  # Kết nối đến port 98
            print("Kết nối đến weather server thành công.")

            # Gửi yêu cầu với encoding utf-8
            request = f"WEATHER {city}\n"
            client_socket.sendall(request.encode('utf-8'))
            
            # Nhận phản hồi từ server
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Server response: {response}")  # In response để debug
            try:
                response_data = json.loads(response)
                if "error" in response_data:
                    return f"❌ Lỗi: {response_data['error']}"
                else:
                    return (f"🌤️ Thời tiết tại {response_data['location']}, {response_data['country']}:\n\n"
                           f"🌡️ Nhiệt độ: {response_data['temperature']}°C\n"
                           f"☁️ Thời tiết: {response_data['weather_desc']}\n"
                           f"💧 Độ ẩm: {response_data['humidity']}%\n"
                           f"💨 Tốc độ gió: {response_data['wind_speed']} km/h")
            except json.JSONDecodeError:
                return f"❌ Phản hồi không hợp lệ từ server: {response}"
        except ConnectionRefusedError:
            return "❌ Không thể kết nối đến weather server. Vui lòng kiểm tra địa chỉ và cổng."
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
        finally:
            client_socket.close()
    def stock(self, code):
        try:
            # Tạo socket và kết nối đến server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 97))  # Kết nối đến port 97
            print("Kết nối đến server thành công.")

            # Gửi yêu cầu
            request = f"STOCK {code}\n"
            client_socket.sendall(request.encode('ascii'))
            
            # Nhận phản hồi từ server
            response = client_socket.recv(1024).decode('ascii')
            try:
                response_data = json.loads(response)
                if "error" in response_data:
                    return f"❌ Lỗi: {response_data['error']}"
                else:
                    return (f"📊 Thông tin cổ phiếu {response_data['stock_code']}:\n\n"
                            f"💰 Giá hiện tại: {response_data['current_price']}\n"
                            f"📌 Giá tham chiếu: {response_data['ref_price']}\n"
                            f"⬆️ Giá trần: {response_data['ceil_price']}\n"
                            f"⬇️ Giá sàn: {response_data['floor_price']}\n"
                            f"📈 Khối lượng GD: {response_data['total_volume']}")
            except json.JSONDecodeError:
                return f"❌ Phản hồi không hợp lệ từ server: {response}"
        except ConnectionRefusedError:
            return "❌ Không thể kết nối đến server. Vui lòng kiểm tra địa chỉ và cổng."
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
        finally:
            client_socket.close()

