import socket
from playwright.sync_api import sync_playwright

def lay_chi_tiet(stock_symbol, stock_name):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)  # Đặt headless=False để debug
        page = browser.new_page()

        # Điều hướng đến trang iBoard SSI
        page.goto("https://iboard.ssi.com.vn/", timeout=0)

        # Chờ ô chứa mã chứng khoán và nhấp vào nó
        stock_symbol_selector = f'div[role="gridcell"][col-id="stockSymbol"]:has-text("{stock_symbol}")'
        page.wait_for_selector(stock_symbol_selector)
        page.click(stock_symbol_selector)  # Nhấp vào mã chứng khoán

        # Chờ một chút để giá cổ phiếu xuất hiện
        page.wait_for_timeout(3000)  # Thay đổi thời gian nếu cần

        # Lấy giá cổ phiếu từ phần tử có class .stock-header-price
        price_element = page.wait_for_selector('.stock-header-price', timeout=15000)

        if price_element:
            # Lấy giá hiện tại
            current_price = price_element.query_selector('.text-3xl > div').inner_text() if price_element.query_selector('.text-3xl > div') else 'Không tìm thấy giá'
            
            # Lấy thêm thông tin khác
            open_price = price_element.query_selector('div.flex > div.text-color-down').inner_text() if price_element.query_selector('div.flex > div.text-color-down') else 'Không tìm thấy'
            low_price = price_element.query_selector('div.flex:nth-child(2) > div.text-color-down').inner_text() if price_element.query_selector('div.flex:nth-child(2) > div.text-color-down') else 'Không tìm thấy'
            high_price = price_element.query_selector('div.flex:nth-child(2) > div.text-color-up').inner_text() if price_element.query_selector('div.flex:nth-child(2) > div.text-color-up') else 'Không tìm thấy'
            total_volume = price_element.query_selector('div.flex:nth-child(3) > div.text-color-tertiary').inner_text() if price_element.query_selector('div.flex:nth-child(3) > div.text-color-tertiary') else 'Không tìm thấy'
            
            return {
                'current_price': current_price,
                'open_price': open_price,
                'low_price': low_price,
                'high_price': high_price,
                'total_volume': total_volume
            }
        else:
            return {'error': 'Không tìm thấy phần tử giá cổ phiếu.'}
        
    # Đóng trình duyệt trong khối finally
    browser.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 99))
    server_socket.listen(1)
    print("🔄 Server đang chạy tại 0.0.0.0 Port:99...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f'Kết nối từ {addr}')
        
        # Nhận mã chứng khoán từ client
        data = client_socket.recv(1024).decode().strip()
        stock_symbol, stock_name = data.split(',')  # Giả định client gửi mã chứng khoán và tên cổ phiếu cách nhau bằng dấu phẩy
        print(f'Nhận mã chứng khoán: {stock_symbol}, Tên cổ phiếu: {stock_name}')

        result = lay_chi_tiet(stock_symbol, stock_name)
        client_socket.send(str(result).encode())
        
        client_socket.close()

if __name__ == "__main__":
    main()
    
def start_server():
    host = '0.0.0.0'
    port = 99
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server is listening on {host}:{port}")
        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                try:
                    num1, num2 = map(float, data.split(","))
                    result = num1 + num2
                    response = f" {num1} + {num2} = {result}"
                except ValueError:
                    response = "Nhập không hợp lệ vui lòng Nhập số thứ nhất rồi nhấn enter sau đó nhập số thứ 2"
                conn.sendall(response.encode())
if __name__ =="__main__":
    start_server()