# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
import time
import pickle
import base64


from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from mouse import move, click
from zheye import zheye
from tools.yundama_requests import YDMHttp


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com']

    def parse(self, response):
        pass

    def detail_parse(self, response):
        pass

    def start_requests(self):
        chrome_option = Options()
        chrome_option.add_argument("--disable-extensions")
        chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        browser = webdriver.Chrome(executable_path="/home/zgf/chromedriver", chrome_options=chrome_option)
        try:
            browser.maximize_window()
        except:
            pass
        browser = webdriver.Chrome(executable_path="/home/zgf/chromedriver", chrome_options=chrome_option)
        browser.get("https://www.zhihu.com/signin")
        browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys(Keys.CONTROL + "a")
        browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys('18218082132')
        browser.find_element_by_css_selector('.SignFlow-password input').send_keys(Keys.CONTROL + "a")
        browser.find_element_by_css_selector('.SignFlow-password input').send_keys('zh199206')
        browser.find_element_by_css_selector('.Button.SignFlow-submitButton').click()
        time.sleep(2)
        browser.find_element_by_css_selector('.Button.SignFlow-submitButton').click()
        time.sleep(10) # 防止网页没有加载成功
        login_success = False
        while not login_success:
            try:
                notify_ele = browser.find_element_by_class_name('Popover PushNotifications AppHeader-notifications')
                login_success = True
            except:
                login_success = True
        try:
            english_captcha_element = browser.find_element_by_class_name('Captcha-englishImg')
        except:
            english_captcha_element = None
        try:
            chinese_captcha_element = browser.find_element_by_class_name('Captcha-chineseImg')
        except:
            chinese_captcha_element = None
        if chinese_captcha_element:
            ele_position = chinese_captcha_element.location
            x_relative = ele_position['x']
            y_relative = ele_position['y']
            browser_navigation_panel_height = browser.execute_script(
                'return window.outerHeight - window.innerHeight;'
            )
            base64_text = chinese_captcha_element.get_attribute("src")
            code = base64_text.replace("data:image/jpg;base64,", "").replace("%0A", "")
            fh = open("yzm_cn.jpeg", 'wb')
            fh.write(base64.b64decode(code))
            fh.close()
            z = zheye()
            positions = z.Recognize('yzm_cn.jpeg')
            last_position = []
            if len(positions) ==2:
                if positions[0][1] > positions[1][1]:
                    last_position.append([positions[1][1], positions[1][0]])
                    last_position.append([positions[0][1], positions[0][0]])
                else:
                    last_position.append([positions[0][1], positions[0][0]])
                    last_position.append([positions[1][1], positions[1][0]])
                first_position = [int(last_position[0][0]/2), int(last_position[0][1]/2)]
                second_position = [int(last_position[1][0] / 2), int(last_position[1][1] / 2)]
                move(x_relative + first_position[0], y_relative+browser_navigation_panel_height+first_position[1])
                click()
                time.sleep(3)
                move(x_relative + second_position[0], y_relative + browser_navigation_panel_height + second_position[1])
                click()
            else:
                last_position.append([positions[0][1], positions[0][0]])
                first_position = [int(last_position[0][0] / 2), int(last_position[0][1] / 2)]
                move(x_relative + first_position[0], y_relative + browser_navigation_panel_height + first_position[1])
                click()
            browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys(
                Keys.CONTROL + "a")
            browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys('18218082132')
            browser.find_element_by_css_selector('.SignFlow-password input').send_keys(Keys.CONTROL + "a")
            browser.find_element_by_css_selector('.SignFlow-password input').send_keys('zh19920630')
            button_captcha_element = browser.find_element_by_class_name('Button SignFlow-submitButton Button--primary Button--blue')
            ele_position = button_captcha_element.location
            x_relative = ele_position['x']
            y_relative = ele_position['y']
            move(x_relative+5, y_relative+browser_navigation_panel_height+2)
            click()

        if english_captcha_element:
            base64_text = english_captcha_element.get_attribute("src")
            code = base64_text.replace("data:image/jpg;base64,", "").replace("%0A", "")
            fh = open("yzm_cn.jpeg", 'wb')
            fh.write(base64.b64decode(code))
            fh.close()

            yundama = YDMHttp("da_ge_dal", "dageda", 3129, "40d5ad41c047179fc797631e3b9c3025")
            code = yundama.decode('yzm_cn.jpeg', 5000, 60)
            while True:
                if code == "":
                    code = yundama.decode('yzm_cn.jpeg', 5000, 60)
                else:
                    break
            browser.find_element_by_xpath(
                '//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[3]/div/div/div[1]/input').send_keys(
                Keys.CONTROL + "a")
            browser.find_element_by_xpath(
                '//*[@id="root"]/div/main/div/div/div/div[2]/div[1]/form/div[3]/div/div/div[1]/input').send_keys(
                code)

            browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                Keys.CONTROL + "a")
            browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                "xxx")
            browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
            browser.find_element_by_css_selector(".SignFlow-password input").send_keys("xxx")
            # move(895, 603)
            browser_navigation_panel_height = browser.execute_script(
                'return window.outerHeight - window.innerHeight;'
            )
            button_captcha_element = browser.find_element_by_class_name(
                'Button SignFlow-submitButton Button--primary Button--blue')
            ele_position = button_captcha_element.location
            x_relative = ele_position['x']
            y_relative = ele_position['y']
            move(x_relative + 5, y_relative + browser_navigation_panel_height + 2)
            click()

    # def start_requests(self):
    #     cookies = pickle.load(open("/home/zgf/PycharmProjects/ArticleSpider/ArticleSpider/build/cookies/zhihu.cookie", 'rb'))
    #     cookie_dict = {}
    #     for cookie in cookies:
    #         cookie_dict[cookie["name"]] = cookie["value"]
    #     return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
    #     # # 解决signin错误问题
    #     # chrome_option = Options()
    #     # chrome_option.add_argument("--disable-extensions")
    #     # chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    #     #
    #     # browser = webdriver.Chrome(executable_path="/home/zgf/chromedriver", chrome_options=chrome_option)
    #     # browser.get("https://www.zhihu.com/signin")
    #     # # browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys(Keys.CONTROL + "a")
    #     # # browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper input').send_keys('18218082132')
    #     # # browser.find_element_by_css_selector('.SignFlow-password input').send_keys(Keys.CONTROL + "a")
    #     # # browser.find_element_by_css_selector('.SignFlow-password input').send_keys('zh19920630')
    #     # # # move(605, 500)
    #     # # # click()
    #     # # browser.find_element_by_css_selector('.Button.SignFlow-submitButton').click()
    #     #
    #     # cookies = browser.get_cookies()
    #     # pickle.dump(cookies, open("/home/zgf/PycharmProjects/ArticleSpider/ArticleSpider/build/cookies/zhihu.cookie", 'wb'))
    #     # cookie_dict = {}
    #     # for cookie in cookies:
    #     #     cookie_dict[cookie["name"]] = cookie["value"]
    #     # return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
