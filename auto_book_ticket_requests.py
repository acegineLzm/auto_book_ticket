# -*- coding: UTF-8 -*-
import requests
import re, json, sys, time, os
from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ======= config start =======

# Cookie
SID = ''

# FB LOGIN
# EMAIL = ''
# PASSWD = ''

BUTTONNUM = 1

# 0 is most expensive and -1 is cheapest
AREASELECT = 0

TICKETNUM = 1

ACTIVITY = ''

# LOG
LOGFILE = False
STOREVC = False

# =======  config end  =======

DOMAIN = 'https://****.com'
GAMEPATH = '/activity/game/'
CAPTCHAPATH = '/ticket/captcha?v=5a6952f818c4a'
CHECKPATH = '/ticket/check'
PAYMENTPATH = '/ticket/payment'
FACEBOOKPATH = '/login/facebook'
ORDERPAGE = '/ticket/order'

headers = {}

proxies = {
        "http": "http://127.0.0.1:8080",
        "https": "http://127.0.0.1:8080",
    }

def getCaptcha():
    resp = requests.get(url=DOMAIN+CAPTCHAPATH, headers=headers)
    with open('temp.png', 'wb') as f:
        f.write(resp.content)

def gamePage():
    buttons = []
    urls = []
    while len(buttons) == 0:
        print('waiting...')
        time.sleep(0.001)
        url = DOMAIN + GAMEPATH + ACTIVITY
        resp = requests.get(url=url, headers=headers)
        soup = bs(resp.text, 'lxml')
        buttons = soup.find_all("input", type="button")
        if buttons:
            inputTag = soup.find_all('input', {'class':'btn btn-info-filled btn-rounded'})
            for tag in inputTag:
                urls.append(tag['data-href'])
    return urls

def areaPage(url):
    resp = requests.get(url=url, headers=headers)
    areaUrlListstr = re.search(r'areaUrlList = {(.*?)};', resp.text).group(1)
    areaUrlList = [i.replace('\\', '') for i in re.findall(r'"(.*?)"', areaUrlListstr) if 'ticket' in i]
    return areaUrlList[AREASELECT]

def ticketPage(url, captcha, num):
    postdata = {
        "CSRFTOKEN": "YTdkVXplOWo2R1NodnBUVm5lQXRHU3I2eUNUV0NxSjbRCQN59Aovb1Utudz-v7rwkUCpy1R2tpH1p93TLWffDw==",
        "TicketForm[ticketPrice][{}]".format(num): TICKETNUM,
        "TicketForm[verifyCode]": captcha,
        "TicketForm[agree]": "1",
        "ticketPriceSubmit": "確認張數"
    }
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    resp = requests.post(url=url, headers=headers, data=postdata, allow_redirects=False)
    with open('order.html', 'w', encoding='utf-8') as f:
        f.write(resp.text)
    return True if resp.status_code == 302 else False

def orderPage():
    requests.get(url=DOMAIN+ORDERPAGE, headers=headers)

def ticketselect(url):
    resp = requests.get(url=url, headers=headers)
    soup = bs(resp.text, 'lxml')
    select = soup.find('select')['id']
    selectnum = select.split('_')[-1]
    return selectnum

def checkPage():
    headers['X-Requested-With'] = 'XMLHttpRequest'
    while 1:
        resp = requests.get(url=DOMAIN+CHECKPATH, headers=headers)
        print(json.loads(resp.text)['message'])
        if json.loads(resp.text)['time'] == 0:
            break
        time.sleep(3)

def paymentPage():
    requests.get(url=DOMAIN+PAYMENTPATH, headers=headers)

def printstr(string):
    print('[*] %s' % string)

# !not use
def login_facebook():
    global SID
    driver = webdriver.Firefox()
    driver.get(DOMAIN)
    elem = WebDriverWait(driver, 5).until(
           EC.presence_of_element_located((By.ID, "loginFacebook"))
      )
    driver.get(DOMAIN+FACEBOOKPATH)
    elem = driver.find_element_by_id("email")
    elem.send_keys(EMAIL)
    elem = driver.find_element_by_id("pass")
    elem.send_keys(PASSWD)
    elem.send_keys(Keys.RETURN)
    try:
        elem = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "logout"))
        )
        printstr('Login success')
        cookies = driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == 'SID':
                SID = cookie['value']
        # with open('cookie', 'w') as f:
        #     f.write(SID)
        driver.quit()
    except:
        print("[!] Login failed")
        driver.quit()
        sys.exit()

def setHeader():
    global headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0",
        "Cookie": "_ga=GA1.2.1777440068.1516644170; SID={}; CSRFTOKEN=b90726ecb9c2d7535dbe83e250a14aed87c079a5s%3A88%3A%22YTdkVXplOWo2R1NodnBUVm5lQXRHU3I2eUNUV0NxSjbRCQN59Aovb1Utudz-v7rwkUCpy1R2tpH1p93TLWffDw%3D%3D%22%3B; _gid=GA1.2.720235991.1516879519; lang=1a73f0317e76f38c9adb36e69bdc73613602f560s%3A5%3A%22zh_tw%22%3B".format(
            SID)
    }

def isLogin():
    global SID
    with open('cookie', 'r') as f:
        SID = f.read().strip()
    setHeader()
    resp = requests.get(url=DOMAIN + '/order', headers=headers)
    soup = bs(resp.text, 'lxml')
    logout = soup.find('a', {'id':'logout'})
    return True if logout else False

def main():
    # if not isLogin():
    #     printstr('FB logining...')
    #     login_facebook()
    #     setHeader()
    setHeader()
    printstr('Get verification code...')
    getCaptcha()
    time.sleep(2)
    captcha = input('>>> verify code : ')
    printstr('Get button...')
    urls = gamePage()
    printstr('Choose area...')
    ticketurl = areaPage(DOMAIN+urls[BUTTONNUM-1])
    printstr('Submit order...')
    num = ticketselect(DOMAIN+ticketurl)
    ticketSuccess = ticketPage(DOMAIN+ticketurl, captcha, num)
    while not ticketSuccess:
        print('[!] Fail! Again get verification code...')
        getCaptcha()
        captcha = input('>>> verify code : ')
        ticketSuccess = ticketPage(DOMAIN + ticketurl, captcha, num)
    orderPage()
    checkPage()
    paymentPage()
    printstr('Success! Please visit the main station for orders.')

    if not STOREVC:
        if os.path.exists("temp.png"):
            os.remove("temp.png")
    if not LOGFILE:
        if os.path.exists("order.html"):
            os.remove("order.html")

if __name__ == '__main__':
    main()
