import aiofiles
import aiohttp
import csv
import asyncio
from decorators import check_time


def new_csv():
    with open('liveinternet_async.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'url_site', 'description', 'traffic', 'percent'])


async def write_to_csv(data):
    async with aiofiles.open('liveinternet_async.csv', 'a') as f:
        row = ','.join(str(v) for v in data.values()) + '\n'
        await f.write(row)


async def fetch_text(session, url):
    async with session.get(url) as resp:
        return await resp.text(encoding='utf-8')

async def parse_site(session, url):
    text = await fetch_text(session, url)
    data = text.strip().split('\n')[1:]
    if not data:
        return
    for row in data:
        columns = row.strip().split('\t')
        keys = ['name', 'url_site', 'description', 'traffic', 'percent']
        info = {key: columns[i] for i, key in enumerate(keys)}
        await write_to_csv(info)


async def main():
    async with aiohttp.ClientSession() as session:
        base_url = 'https://www.liveinternet.ru/rating/ru//today.tsv?page={}'
        pages = range(1, 1000)
        tasks = []
        for p in pages:
            page = base_url.format(p)
            task = asyncio.create_task(parse_site(session, page))
            tasks.append(task)
        await asyncio.gather(*tasks)


@check_time
def async_function():
    new_csv()
    asyncio.run(main())

if __name__ == '__main__':
    async_function()
