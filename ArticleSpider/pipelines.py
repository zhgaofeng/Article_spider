# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JonsExporterPipleline(object):
    def __init__(self):
        self.file = open('articleExporter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '123456', 'scrapyspider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = '''
            insert into article(url_object_id, title, url, content, create_date,write_nums)
            VALUES(%s, %s, %s, %s, %s, %s)
        '''
        self.cursor.execute(insert_sql, (item["url_object_id"], item["title"], item["url"], item["content"], item["create_date"], item["write_nums"]))
        self.conn.commit()
        return item


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def do_insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()

        cursor.execute(insert_sql, params)

    def handle_error(self, failure, item, spider):
        print(failure)


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_img_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path
        return item


class ElasticsearchPipeline(object):
    def process_item(self, item, spider):
        item.save_to_es()

        return item