import concurrent.futures
import random
import re
import time

from bs4 import BeautifulSoup
import requests


def crawl(product):
    response = requests.get(product.url)


def main():
    from panel.models import Product

    products = (
        Product.objects.all()
        .order_by("-site")
        .exclude(site__site_name__icontains="walmart")
    )
    walmart_products = Product.objects.filter(site__site_name__icontains="walmart")

    MAX_THREADS = 10
    threads = min(MAX_THREADS, len(products))

    start = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(crawl, walmart_products)

    end = time.time()
    print(f"{end-start} seconds to finish.")


if __name__ == "__main__":
    import os

    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "watchdog.settings")

    django.setup()
    main()
