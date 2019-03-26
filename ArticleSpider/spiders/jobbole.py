# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
import datetime
from scrapy.loader import ItemLoader

from ArticleSpider.items import JobboleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path='/home/zgf/chromedirver')
        super(JobboleSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 当爬虫退出的时候退出browser
        self.browser.quit()

    def parse(self, response):
        # 获取下一页的url并且交给scrapy进行下载
        post_nodes = response.xpath('//*[@id="archive"]/div/div[1]/a')
        for post_node in post_nodes:
            post_url = post_node.xpath('@href').extract_first()
            post_imgUrl = post_node.xpath('img/@src').extract_first()
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_img_url":post_imgUrl}, callback=self.detail_parse)
        next_url = response.xpath('//a[contains(@class, "next") and contains(@class, "page-numbers")]/@href').extract()
        if next_url:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)

    def detail_parse(self, response):
        # article_item = JobboleArticleItem()
        # front_img_url = response.meta.get("front_img_url", "")
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        # create_date = response.xpath('//div[@class="entry-meta"]/p/text()').extract_first().strip().replace("·","").strip()
        # praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract_first()
        # bookmark_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract_first()
        # mark_match = re.match(".*?(\d).*", bookmark_nums)
        # if mark_match:
        #     bookmark_nums = int(mark_match.group(1))
        # else:
        #     bookmark_nums = 0
        # write_nums = response.xpath('//div[@class="post-adds"]/a/span/text()').extract_first()
        # write_match = re.match(".*?(\d).*", write_nums)
        # if write_match:
        #     write_nums = int(write_match.group(1))
        # else:
        #     write_nums = 0
        # content = response.xpath('//div[@class="entry"]/p/text()').extract_first()
        # # create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_lists = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_list = [element for element in tag_lists if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
        #
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["title"] = title
        # article_item["front_img_url"] = [front_img_url]
        # try:
        #     create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        # article_item["create_date"] = create_date
        # article_item["url"] = response.url
        # article_item["praise_nums"] = praise_nums
        # article_item["bookmark_nums"] = bookmark_nums
        # article_item["write_nums"] = write_nums
        # article_item["content"] = content
        # article_item["tags"] = tags

        item_loader = ArticleItemLoader(item=JobboleArticleItem(), response=response)
        front_img_url = response.meta.get("front_img_url", "")
        item_loader.add_xpath("title", '//div[@class="entry-header"]/h1/text()')
        item_loader.add_xpath("create_date", '//div[@class="entry-meta"]/p/text()')
        item_loader.add_xpath("praise_nums", '//span[contains(@class,"vote-post-up")]/h10/text()')
        item_loader.add_xpath("bookmark_nums", '//span[contains(@class,"bookmark-btn")]/text()')
        item_loader.add_xpath("write_nums", '//div[@class="post-adds"]/a/span/text()')
        item_loader.add_xpath("content", '//div[@class="entry"]/p/text()')
        item_loader.add_xpath("tags", '//p[@class="entry-meta-hide-on-mobile"]/a/text()')
        item_loader.add_value("url", response.url)
        item_loader.add_value("front_img_url", [front_img_url])
        item_loader.add_value("url_object_id", get_md5(response.url))
        article_item = item_loader.load_item()
        yield article_item
        pass
