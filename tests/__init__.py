from scrapy.utils.test import get_crawler


def get_spider(spidercls, settings=None, kwargs=None):
    crawler = get_crawler(spidercls, settings or {})
    return crawler._create_spider(spidercls.name, **(kwargs or {}))
