import asyncio
import json
from playwright.async_api import async_playwright
import time

async def get_stock_price(stock_code):
    """Lấy giá realtime của một mã chứng khoán"""
    browser = None
    try:
        async with async_playwright() as p:
            print(f"\n🔄 Đang tìm giá cho mã {stock_code}...")
            browser = await p.chromium.launch(
                headless=False,
                args=['--disable-dev-shm-usage', '--no-sandbox']
            )
            
            context = await browser.new_context(
                viewport={"width": 1000, "height": 1000},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            page = await context.new_page()
            
            print("🌐 Đang kết nối tới SSI...")
            await page.goto("https://iboard.ssi.com.vn/", wait_until="networkidle", timeout=60000)
            
            print("⌛ Đang đợi dữ liệu tải...")
            await page.wait_for_selector(".ag-body-viewport", timeout=60000)

            # Tìm và nhập mã chứng khoán vào ô tìm kiếm
            print(f"🔍 Đang tìm mã {stock_code}...")
            search_box = await page.wait_for_selector('input[placeholder="Nhập mã CK"]')
            await search_box.click()
            await search_box.fill(stock_code)
            await asyncio.sleep(1)  # Đợi cho kết quả tìm kiếm hiển thị
            
            # Tìm tất cả các hàng trong bảng sau khi đã lọc
            rows = await page.query_selector_all(".ag-center-cols-container .ag-row")
            stock_data = None

            # Kiểm tra hàng đầu tiên (thường là kết quả tìm kiếm)
            if len(rows) > 0:
                try:
                    row = rows[0]  # Lấy hàng đầu tiên
                    code_el = await row.query_selector(".stock-symbol")
                    if code_el:
                        code = await code_el.inner_text()
                        
                        if code.strip().upper() == stock_code.upper():
                            price_el = await row.query_selector("[col-id='lastPrice']")
                            price = await price_el.inner_text() if price_el else "N/A"
                            
                            change_el = await row.query_selector("[col-id='change']")
                            change = await change_el.inner_text() if change_el else "N/A"
                            
                            volume_el = await row.query_selector("[col-id='volume']")
                            volume = await volume_el.inner_text() if volume_el else "N/A"
                            
                            stock_data = {
                                "ma_ck": code,
                                "gia": price.strip(),
                                "thay_doi": change.strip(),
                                "klgd": volume.strip(),
                                "thoi_gian": time.strftime("%H:%M:%S")
                            }
                except Exception as e:
                    print(f"❌ Lỗi khi xử lý dữ liệu: {e}")

            if stock_data:
                print(f"✅ Đã tìm thấy giá mã {stock_code}")
                return {
                    "status": "success",
                    "data": stock_data
                }
            else:
                print(f"❌ Không tìm thấy mã {stock_code}")
                return {
                    "status": "error",
                    "message": f"Không tìm thấy mã {stock_code}"
                }

    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        if browser:
            await browser.close()

async def handle_client(reader, writer):
    try:
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        print(f"\n📱 Client {addr!r} yêu cầu: {message!r}")

        if message.startswith("STOCK "):
            stock_code = message.split()[1].strip().upper()
            result = await get_stock_price(stock_code)
        else:
            result = {
                "status": "error",
                "message": "Vui lòng nhập: STOCK <mã>"
            }
            
        writer.write(json.dumps(result).encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(
        handle_client, '127.0.0.1', 99
    )
    print('🚀 Server đang chạy tại 127.0.0.1:99')
    print('⌛ Đang đợi kết nối...')

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Đã dừng server")