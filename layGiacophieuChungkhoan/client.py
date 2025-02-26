import socket

def get_stock_price(stock_symbol, stock_name):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect(('127.0.0.1', 99))
        # Gửi mã chứng khoán và tên cổ phiếu cách nhau bằng dấu phẩy
        client_socket.send(f"{stock_symbol},{stock_name}".encode())
        
        # Nhận kết quả từ server
        response = client_socket.recv(1024).decode()
        return response
    
    except Exception as e:
        return {'error': str(e)}
    
    finally:
        client_socket.close()

if __name__ == "__main__":
    stock_symbol = input("Nhập mã chứng khoán: ")
    stock_name = input("Nhập tên cổ phiếu: ")  # Nhập tên cổ phiếu nếu cần
    price = get_stock_price(stock_symbol, stock_name)
    print(f'Giá chứng khoán: {price}')