from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join


class CompanyLoader(ItemLoader):
    """
    This processes items to make sure they are stored correctly.
    """
    default_output_processor = TakeFirst()

    qualifications_in = MapCompose(unicode.strip)
    qualifications_out = Join()
    #
    description_in = MapCompose(unicode.strip)
    description_out = Join(separator='\n')

    position_title_in = MapCompose(unicode.strip)