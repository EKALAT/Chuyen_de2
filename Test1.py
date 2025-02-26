from playwright.sync_api import sync_playwright
import csv
import time

def fetch_all_stock_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Chạy ẩn
        page = browser.new_page()

        # Truy cập trang iBoard SSI
        page.goto("https://iboard.ssi.com.vn/", timeout=60000)
        time.sleep(5)  # Chờ trang tải

        # Tạo danh sách lưu dữ liệu
        stock_data = []

        # Lấy tất cả mã chứng khoán
        stock_symbols = page.query_selector_all(".ag-pinned-left-cols-container .ag-cell")
        stock_codes = [symbol.inner_text().strip() for symbol in stock_symbols]

        # Cuộn để tải hết dữ liệu
        scroll_container = page.locator(".ag-body-viewport")
        page.evaluate("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
        time.sleep(3)

        # Lấy tất cả hàng dữ liệu
        rows = page.query_selector_all(".ag-center-cols-container .ag-row")

        for i, row in enumerate(rows):
            if i >= len(stock_codes):
                break  # Nếu số lượng hàng > mã chứng khoán, dừng lại

            stock_code = stock_codes[i]  # Mã chứng khoán

            # Lấy dữ liệu từ các cột
            def get_cell(col_index):
                cell = row.query_selector(f"[aria-colindex='{col_index}']")
                return cell.inner_text().strip() if cell else "N/A"

            high_price = get_cell(10)  # Giá cao nhất
            low_price = get_cell(11)   # Giá thấp nhất
            total_volume = get_cell(18)  # Tổng khối lượng

            # Thêm vào danh sách
            stock_data.append([stock_code, high_price, low_price, total_volume])

        browser.close()

        # Xuất dữ liệu ra CSV
        with open("stock_data.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Mã CK", "Giá Cao", "Giá Thấp", "Tổng Khối Lượng"])
            writer.writerows(stock_data)

        print("✅ Đã lưu dữ liệu vào stock_data.csv")

if __name__ == "__main__":
    fetch_all_stock_data()
