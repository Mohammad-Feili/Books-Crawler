# -*- coding: utf-8 -*-
import os
import csv
import glob
import psycopg2
import scrapy
from scrapy.http import Request


def product_information(response, feature):
    return response.xpath('//th[text()="' + feature + '"]/following-sibling::td/text()').extract_first()


class Books01Spider(scrapy.Spider):
    name = 'postgre_db'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']

    def parse(self, response):
        """ Gets the books pages and feeds that pages into parse_book """
        books = response.xpath('//h3/a/@href').extract()

        for book in books:
            absulote_url = response.urljoin(book)
            yield Request(absulote_url, callback=self.parse_book)

    def parse_book(self, response):
        """ getting the books information """
        title = response.css('h1::text').extract_first()
        rating = response.xpath(
            '//*[contains(@class, "star-rating")]/@class').extract_first()
        rating = rating.replace('star-rating', '')

        # Product Information Data Points
        upc = product_information(response, "UPC")
        product_type = product_information(response, "Product Type")

        yield {
            'title': title,
            'rating': rating,
            'upc': upc,
            'product_type': product_type
        }

    def close(self, reason):
        csv_file = max(glob.iglob('*.csv'), key=os.path.getctime)
        mydb = psycopg2.connect(host="localhost",
                                user="root",
                                password="mfeili9553",
                                port="5432",
                                database="books")
        cursor = mydb.cursor()
        with open(csv_file, 'r') as f:
            csv_data = csv.reader(f)
            row_count = 0
            for row in csv_data:
                if row_count != 0:
                    cursor.execute(
                        "INSERT INTO books_table(rating, product_type, upc, title) VALUES(%s, %s, %s, %s)", row)
        mydb.commit()
        cursor.close()
