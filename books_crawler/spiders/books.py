# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from selenium import webdriver
from scrapy.http import Request
from scrapy import Spider
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from books_crawler.items import BooksCrawlerItem
from scrapy.loader import ItemLoader


class BooksSpider(Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']

    def start_requests(self):
        self.driver = webdriver.Chrome(
            r'C:\Users\mohammad feili\Documents\Scrapers\books_clrawler\books_crawler\spiders\chromedriver.exe')
        self.driver.get('http://books.toscrape.com')
        sel = Selector(text=self.driver.page_source)
        book_urls = sel.xpath('//h3/a/@href').extract()
        for book in book_urls:
            url = 'http://books.toscrape.com/' + book
            yield Request(url, callback=self.parse_book)

        while True:
            try:
                next_page = self.driver.find_element_by_xpath(
                    '//a[text()="next"]')
                sleep(3)
                self.logger.info('Sleeping for 3 seconds.')
                next_page.click()

                sel = Selector(text=self.driver.page_source)
                book_urls = sel.xpath('//h3/a/@href').extract()
                for book in book_urls:
                    url = 'http://books.toscrape.com/catalogue/' + book
                    yield Request(url, callback=self.parse_book)

            except NoSuchElementException:
                self.logger.info('no more pages to load')
                self.driver.quit()
                break

    def parse_book(self, response):
        item_loader = ItemLoader(item=BooksCrawlerItem(), response=response)
        title = response.xpath('//h1/text()').extract_first()
        url = response.request.url

        yield {
            'Title': title,
            'Url': url
        }

        item_loader.add_value('Title', title)
        item_loader.add_value('Url', url)

        item_loader.load_item()
