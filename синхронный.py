import requests
import csv
from decorators import check_time


def get_html(url):
    r = requests.get(url)
    return r.text



def new_csv():
    with open('liveinternet.csv', 'w'):
        pass

def write_csv(data):
    with open('liveinternet.csv', 'a') as f:
        order = ['name', 'url_site', 'description', 'traffic', 'percent']
        writer = csv.DictWriter(f, fieldnames=order)
        writer.writerow(data)

@check_time
def main():
    base_url = 'https://www.liveinternet.ru/rating/ru//today.tsv?page={}'
    for i in range(1, 1000):
        url = base_url.format(i)
        d = get_html(url)
        data = d.strip().split('\n')[1:]
        for row in data:
            columns = row.strip().split('\t')
            keys = ['name', 'url_site', 'description', 'traffic', 'percent']
            info = {key: columns[i] for i, key in enumerate(keys)}
            write_csv(info)
        

if __name__ == '__main__':
    new_csv()
    main()
