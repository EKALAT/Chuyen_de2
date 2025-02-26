import socket
import json
import requests
from datetime import datetime

class WeatherServer:
    def __init__(self, host='0.0.0.0', port=98):
        self.host = host
        self.port = port
        # API key đã được xác nhận hoạt động
        self.api_key = "ed60fcfbd110ee65c7150605ea8aceea"
        self.server_socket = None

    def start(self):
        try:
            # Tạo socket server
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Cho phép tái sử dụng địa chỉ và cổng
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind socket với host và port
            self.server_socket.bind((self.host, self.port))
            # Lắng nghe kết nối
            self.server_socket.listen(5)
            print(f"Weather Server đang chạy tại {self.host}:{self.port}")

            while True:
                # Chấp nhận kết nối từ client
                client_socket, client_address = self.server_socket.accept()
                print(f"Kết nối mới từ {client_address}")
                
                try:
                    # Nhận dữ liệu từ client
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        continue

                    # Xử lý yêu cầu
                    if data.startswith("WEATHER"):
                        city = data.split()[1]
                        response = self.get_weather(city)
                        # Gửi phản hồi về client
                        client_socket.sendall(json.dumps(response).encode('utf-8'))
                    else:
                        error_response = {"error": "Lệnh không hợp lệ"}
                        client_socket.sendall(json.dumps(error_response).encode('utf-8'))

                except Exception as e:
                    print(f"Lỗi khi xử lý yêu cầu: {str(e)}")
                    error_response = {"error": str(e)}
                    client_socket.sendall(json.dumps(error_response).encode('utf-8'))
                finally:
                    client_socket.close()

        except Exception as e:
            print(f"Lỗi server: {str(e)}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def get_weather(self, city):
        try:
            # Xử lý tên thành phố
            city = city.replace("_", " ")  # Thay thế dấu _ bằng khoảng trắng
            
            # Mapping đầy đủ 63 tỉnh thành Việt Nam
            city_mapping = {
                # Miền Bắc
                "HaNoi": "Hanoi,VN",
                "HaiPhong": "Hai Phong,VN",
                "HaGiang": "Ha Giang,VN",
                "CaoBang": "Cao Bang,VN",
                "BacKan": "Bac Kan,VN",
                "TuyenQuang": "Tuyen Quang,VN",
                "LaoCai": "Lao Cai,VN",
                "DienBien": "Dien Bien Phu,VN",
                "LaiChau": "Lai Chau,VN",
                "SonLa": "Son La,VN",
                "YenBai": "Yen Bai,VN",
                "HoaBinh": "Hoa Binh,VN",
                "ThaiNguyen": "Thai Nguyen,VN",
                "LangSon": "Lang Son,VN",
                "QuangNinh": "Ha Long,VN",
                "BacGiang": "Bac Giang,VN",
                "PhuTho": "Viet Tri,VN",
                "VinhPhuc": "Vinh Yen,VN",
                "BacNinh": "Bac Ninh,VN",
                "HaiDuong": "Hai Duong,VN",
                "HungYen": "Hung Yen,VN",
                "ThaiBinh": "Thai Binh,VN",
                "HaNam": "Phu Ly,VN",
                "NamDinh": "Nam Dinh,VN",
                "NinhBinh": "Ninh Binh,VN",

                # Miền Trung
                "ThanhHoa": "Thanh Hoa,VN",
                "NgheAn": "Vinh,VN",
                "HaTinh": "Ha Tinh,VN",
                "QuangBinh": "Dong Hoi,VN",
                "QuangTri": "Dong Ha,VN",
                "ThuaThienHue": "Hue,VN",
                "DaNang": "Da Nang,VN",
                "QuangNam": "Tam Ky,VN",
                "QuangNgai": "Quang Ngai,VN",
                "BinhDinh": "Quy Nhon,VN",
                "PhuYen": "Tuy Hoa,VN",
                "KhanhHoa": "Nha Trang,VN",
                "NinhThuan": "Phan Rang-Thap Cham,VN",
                "BinhThuan": "Phan Thiet,VN",
                
                # Tây Nguyên
                "KonTum": "Kon Tum,VN",
                "GiaLai": "Pleiku,VN",
                "DakLak": "Buon Ma Thuot,VN",
                "DakNong": "Gia Nghia,VN",
                "LamDong": "Da Lat,VN",

                # Miền Nam
                "BinhPhuoc": "Dong Xoai,VN",
                "TayNinh": "Tay Ninh,VN",
                "BinhDuong": "Thu Dau Mot,VN",
                "DongNai": "Bien Hoa,VN",
                "BaRiaVungTau": "Vung Tau,VN",
                "HoChiMinh": "Ho Chi Minh City,VN",
                "LongAn": "Tan An,VN",
                "TienGiang": "My Tho,VN",
                "BenTre": "Ben Tre,VN",
                "TraVinh": "Tra Vinh,VN",
                "VinhLong": "Vinh Long,VN",
                "DongThap": "Cao Lanh,VN",
                "AnGiang": "Long Xuyen,VN",
                "KienGiang": "Rach Gia,VN",
                "CanTho": "Can Tho,VN",
                "HauGiang": "Vi Thanh,VN",
                "SocTrang": "Soc Trang,VN",
                "BacLieu": "Bac Lieu,VN",
                "CaMau": "Ca Mau,VN",

                # Các thành phố lớn (alias)
                "SaiGon": "Ho Chi Minh City,VN",
                "TPHCM": "Ho Chi Minh City,VN",
                "HCM": "Ho Chi Minh City,VN",
                "Hue": "Hue,VN",
                "DaLat": "Da Lat,VN",
                "NhaTrang": "Nha Trang,VN",
                "VungTau": "Vung Tau,VN",
                "BienHoa": "Bien Hoa,VN",
                "HaLong": "Ha Long,VN",
                "HaiPhong": "Hai Phong,VN",
                "CanTho": "Can Tho,VN",
                "QuyNhon": "Quy Nhon,VN",
                "DongHoi": "Dong Hoi,VN",
                "Vinh": "Vinh,VN",
                "PhanThiet": "Phan Thiet,VN",
                "BuonMaThuot": "Buon Ma Thuot,VN",
                "ThuDuc": "Thu Duc,VN",
                "MyTho": "My Tho,VN",
                "LongXuyen": "Long Xuyen,VN",
                "RachGia": "Rach Gia,VN"
            }
            
            # Kiểm tra và thay thế tên thành phố nếu có trong mapping
            if city in city_mapping:
                city = city_mapping[city]
            
            # Gọi API OpenWeather với lang=vi và in url để debug
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric&lang=vi"
            print(f"Calling API: {url}")
            response = requests.get(url)
            data = response.json()
            print(f"API Response: {data}")  # In response để debug

            if response.status_code == 200:
                return {
                    "location": data["name"],
                    "country": data["sys"]["country"],
                    "temperature": round(data["main"]["temp"]),
                    "weather_desc": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": round(data["wind"]["speed"] * 3.6, 1)  # Chuyển đổi m/s sang km/h
                }
            else:
                # Thêm gợi ý cách viết tên thành phố và danh sách một số thành phố hỗ trợ
                return {
                    "error": f"Không tìm thấy thông tin thời tiết cho {city}. \n"
                            f"Vui lòng thử lại với một trong các thành phố sau:\n\n"
                            f"Miền Bắc: Hanoi, HaiPhong, HaLong, ThaiNguyen...\n"
                            f"Miền Trung: NgheAn, HaTinh, DongHoi, DaNang...\n"
                            f"Miền Nam: HoChiMinh, CanTho, VungTau, DaLat...\n\n"
                            f"Ví dụ: /student Ekalat weather NgheAn"
                }

        except Exception as e:
            return {"error": f"Lỗi khi lấy thông tin thời tiết: {str(e)}"}

if __name__ == "__main__":
    weather_server = WeatherServer()
    weather_server.start() 