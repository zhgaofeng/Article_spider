# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
import time
import pickle
import base64
import re
import json
import datetime
import random


from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from mouse import move, click
from zheye import zheye
from tools.yundama_requests import YDMHttp
try:
    import urlparse as parse
except:
    from urllib import parse
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem
from ArticleSpider.settings import user_agent_list


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com']
    start_answer_url = ['https://www.zhihu.com/api/v4/questions/{0}/answers?include=data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,is_recognized;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics&limit={1}&offset={2}&platform=desktop&sort_by=default']
    random_index = random.randint(0, len(user_agent_list)-1)
    random_agent = user_agent_list[random_index]
    headers = {
        'HOST': 'www.zhihu.com',
        'Referer': 'https:www.zhihu.com',
        'User-Agent': random_agent
    }

    custom_settings = {
        'COOKIES_ENABLED': True
    }

    def parse(self, response):
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)
        for url in all_urls:
            match_obj = re.match('.*zhihu.com/question/(\d+)(/|$).*', url)
            if match_obj:
                request_url = match_obj.group(1)
                random_index = random.randint(0, len(user_agent_list) - 1)
                random_agent = user_agent_list[random_index]
                self.headers['User-Agent'] = random_agent
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
            else:
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        # 从页面中提取question
        match_obj = re.match('.*zhihu.com/question/(\d)(/|$).*', response.url)
        if match_obj:
            question_id = match_obj.group(2)
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css('title', '.QuestionHeader-title::text') # css没有或 用xpath
        # item_loader.add_xpath('title', '//*[@id="QuestionHeader-title"]/h2/a/text()|//*[@id="QuestionHeader-title"]/h2/span/text()')
        item_loader.add_css('content', '.QuestionHeader-detail')
        item_loader.add_value('url', response.url)
        item_loader.add_value('zhihu_id', question_id)
        item_loader.add_css('answer_num', '.List-headerText span::text')
        item_loader.add_css('comments_num', '.QuestionHeaderActions button::text')
        item_loader.add_css('watch_user_num', '.NumberBoard-itemValue::text')
        item_loader.add_css('topic', '.QuestionHeader-topics .Popover div::text')
        question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id, 5, 0), headers=self.headers, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        ans_json = json.loads(respons.text)
        is_end = ans_json['paging']['is_end']
        totals_answer = ans_json['paging']['totals']
        next_url = ans_json['paging']['next']
        for answer in ans_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id'] if 'id' in answer['author'] else None
            answer_item['content'] = answer['content'] if 'content' in answer else None
            answer_item['praise_num'] = answer['voteup_count']
            answer_item['comments_num'] = answer['comment_count']
            answer_item['create_date'] = answer['created_time']
            answer_item['update_date'] = answer['update_time']
            answer_item['crawl_time'] = datetime.datetime.now()
            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer())


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
        browser.find_element_by_css_selector('.SignFlow-password input').send_keys('zhang19920630')
        browser.find_element_by_css_selector('.Button.SignFlow-submitButton').click()
        time.sleep(10) # 防止网页没有加载成功
        login_success = False
        while not login_success:
            try:
                notify_ele = browser.find_element_by_class_name('AppHeader-notifications')
                login_success = True
                Cookies = browser.get_cookies()
                cookie_dict = {}
                for cookie in Cookies:
                    f = open('./ArticleSpider/cookies/zhihu' + cookie['name'] + '.zhihu', 'wb')
                    pickle.dump(cookie, f)
                    f.close()
                    cookie_dict[cookie['name']] = cookie['value']
                browser.close()
                return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]
            except:
                pass
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
