# -*- coding: utf-8 -*-
import os
import glob
import csv
from openpyxl import Workbook
import scrapy
from scrapy.http import Request


def product_information(response, feature):
    return response.xpath('//th[text()="' + feature + '"]/following-sibling::td/text()').extract_first()


class ArgBooksSpider(scrapy.Spider):
    name = 'arg_books'
    allowed_domains = ['books.toscrape.com']

    def __init__(self, category):
        self.start_urls = [category]

    def parse(self, response):
        """ Gets the books pages and feeds that pages into parse_book """
        books = response.xpath('//h3/a/@href').extract()

        for book in books:
            absulote_url = response.urljoin(book)
            yield Request(absulote_url, callback=self.parse_book)

        next_page_url = response.xpath(
            '//*[@class="next"]/a/@href').extract_first()
        absulote_next_page_url = response.urljoin(next_page_url)
        yield Request(absulote_next_page_url)

    def parse_book(self, response):
        """ getting the books information """
        title = response.css('h1::text').extract_first()
        price_color = response.xpath(
            '//h1/following-sibling::p[@class="price_color"]/text()').extract_first()
        rating = response.xpath(
            '//*[contains(@class, "star-rating")]/@class').extract_first()
        rating = rating.replace('star-rating', '')

        image_url = response.xpath('//img/@src').extract_first()
        image_url = image_url.replace('../..', 'http://books.toscrape.com')

        product_description = response.xpath(
            '//*[@id="product_description"]/following-sibling::p/text()').extract_first()

        # Product Information Data Points
        upc = product_information(response, "UPC")
        product_type = product_information(response, "Product Type")
        price_without_tax = product_information(response, "Price (excl. tax)")
        price_with_tax = product_information(response, "Price (incl. tax)")
        tax = product_information(response, "Tax")
        availability = product_information(response, "Availability")
        number_of_review = product_information(response, "Number of reviews")

        yield {
            'title': title,
            'price_color': price_color,
            'rating': rating,
            'product_description': product_description,
            'image_url': image_url,
            'upc': upc,
            'product_type': product_type,
            'price_without_tax': price_without_tax,
            'price_with_tax': price_with_tax,
            'tax': tax,
            'availability': availability,
            'number_of_review': number_of_review
        }

    def close(self, reason):
        csv_file = max(glob.iglob('*.csv'), key=os.path.getctime)
        wb = Workbook()
        ws = wb.active

        with open(csv_file, 'r') as f:
            for row in csv.reader(f):
                ws.append(row)

        wb.save(csv_file.replace('.csv', '') + '.xlsx')
