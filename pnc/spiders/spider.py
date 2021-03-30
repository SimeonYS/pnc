import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import PncItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class PncSpider(scrapy.Spider):
	name = 'pnc'
	start_urls = ['https://pnc.mediaroom.com/index.php?s=3473&o=0']

	def parse(self, response):
		articles = response.xpath('//div[@class="wd_item_wrapper"]')
		for article in articles:
			date = article.xpath('.//div[@class="wd_date"]/text()').get()
			post_links = article.xpath('.//div[@class="wd_title"]/a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[@aria-label="Show next page"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="wd_title wd_language_left"]/text()').get()
		content = response.xpath('//div[@class="wd_body wd_news_body"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=PncItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
