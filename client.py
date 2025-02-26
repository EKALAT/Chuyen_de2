import asyncio
import json

async def get_stock_price(stock_code):
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 99)
        writer.write(f"STOCK {stock_code}".encode())
        await writer.drain()

        data = await reader.read(1024)
        writer.close()
        await writer.wait_closed()

        return json.loads(data.decode())
    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")
        return None

def print_stock_info(data):
    if data and data["status"] == "success":
        stock = data["data"]
        print(f"""
📊 THÔNG TIN REALTIME
━━━━━━━━━━━━━━━━━━━━━
🔖 Mã CP: {stock['ma_ck']}
💰 Giá: {stock['gia']}
📈 Thay đổi: {stock['thay_doi']}
⏰ Thời gian: {stock['thoi_gian']}
━━━━━━━━━━━━━━━━━━━━━""")
    else:
        print(f"❌ Lỗi: {data['message'] if data else 'Không thể kết nối server'}")

async def main():
    print("🔄 Đang kết nối đến server...")
    
    while True:
        print("\n📝 Nhập mã chứng khoán (hoặc 'q' để thoát):")
        stock_code = input(">> ").strip().upper()
        
        if stock_code.lower() == 'q':
            print("👋 Tạm biệt!")
            break
            
        if not stock_code:
            print("❌ Vui lòng nhập mã chứng khoán!")
            continue
            
        print(f"🔄 Đang lấy giá mã {stock_code}...")
        result = await get_stock_price(stock_code)
        print_stock_info(result)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Đã dừng chương trình")
