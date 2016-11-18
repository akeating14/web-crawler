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
    The user must supply the companies url. All the user needs to do is
    input a list of start urls.
    """
    name = 'company'
    company_name = 'Stripe'
    start_urls = ['https://stripe.com/jobs'
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
                  'https://slack.com/',
                  'http://www.espn.com/',
                  'https://justworks.com/'
                  ]
    possible_domains = ['jobs.', 'corporate.', 'careers.', '']
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
        Rule(LinkExtractor(allow=('jobs?\..*\/?.*job.*')), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=('careers?\..*\/?.*job.*')), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=('careers\/.*job.*')), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=('jobs')), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=('careers')), follow=True),
        Rule(LinkExtractor(allow=('joinus')), follow=True),
    )

    def __int__(self):
        self.allowed_domains = self.process_start_urls()

    def process_start_urls(self):
        return [re.sub('^www.$', '', urlparse(url).netloc,) for url in self.start_urls]

    # def get_allowed_domains(self):
    #     return ['{domain}{url}'.format(url=url, domain=text)
    #             for url in self.process_start_urls() for text in self.possible_domains]

    def root_links(self):
        """
        It will return a list of root domains.
        TODO:
              1. Combine regex statements
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
        1. Design is weak because it relies on key words
        2. Does not handle Javascript
        3. Does not handle XML.
        """
        base_job_pages = ['{url}/{ext}'.format(url=url, ext=ext) for url in self.root_links()
                          for ext in self.possible_endpoints]
        if response.url in base_job_pages:
            return response

        loader = CompanyLoader(ListingItem(), response=response)
        loader.add_value('company_name', urlparse(response.url).netloc)
        loader.add_value('listing_link', response.url)
        loader.add_value('position_page', response.text)
        loader.add_xpath('location', '//span[@class="location"]/text()')
        loader.add_xpath('position_title', '//h1/text()')
        loader.add_xpath('description', '//p/text()')
        loader.add_xpath('qualifications', '//li/text()')
        return loader.load_item()
