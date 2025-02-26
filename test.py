from playwright.sync_api import sync_playwright

EXCLUDED_STOCKS = {"VNXALL", "VNINDEX", "VN30", "HNXUPCOMIND", "HNXINDEX", "HNX30", "HNXIndex", "HNXUpcomIndex"}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Hiển thị giao diện để gỡ lỗi
    context = browser.new_context(viewport={"width": 1000, "height": 1000})  # Cấu hình viewport lớn
    page = context.new_page()
    page.goto("https://iboard.ssi.com.vn/")
    
    # Chờ cho dữ liệu tải
    page.wait_for_selector(".ag-body-viewport")
    
    # Lấy danh sách mã chứng khoán
    stocks = page.locator(".ag-pinned-left-cols-container .ag-cell").all_inner_texts()
    
    # Lọc bỏ khoảng trắng, phần tử rỗng và các mã chứng khoán không mong muốn
    filtered_stocks = [stock.strip() for stock in stocks if stock.strip() and stock.strip() not in EXCLUDED_STOCKS]

    # In danh sách kèm số thứ tự
    print(f"Đã lọc, còn {len(filtered_stocks)} mã chứng khoán:")
    for index, stock in enumerate(filtered_stocks, start=1):
        print(f"{index}. {stock}")
    
    browser.close()
