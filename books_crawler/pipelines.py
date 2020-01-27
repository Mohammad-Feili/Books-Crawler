# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
from .settings import MONGODB_SERVER, MONGODB_PORT, MONGODB_DB, MONGODB_COLLECTION


class MongoDBPipeline(object):
    def __init__(self):
        connection = MongoClient(
            MONGODB_SERVER,
            MONGODB_PORT
        )
        db = connection[MONGODB_DB]
        self.collection = db[MONGODB_COLLECTION]

    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item
