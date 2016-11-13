import re
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from jobbot.item_loaders import CompanyLoader
from jobbot.items import ListingItem

"""
pycharm, breakpoint pycharm
read documenttion to the end, it helps give you an idea of how to do things
Try to implement for a specific page, indeed or dice, one or two different spiders than
abstract. Javascript sites,
"""


class CompanySpider(CrawlSpider):
    """
    This spider will locate all job listings for an arbitrary company.
    The user must supply the companies url.

    TODO: 1. all class parameters should either be defined
             by a settings file or should be defined in
             the crawling command.
          2. If user inputs a starting url that is not the root url
             it should be ignored and default to the root url.
    """
    name = 'company'
    company_name = 'Stripe'
    allowed_domains = ['stripe.com']  # optional parameter
    start_urls = ['https://stripe.com/jobs']
    find_root_link = True
    possible_endpoints = ['jobs', 'careers', 'joinus']

    rules = (
        # Extract links matching possible extensions for company job's pages
        Rule(LinkExtractor(allow=('jobs')), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=('careers')), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=('joinus')), callback='parse_item', follow=True),
    )

    def root_links(self):
        """
        It will return a list of root domains.
        TODO:
              1. Combine regex statements
        """
        root_start_urls = []
        for url in self.start_urls:
            shortened_url = re.search(':\/\/(.*)', url)
            root_domain = re.search(r'^[\w\d.]+', shortened_url.group(1))
            if root_domain:
                start_url = 'https://' + root_domain.group(0)
                root_start_urls.append(start_url)
            else:
                root_start_urls.append(url)

        return root_start_urls

    def start_requests(self):
        if self.find_root_link is True:
            start_urls = self.root_links()
        else:
            start_urls = self.start_urls
        for url in start_urls:
            yield self.make_requests_from_url(url)

    def parse_item(self, response):
        """
        TODO:
        1. Handle a situation where xpath gets no links
        2. Handle the situation where the homepage returns null
        3. Design is weak because it relies on key words
        4. Does not handle Javascript
        5. Does not handle situation where job page lives on another
           domain careers.microsoft.com.
        6. Does not handle XML.
        """
        base_job_page = [url + '/' + ext for url in self.root_links()
                         for ext in self.possible_endpoints]
        if response.url in base_job_page:
            return response

        loader = CompanyLoader(ListingItem(), response=response)
        loader.add_value('company_name', self.company_name)
        loader.add_value('listing_link', response.url)
        loader.add_value('position_page', response.text)
        loader.add_xpath('location', '//span[@class="location"]/text()')
        loader.add_xpath('position_title', '//h1/text()')
        loader.add_xpath('description', '//p/text()')
        loader.add_xpath('qualifications', '//p/text()')
        return loader.load_item()


