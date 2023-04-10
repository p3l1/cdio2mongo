import logging
import scrapy
from cdio2mongo.items import WatchDocument


class ApiSpider(scrapy.Spider):

    name = "api"
    allowed_domains = []
    start_urls = []

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # http or https
        _protocol = kwargs.get("protocol")
        _port = kwargs.get("port")

        self.domain = kwargs.get("domain")
        self.allowed_domains.append(self.domain)

        self.base_url = f"{_protocol}://{self.domain}:{_port}"

        start_url = f"{self.base_url}/api/v1/watch"
        self.start_urls.append(start_url)

        self.api_key = kwargs.get("api_key")

        if not self.api_key:
            raise ValueError('Changedetection API key missing! Set CHANGEDETECTION_API_KEY variable')

        self.headers = {
            kwargs.get("http_header"): self.api_key
        }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):

        spider = cls(
            *args,
            domain=crawler.settings.get("CHANGEDETECTION_DOMAIN", "changedetection.io"),
            port=crawler.settings.get("CHANGEDETECTION_PORT", 443),
            protocol=crawler.settings.get("CHANGEDETECTION_PROTOCOL", "https"),
            http_header=crawler.settings.get("CHANGEDETECTION_HTTP_HEADER", "x-api-key"),
            api_key=crawler.settings.get("CHANGEDETECTION_API_KEY", None),
            **kwargs
        )
        spider._set_crawler(crawler)
        return spider

    def start_requests(self):

        self.logger.debug(f"CHANGEDETECTION_HTTP_HEADER: {self.headers}")
        yield scrapy.http.Request(self.start_urls[0], headers=self.headers)

    def parse(self, response, **kwargs):

        watch_list_json = response.json()

        for watch_uuid, watch_info in watch_list_json.items():
            self.logger.debug(f"Processing watch with UUID {watch_uuid}")

            if watch_info.get('last_error', True):
                logging.error("Skipping! last_error is True")
                continue

            watch_url = self.base_url + f"/api/v1/watch/{watch_uuid}"

            yield scrapy.http.Request(watch_url, headers=self.headers, callback=self.parse_watch)

    def parse_watch(self, response):

        watch_json: dict = response.json()
        watch_uuid = watch_json.get('uuid', None)

        watch_document = WatchDocument(
            watch_uuid=watch_uuid,
            created_at=None,
            body=None,
            source_url=watch_json.get("url", None)
        )

        cb_args = {
            "document": watch_document
        }

        watch_history_url = response.urljoin(f"{watch_uuid}/history")

        yield scrapy.http.Request(watch_history_url, headers=self.headers, callback=self.parse_watch_history, cb_kwargs=cb_args)

    def parse_watch_history(self, response, document: WatchDocument):

        cb_args = {
            "document": document,
        }

        history_list_json: dict = response.json()

        timestamps = [t for t, _ in history_list_json.items()]
        timestamps.sort(reverse=True)  # History in descending order

        for timestamp in timestamps:

            cb_args['created_at'] = timestamp

            watch_document_url = response.urljoin(f"history/{timestamp}")
            yield scrapy.http.Request(watch_document_url, headers=self.headers, callback=self.parse_watch_document, cb_kwargs=cb_args)

            if self.settings.getbool("CHANGEDETECTION_ONLY_LATEST", True):
                break  # Break after first item, when only latest is required

    def parse_watch_document(self, response, created_at: str, document: WatchDocument) -> WatchDocument:

        # Set missing parameters and return item

        document["body"] = response.text
        document["created_at"] = created_at
        document["_id"] = created_at  # TODO: Change to a better identifier at some point

        return document
