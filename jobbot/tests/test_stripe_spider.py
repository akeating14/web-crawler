# from mock import patch
import pytest
import os
from scrapy.http import HtmlResponse
from jobbot.models import create_all_tables
from jobbot.spiders.stripe_spider import StripeSpider
from conftest import create_session


class TestStripeSpider:

    company_name = 'Stripe'
    allowed_domains = ['stripe.com']  # optional parameter
    start_urls = ['https://stripe.com/jobs']

    def test_root_links(self):
        root_links = StripeSpider().root_links()
        assert root_links == ['https://stripe.com']

    def test_parse_item(self, create_session):
        """
        What more do I need in this test?
        :return:
        """
        dir = os.path.dirname(__file__)
        webpage = open(os.path.join(dir, 'mock_webpages', 'stripe_job_listing.html'), "rb")
        request = {'url': 'https://stripe.com/jobs/positions/engineer'}
        response = HtmlResponse(url='https://stripe.com/jobs/positions/engineer', body=webpage.read(), request=request)  # mock takes request response
        loader = StripeSpider().parse_item(response)
        webpage.close()
        assert loader.keys() == ['description', 'qualifications', 'position_page', 'location',
                                 'listing_link', 'position_title', 'company_name']