import scrapy


class ApiSpider(scrapy.Spider):

    name = "api"
    allowed_domains = []
    start_urls = []

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        print('kwargs =', kwargs)

        changedetection_io_instance = kwargs.get('domain', 'changedetection.io')
        self.allowed_domains.append(changedetection_io_instance)

        api_url = kwargs.get('start_url', 'https://changedetection.io') + "api/v1/watch"

        self.start_urls.append(api_url)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(
            *args,
            domain=crawler.settings.get("CHANGEDETECTION_DOMAIN"),
            start_url=crawler.settings.get("CHANGEDETECTION_BASE_URL"),
            **kwargs
        )
        spider._set_crawler(crawler)
        return spider

    def start_requests(self):

        headers = {
            self.settings.get("CHANGEDETECTION_HTTP_HEADER"): self.settings.get('CHANGEDETECTION_API_KEY')
        }

        self.logger.debug(f"CHANGEDETECTION_HTTP_HEADER: {headers}")
        yield scrapy.http.Request(self.start_urls[0], headers=headers)

    def parse(self, response, **kwargs):

        self.logger.debug(f"{response}")
