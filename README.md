# cdio2mongo
[Scrapy](https://github.com/scrapy/scrapy) spider to consume watch results from a [changedetection.io](https://github.com/dgtlmoon/changedetection.io)
instance and save them into a [MongoDB](https://www.mongodb.com/de-de).

## Usage

Start the Docker Compose stack with a mongo database and changedetection.io for testing.

```shell
docker-compose up -d
```

### Example

```shell
scrapy crawl api -s CHANGEDETECTION_DOMAIN=localhost -s CHANGEDETECTION_PORT=8082 -s CHANGEDETECTION_PROTOCOL=http -s CHANGEDETECTION_API_KEY=<API_KEY> -s CHANGEDETECTION_ONLY_LATEST=False
```

Set `CHANGEDETECTION_ONLY_LATEST` to `True` if you only need the latest data from each watch.

See [settings.py](cdio2mongo/settings.py) for database connection variables.


All data is saved into the `watches` database. For each watch a new collection, identified by the `watch_uuid` is
created. The history timestamp (`created_at`) is used as the primary key (`_id`) for each watch collection.

## Motivation

The storage backend of [changedetection.io](https://github.com/dgtlmoon/changedetection.io) is not sufficient for my
needs, so I decided to create a simple spider with [Scrapy](https://github.com/scrapy/scrapy) to save all my data
from changedetection.io for further processing and to back it up.

## Licence

[MIT](LICENSE)
