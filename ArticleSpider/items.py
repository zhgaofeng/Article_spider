# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
from w3lib.html import remove_tags


from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
from ArticleSpider.utils.common import get_nums
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT
from ArticleSpider.models.es_types import ArticleType
from elasticsearch_dsl.connections import connections
es = connections.create_connection(ArticleType._doc_type.using)


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_jobbole(value):
    return value


def date_convert(value):
    try:
        value = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
    except Exception as e:
        value = datetime.datetime.now().date()
    return value


def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value

def gen_suggests(index, info_tuple):
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={"filter":["lowercase"]}, body=text)
            analyzed_words = set(r["token"] for r in words["tokens"] if len(r["token"]) > 1)
            new_words = analyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input":list(new_words), "weight":weight})


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    front_img_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    praise_nums = scrapy.Field()
    bookmark_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    write_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_path = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
            insert into article(url_object_id, title, url, content, create_date,write_nums)
            VALUES(%s, %s, %s, %s, %s, %s)
        '''
        params = (self["url_object_id"], self["title"], self["url"], self["content"], self["create_date"], self["write_nums"])
        return insert_sql, params

    def save_to_es(self):
        article = ArticleType()
        article.title = self["title"]
        article.create_date = self["create_date"]
        article.content = self["content"]
        article.front_img_url = self["front_img_url"]
        article.praise_nums = self["praise_nums"]
        article.write_nums = self["write_nums"]
        article.bookmark_nums = self["bookmark_nums"]
        article.url = self["url"]
        article.tags = self["tags"]
        article.meta.id = self["url_object_id"]
        if "front_image_path" in self:
            article.front_image_path = self["front_image_path"]
        article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title,10),(article.tags,7)))
        article.save()
        return


class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topic = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
            insert into zhihu_question(zhihu_id, topic, url, title, content,answer_num, comments_num, watch_user_num, click_num, crawl_time)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE topic=VALUES(topic), comments_num=VALUES(comments_num), 
            answer_num=VALUES(answer_num)
        '''
        zhihu_id = int("".join(self['zhihu_id']))
        topic = ",".join(self['topic'])
        url = "".join(self['url'])
        title = "".join(self['title'])
        content = "".join(self['content'])
        answer_num = get_nums("".join(self['answer_num']))
        comments_num = get_nums("".join(self['comments_num']))
        watch_user_num = get_nums("".join(self['watch_user_num']))
        click_num = get_nums("".join(self['click_num']))
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        params = (zhihu_id, topic, url, title, content, answer_num, comments_num, watch_user_num, click_num, crawl_time)
        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_date = scrapy.Field()
    update_date = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num, create_date, 
            update_date, crawl_time) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), 
            update_time=VALUES(update_time)
        '''
        create_date = datetime.datetime.fromtimestamp(self['create_date']).strftime(SQL_DATETIME_FORMAT)
        update_date = datetime.datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT)
        params = (
            self['zhihu_id'], self['url'], self['question_id'], self['author_id'], self['content'],
            self['praise_num'], self['comments_num'], create_date, update_date,
            self['crawl_time'].strftime(SQL_DATETIME_FORMAT)
        )
        return insert_sql, params


def remove_splash(value):
    return value.replace('/', '')

def handle_jobaddr(value):
    addr_list = value.split('\n')
    addr_list = [item.strip() for item in addr_list if item.strip() != '查看地图']
    return ''.join(addr_list)


class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(',')
    )
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                    insert into lagou_job(title, url, url_object_id, salary, job_city, work_years, degree_need,
                    job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
                    tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
        """

        params = (
            self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"],
            self["work_years"], self["degree_need"], self["job_type"],
            self["publish_time"], self["job_advantage"], self["job_desc"],
            self["job_addr"], self["company_name"], self["company_url"],
            self["job_addr"], self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params