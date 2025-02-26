import asyncio
from playwright.async_api import async_playwright, TimeoutError
import json
import logging
import nest_asyncio

# Thiết lập logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cho phép lồng event loops
nest_asyncio.apply()

async def lay_chi_tiet(stock_symbol):
    async with async_playwright() as playwright:
        browser = None
        try:
            # Thay đổi thành hiển thị browser và thêm các options
            browser = await playwright.chromium.launch(
                headless=False,  # Hiển thị browser
                args=['--start-maximized']  # Mở cửa sổ to
            )
            
            context = await browser.new_context(
                viewport={'width': 1000, 'height': 1000}
            )
            
            page = await context.new_page()

            # Tăng timeout và thêm thông báo
            print(f"🌐 Đang mở trang web để tìm mã {stock_symbol}...")
            await page.goto("https://iboard.ssi.com.vn/", timeout=60000)  # Tăng timeout lên 60s
            
            # Đợi lâu hơn để trang load hoàn toàn
            await asyncio.sleep(5)  # Tăng thời gian đợi lên 5s

            print(f"🔍 Đang tìm kiếm mã {stock_symbol}...")
            stock_selector = f'div[role="gridcell"][col-id="stockSymbol"]:has-text("{stock_symbol}")'
            await page.wait_for_selector(stock_selector, timeout=60000)  # Tăng timeout
            await page.click(stock_selector)
            
            # Đợi để thông tin hiển thị
            await asyncio.sleep(3)

            print("📊 Đang lấy thông tin giá...")
            price_element = await page.wait_for_selector('.stock-header-price', timeout=30000)

            if price_element:
                # Lấy các thông tin cần thiết
                current_price = await price_element.query_selector('.text-3xl > div')
                current_price = await current_price.inner_text() if current_price else 'N/A'
                
                ref_price = await price_element.query_selector('div.flex > div.text-color-down')
                ref_price = await ref_price.inner_text() if ref_price else 'N/A'
                
                ceil_price = await price_element.query_selector('div.flex:nth-child(2) > div.text-color-up')
                ceil_price = await ceil_price.inner_text() if ceil_price else 'N/A'
                
                floor_price = await price_element.query_selector('div.flex:nth-child(2) > div.text-color-down')
                floor_price = await floor_price.inner_text() if floor_price else 'N/A'
                
                total_volume = await price_element.query_selector('div.flex:nth-child(3) > div.text-color-tertiary')
                total_volume = await total_volume.inner_text() if total_volume else 'N/A'

                # Đợi thêm 2 giây để người dùng có thể thấy kết quả
                await asyncio.sleep(2)
                
                # Tạo response data
                response_data = {
                    "stock_code": stock_symbol,
                    "current_price": current_price,
                    "ref_price": ref_price,
                    "ceil_price": ceil_price,
                    "floor_price": floor_price,
                    "total_volume": total_volume
                }
                return json.dumps(response_data)
            else:
                return json.dumps({"error": f"Không tìm thấy thông tin giá của mã {stock_symbol}"})

        except Exception as e:
            logger.error(f"Lỗi: {str(e)}")
            return json.dumps({"error": f"Có lỗi xảy ra khi tìm kiếm mã {stock_symbol}: {str(e)}"})

        finally:
            if browser:
                # Đợi 1 giây trước khi đóng browser
                await asyncio.sleep(1)
                await browser.close()

async def handle_client(reader, writer):
    try:
        data = await reader.read(1024)
        message = data.decode('ascii')
        addr = writer.get_extra_info('peername')
        
        logger.info(f"Received {message!r} from {addr!r}")

        # Xử lý yêu cầu STOCK
        if message.startswith('STOCK '):
            stock_code = message.split()[1].strip()
            response = await lay_chi_tiet(stock_code)
        else:
            response = json.dumps({"error": "Invalid command. Use: STOCK <code>"})

        writer.write(response.encode('ascii'))
        await writer.drain()
        
        writer.close()
        await writer.wait_closed()
        
    except Exception as e:
        logger.error(f"Error handling client: {str(e)}")
        error_response = json.dumps({"error": str(e)})
        writer.write(error_response.encode('ascii'))
        await writer.drain()
        writer.close()

async def main():
    server = await asyncio.start_server(
        handle_client, '0.0.0.0', 97
    )

    addr = server.sockets[0].getsockname()
    print(f'🚀 Server đang chạy tại {addr}')

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server đã dừng bởi người dùng")
    except Exception as e:
        logger.error(f"Lỗi server: {e}")
        print(f"❌ Lỗi: {e}")
