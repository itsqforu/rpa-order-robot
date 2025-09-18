from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images."""
    open_robot_order_website()
    orders = get_orders()
    for order in orders:
        fill_the_form(order)
    archive_receipts()

def open_robot_order_website():
    """Navigates to the given URL."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Downloads the orders CSV file from an URL."""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    orders = library.read_table_from_csv(
        "orders.csv", columns=["Order number","Head","Body","Legs","Address"]
        )
    return orders

def close_annoying_modal():
    """Closes the pop up."""
    page = browser.page()
    page.click("button:text('I guess so...')")

def fill_the_form(order):
    """Fills the order form from the orders.csv."""
    close_annoying_modal()
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.check(f'input[type="radio"][value="{order["Body"]}"]')
    page.fill('input[type="number"]', order["Legs"])
    page.fill("#address", order["Address"])
    page.click("#preview")
    click_until_no_alert(page)
    pdf = store_receipt_as_pdf(order["Order number"])
    screenshot = screenshot_robot(order["Order number"])
    embed_screenshot_to_receipt(screenshot, pdf)
    page.click("#order-another")

def click_until_no_alert(page):
    while True:
        page.click("#order")
        if page.query_selector(".alert.alert-danger") is None:
            break
    
def store_receipt_as_pdf(order_number):
    """Stores the order receipt as PDF."""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(receipt_html, f"output/receipts/order_{order_number}_receipt.pdf")
    return f"output/receipts/order_{order_number}_receipt.pdf"

def screenshot_robot(order_number):
    """Take a screenshot of the robot."""
    page = browser.page()
    page.screenshot(path=f"output/screenshots/robot_{order_number}.png")
    return f"output/screenshots/robot_{order_number}.png"

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed the robot screenshot to the receipt PDF file."""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(screenshot, pdf_file, pdf_file)

def archive_receipts():
    """Create a ZIP file of receipt PDF files."""
    lib = Archive()
    lib.archive_folder_with_zip('output/receipts', 'receipts.zip')

