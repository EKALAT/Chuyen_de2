import asyncio
from playwright.async_api import async_playwright, TimeoutError
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import nest_asyncio
import logging

# Thiết lập logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cho phép lồng event loops
nest_asyncio.apply()

# Cài đặt Token Telegram Bot
TELEGRAM_TOKEN = "7705072328:AAElGoUVLaXNnbwsMyBg59tWOCXNdVtHkz4"

async def lay_chi_tiet(stock_symbol):
    async with async_playwright() as playwright:
        browser = None
        try:
            # Khởi tạo browser với chế độ hiển thị
            browser = await playwright.chromium.launch(
                headless=False,  # Hiển thị trình duyệt
                args=['--start-maximized']  # Mở cửa sổ to
            )
            
            # Tạo context với kích thước cửa sổ lớn
            context = await browser.new_context(
                viewport={'width': 1000, 'height': 1000}
            )
            
            page = await context.new_page()

            # Điều hướng đến trang web
            await page.goto("https://iboard.ssi.com.vn/", timeout=30000)
            await asyncio.sleep(2)  # Đợi trang load

            # Tìm và click vào mã chứng khoán
            stock_selector = f'div[role="gridcell"][col-id="stockSymbol"]:has-text("{stock_symbol}")'
            await page.wait_for_selector(stock_selector)
            await page.click(stock_selector)
            await asyncio.sleep(2)  # Đợi sau khi click

            # Lấy thông tin từ phần tử .stock-header-price
            price_element = await page.wait_for_selector('.stock-header-price', timeout=15000)

            if price_element:
                # Lấy giá hiện tại
                current_price = await price_element.query_selector('.text-3xl > div')
                current_price = await current_price.inner_text() if current_price else 'Không tìm thấy giá'
                
                # Lấy thêm thông tin khác
                open_price = await price_element.query_selector('div.flex > div.text-color-down')
                open_price = await open_price.inner_text() if open_price else 'Không tìm thấy'
                
                low_price = await price_element.query_selector('div.flex:nth-child(2) > div.text-color-down')
                low_price = await low_price.inner_text() if low_price else 'Không tìm thấy'
                
                high_price = await price_element.query_selector('div.flex:nth-child(2) > div.text-color-up')
                high_price = await high_price.inner_text() if high_price else 'Không tìm thấy'
                
                total_volume = await price_element.query_selector('div.flex:nth-child(3) > div.text-color-tertiary')
                total_volume = await total_volume.inner_text() if total_volume else 'Không tìm thấy'

                # Đợi 3 giây để người dùng có thể thấy dữ liệu
                await asyncio.sleep(3)

                # Tạo message response
                message = f"📊 Thông tin cổ phiếu {stock_symbol}:\n\n"
                message += f"💰 Giá hiện tại: {current_price}\n"
                message += f"📈 Giá mở cửa: {open_price}\n"
                message += f"⬆️ Cao nhất: {high_price}\n"
                message += f"⬇️ Thấp nhất: {low_price}\n"
                message += f"📊 Khối lượng: {total_volume}"

                # Đợi thêm 2 giây trước khi đóng browser
                await asyncio.sleep(2)
                return message
            else:
                return f"❌ Không tìm thấy thông tin giá của mã {stock_symbol}"

        except Exception as e:
            logger.error(f"Lỗi: {str(e)}")
            return f"❌ Có lỗi xảy ra khi tìm kiếm mã {stock_symbol}"

        finally:
            if browser:
                await asyncio.sleep(1)  # Đợi 1 giây trước khi đóng
                await browser.close()

async def stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if len(context.args) == 0:
            await update.message.reply_text(
                "📝 Vui lòng nhập mã cổ phiếu\n"
                "Cách dùng: /stock <mã cp>\n"
                "Ví dụ: /stock VNM",
                parse_mode="Markdown"
            )
            return

        stock_code = context.args[0].upper()
        status_message = await update.message.reply_text(
            f"⏳ Đang mở trình duyệt để tìm thông tin cổ phiếu {stock_code}...",
            parse_mode="Markdown"
        )

        result = await lay_chi_tiet(stock_code)
        await status_message.edit_text(result)
        
    except Exception as e:
        logger.error(f"Lỗi trong stock_command: {e}")
        error_message = "❌ Có lỗi xảy ra, vui lòng thử lại sau"
        if 'status_message' in locals():
            await status_message.edit_text(error_message)
        else:
            await update.message.reply_text(error_message)

def main():
    try:
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("stock", stock_command))
        print("🤖 Bot đã sẵn sàng!")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Lỗi khi khởi động bot: {e}")
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
