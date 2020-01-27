# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.loader import ItemLoader
from books_crawler.items import BooksCrawlerItem


class Books01Spider(scrapy.Spider):
    name = 'img_downloading'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']

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
        l = ItemLoader(item=BooksCrawlerItem(), response=response)
        title = response.css('h1::text').extract_first()
        price_color = response.xpath(
            '//h1/following-sibling::p[@class="price_color"]/text()').extract_first()

        image_urls = response.xpath('//img/@src').extract_first()
        image_urls = image_urls.replace('../..', 'http://books.toscrape.com')

        l.add_value('title', title)
        l.add_value('price', price_color)
        l.add_value('image_urls', image_urls)

        return l.load_item()
