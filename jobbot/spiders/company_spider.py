import re
from urlparse import urlparse

from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from jobbot.item_loaders import CompanyLoader
from jobbot.items import ListingItem


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
    start_urls = ['https://www.stripe.com/',
                  'https://www.google.com/',
                  'https://www.walmart.com/',
                  'http://corporate.exxonmobil.com/',
                  'http://www.gm.com/index.html',
                  'https://www.chevron.com/',
                  'http://www.conocophillips.com/Pages/default.aspx',
                  'http://www.ge.com/',
                  'http://www.ford.com/',
                  'http://www.citigroup.com/citi/',
                  'https://www.bankofamerica.com/',
                  'http://www.aig.com/individual',
                  ]
    possible_domains = ['https://jobs', 'https://corporate', 'https://careers', 'https://www']
    allowed_domains = ['{domain}{url}'.format(url=re.search(r'\..*', urlparse(url).netloc).group(0), domain=text)
                       for url in start_urls for text in possible_domains]
    find_root_link = True
    possible_endpoints = ['jobs', 'careers', 'joinus']
    """
    Example job pages:
                        1. https://jobs.walmart.com/us/jobs/820209/HERMISTON-OR-Trans-ServiceShopTechnician-II?lang=en-US
                        2. http://www.aig.com/careers/students/students-job-search -- this needs to be taken care of in processing - my rules will skip this
                        3. http://careers.exxonmobil.com/openings/2017-Global-Geoscience-Student-Placement-90-25778BR - I will ignore this situation
                        4. https://search-careers.gm.com/us/en/job/GENEA00845780/Senior-Process-Engineer-Heat-Treat
                        5. https://jobs.chevron.com/job/Buenos-Aires-SAP-ABAP-Application-Developer-Buen/370127300/
                        6. http://careers.conocophillips.com/job/6969956/exchange-skype-engineer-houston-tx/
                        7. https://xjobs.brassring.com/tgwebhost/jobdetails.aspx?partnerid=54&siteid=5346&jobId=1341726 - handled by allowed domains
                        8. http://corporate.ford.com/ShowJob/Id/1026667/NASCAR-Aerodynamics-Engineer/ - Do I need a rule for this link?
                        9. https://jobs.citi.com/job/o-fallon/loss-mitigation-specialist-2-safe-act-nrz-o-fallon-mo/287/2725796
                        10. http://careers.bankofamerica.com/job-detail/16049635/australia/asia-pacific/vp-application-support-delivery-lead
                        11. https://www.google.com/about/careers/jobs#!t=jo&jid=/google/software-engineer-1600-amphitheatre-pkwy-mountain-view-ca-6540009&
    """

    rules = (
        # Extract links matching possible extensions for company job's pages
        # follow career.
        Rule(LinkExtractor(allow=('jobs?\..*\/?.*job.*')), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=('careers?\..*\/?.*job.*')), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=('careers\/.*job.*')), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=('jobs')), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=('careers')), follow=True),
        Rule(LinkExtractor(allow=('joinus')), follow=True),
    )

    def root_links(self):
        """
        It will return a list of root domains.
        """
        root_start_urls = []
        for url in self.start_urls:
            parsed_url = urlparse(url)
            root_domain = parsed_url.netloc
            if root_domain:
                start_url = 'https://{url}'.format(url=root_domain)
                root_start_urls.append(start_url)
            else:
                root_start_urls.append(url)

        return root_start_urls

    @staticmethod
    def get_company_name(url):
        domain = urlparse(url).netloc
        return domain

    def start_requests(self):
        if self.find_root_link:
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
        base_job_pages = ['{url}/{ext}'.format(url=url, ext=ext) for url in self.root_links()
                          for ext in self.possible_endpoints]
        if response.url in base_job_pages:
            return response

        loader = CompanyLoader(ListingItem(), response=response)
        loader.add_value('company_name', self.get_company_name(response.url))
        loader.add_value('listing_link', response.url)
        loader.add_value('position_page', response.text)
        loader.add_xpath('location', '//span[@class="location"]/text()')
        loader.add_xpath('position_title', '//h1/text()')
        loader.add_xpath('description', '//p/text()')
        loader.add_xpath('qualifications', '//li/text()')
        return loader.load_item()