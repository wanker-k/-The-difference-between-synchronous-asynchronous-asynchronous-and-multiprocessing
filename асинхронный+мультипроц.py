import asyncio
import aiohttp
import csv
from concurrent.futures import ProcessPoolExecutor
from decorators import check_time

# Вот эту брехню уже писал не я,а ии, я лишь дополнял. 


def new_csv():
    with open('liveinternet_async.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'url_site', 'description', 'traffic', 'percent'])


def parse_html(html):
    data = html.strip().split('\n')[1:]
    rows = []
    for row in data:
        columns = row.strip().split('\t')
        if len(columns) >= 5:
            rows.append({
                'name': columns[0],
                'url_site': columns[1],
                'description': columns[2],
                'traffic': columns[3],
                'percent': columns[4]
            })
    return rows

async def fetch(session, url):
    async with session.get(url) as resp:
        return await resp.text(encoding='cp1251', errors='ignore')

async def process_page(session, url, executor, queue):
    html = await fetch(session, url)
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(executor, parse_html, html)
    await queue.put(data)

async def writer(queue):
    with open('liveinternet_async_mp.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'url_site', 'description', 'traffic', 'percent'])
        writer.writeheader()
        while True:
            data = await queue.get()
            if data is None:
                break
            writer.writerows(data)


async def main():
    base_url = 'https://www.liveinternet.ru/rating/ru//today.tsv?page={}'
    pages = range(1, 1001)
    queue = asyncio.Queue()

    async with aiohttp.ClientSession() as session:
        with ProcessPoolExecutor(max_workers=4) as executor:

            writer_task = asyncio.create_task(writer(queue))

            tasks = [process_page(session, base_url.format(i), executor, queue) for i in pages]
            await asyncio.gather(*tasks)


            await queue.put(None)
            await writer_task

@check_time
def mp_async():
    new_csv()
    asyncio.run(main())

if __name__ == '__main__':
    mp_async()
