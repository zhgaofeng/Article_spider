from elasticsearch_dsl import DocType, Date, Nested, Boolean, analyzer, \
    Completion, Keyword, Text, Integer
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class ArticleType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    front_img_url = Keyword()
    front_image_path = Keyword()
    praise_nums = Integer()
    bookmark_nums = Integer()
    write_nums = Integer()
    content = Text(analyzer="ik_max_word")
    tags = Text(analyzer="ik_max_word")

    class Meta:
        index = "jobbole"
        doc_type = "article"


if __name__ == "__main__":
    ArticleType.init()