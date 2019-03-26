import time
from selenium import webdriver


# # selenium完成微博模拟登录
# browser = webdriver.Chrome(executable_path='/home/zgf/chromedriver')
# browser.get('https://www.oschina.net/blog')
# time.sleep(5)
# browser.find_element_by_css_selector('#loginname').send_keys('982182648@qq.com')
# browser.find_element_by_css_selector('.info_list.password input[node-type="password"]').send_keys('xxxx')
# browser.find_element_by_css_selector('.info_list.login_btn a[node-type="submitBtn"]').click()
#
# # 每隔3秒自动下拉一次
# for i in range(3):
#     browser.execute_script('window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;')
#     time.sleep(3)

# 设置chromedriver不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {'profile.managed_default_content_settings.images': 2}
chrome_opt.add_experimental_option('prefs', prefs)
browser = webdriver.Chrome(executable_path='/home/zgf/chromedriver', chrome_options=chrome_opt)
browser.get('https://www.taobao.com')
# browser.quit()