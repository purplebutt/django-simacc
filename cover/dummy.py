from django.utils import lorem_ipsum
from django.conf import settings
import random


def products():
    result = []
    for i in range(1, 13):
        price = random.randrange(10, 399)
        result.append(
            {
                'title': f'Product {i}',
                'image': f'/static/images/items/{i}.jpg',
                'price': price,
                'desc': lorem_ipsum.words(20),
                'url': f'#product{i}'
            }
        )
    return result