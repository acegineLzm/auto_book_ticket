from selenium import webdriver
import sched
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, sys, re, os
from lxml import etree
from PIL import Image
import json
#import tesserocr


# ====== config start =======

buttonNum = 2  # 提前选择好要点击第几个“立即订票”按钮

ticketNum = 1  # 购票数量

FORMATTIME = "2018 01 23 10:20:00" # 运行脚本后执行登录，这里定时为：到时自动刷新寻找“立即订票按钮”，定时在倒计时阶段

EMAIL = ""
PASSWD = ""

# ====== config end =======


domain = "https://****.com"
event_path = "/activity/detail/2018_GLAY"
PAYMENT_URL = domain + "/ticket/payment"
ORDER_URL = domain + "/ticket/order"
CHECK_URL = domain + "/ticket/check"
cookies = []
captcha = ""

def printformat(str1):
    print("[*] %s" % str1)

def login_facebook(driver, email, passwd):
    global cookies
    printformat("open ****.com")
    driver.get(domain)
    # elem = WebDriverWait(driver, 10).until(
    #        EC.presence_of_element_located((By.ID, "loginFacebook"))
    #   )
    printformat("login facebook")
    driver.get("https://****.com/login/facebook")
    elem = driver.find_element_by_id("email")
    elem.send_keys(email)
    elem = driver.find_element_by_id("pass")
    elem.send_keys(passwd)
    elem.send_keys(Keys.RETURN)
    try:
        elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "logout"))
        )
        printformat('Login success')
        cookies = driver.get_cookies()
    except:
        print("[!] Login failed")
        driver.quit()
        sys.exit()

def go_event_page(driver, path):
    printformat("open activity/detail")
    driver.get(domain + path)
    return

def find_bookButton_path(driver):
    elems = driver.find_elements_by_css_selector("a[target='_new']")
    url = ""
    for elem in elems:
        if "/activity/game" in elem.get_attribute("href"):
            url = elem.get_attribute("href")
            break
    return url

def buy_ticket(driver, path, buttonNum):
    buttons = []
    while len(buttons) == 0:
        print("finding \"Buy tickets now\" bottons...")
        time.sleep(0.001)
        response = requests.get(domain + path)
        soup = BeautifulSoup(response.content, "html.parser")
        buttons = soup.find_all("input", type="button")
    button = buttons[buttonNum-1]
    printformat("open activity/area")
    driver.get(domain + button.get("data-href"))
    return driver.execute_script("return areaUrlList[$(\"li[class='select_form_b'] > a:first\").attr(\"id\")]")

def confirm_ticket(driver, path):
   printformat("open ticket/ticket")
   driver.get(domain + path)
   select = Select(driver.find_element_by_css_selector("select"))
   select.select_by_index(1)
   driver.find_element_by_id("TicketForm_agree").send_keys(Keys.SPACE)
   i = input(">>> verify code : ")
  while i == "q":
       elem = driver.find_element_by_id("yw0")
       elem.click()
       i = input("verify code : ")

   elem = driver.find_element_by_id("TicketForm_verifyCode")
   elem.send_keys(i)
   printformat("open ticket/order")
   elem.send_keys(Keys.RETURN)
   return

# 验证码提前，确定订票时自动填写
# def confirm_ticket(driver, path):
#     global cookies
#     printformat("open ticket/ticket")
#     cd = {}
#     print(cookies)
#     for cookie in cookies:
#         cd[cookie['name']] = cookie['value']
#         if cookie['name'] == 'CSRFTOKEN':
#             csrftoken = re.search(r'88%3A%22(.*?)%22', cookie['value']).group(1)
#     print(cd)
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0",
#         "Referer": domain+path,
#         "Content-Type": "application/x-www-form-urlencoded",
#         "Cookie": "_ga=GA1.2.1777440068.1516644170; SID={}; CSRFTOKEN=b90726ecb9c2d7535dbe83e250a14aed87c079a5s%3A88%3A%22YTdkVXplOWo2R1NodnBUVm5lQXRHU3I2eUNUV0NxSjbRCQN59Aovb1Utudz-v7rwkUCpy1R2tpH1p93TLWffDw%3D%3D%22%3B; lang=1a73f0317e76f38c9adb36e69bdc73613602f560s%3A5%3A%22zh_tw%22%3B".format(cd['SID']),
#         "Upgrade-Insecure-Requests": "1",
#     }

#     posturl = domain + path

#     datas = {
#         "CSRFTOKEN": "YTdkVXplOWo2R1NodnBUVm5lQXRHU3I2eUNUV0NxSjbRCQN59Aovb1Utudz-v7rwkUCpy1R2tpH1p93TLWffDw%3D%3D",
#         "TicketForm[ticketPrice][01]": ticketNum,
#         "TicketForm[verifyCode]": captcha,
#         "TicketForm[agree]": "1",
#         "ticketPriceSubmit": "確認張數"
#     }
#     response = requests.post(url=posturl, headers=headers, data=datas)
#     print(response.status_code)
#     with open('order.html', 'w') as f:
#         f.write(response.text)
#     if response.status_code == 200:
#         driver.quit()
#         sys.exit()

#     printformat("start ticket/order")
#     s.get(ORDER_URL)

#     while 1:
#         printformat("start ticket/check")
#         response = s.get(CHECK_URL)
#         print(response.text)
#         time.sleep(5)
#         if json.loads(response.text)['time'] == 0:
#             break

#     printformat("start ticket/payment")
#     response = s.get(PAYMENT_URL)

#     if str(response.url).startswith(PAYMENT_URL):
#         root = etree.HTML(response.text)
#         ticket_ID_list = root.xpath("//div[@class='fcBlue']/text()")
#         detail_list = root.xpath("//table[@id='cartList']/tbody/tr/td/text()")
#         print("\nsuccessful!!!\n\nticketID : " + ticket_ID_list[0].encode("utf-8"))
#         for detail in detail_list:
#             print(detail)

def getCaptcha():
    s = requests.session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    current_milli_time = lambda: int(round(time.time() * 1000))
    getcapUrl = 'https://****.com/ticket/captcha?refresh=1&_=' + str(current_milli_time)
    resp = s.get(getcapUrl)
    hashstr = re.search(r'v=(.*?)"', resp.text).group(1)
    captchaUrl = 'https://****.com/ticket/captcha?v=' + hashstr
    png = s.get(captchaUrl)
    print(s.cookies)
    with open('temp.png', 'wb') as f:
        f.write(png.content)

def waited_funcs(url, driver):
    href = buy_ticket(driver, url[len(domain):], buttonNum)
    if href:
        confirm_ticket(driver, href)
    else:
        print("[!] Fail to select area!")
        sys.exit()

def main():
    global captcha
    s = sched.scheduler(time.time, time.sleep)
    driver = webdriver.Firefox()
    login_facebook(driver, EMAIL, PASSWD)
    getCaptcha()
    captcha = input(">>> verify code : ")
    go_event_page(driver, event_path)
    url = find_bookButton_path(driver)
    printformat('click "Buy Ticket"')

    timestamp = time.mktime(time.strptime(FORMATTIME, "%Y %m %d %H:%M:%S"))
    # print(str(time.strptime(FORMATTIME, "%Y %m %d %H:%M:%S")) + " begin to find button")
    s.enterabs(timestamp, 0, waited_funcs, kwargs={'url': url, 'driver': driver})
    s.run()

    if os.path.exists("./temp.png"):
       os.remove("./temp.png")

# def ocr():
#     p1 = Image.open('temp.png')
#     code = tesserocr.image_to_text(p1)
#     print(code.strip())

if __name__ == "__main__":
    main()