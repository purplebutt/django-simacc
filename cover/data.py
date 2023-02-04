from django.utils import lorem_ipsum
from django.template.defaultfilters import slugify
from django.conf import settings
from django.shortcuts import reverse
from random import randrange


def features():
    result = [
        {
            'title': f'Auto Cash Flow',
            'icon': 'fa-sack-dollar',
            'desc': lorem_ipsum.words(20),
            'url': '#'
        },
        {
            'title': f'Online Access',
            'icon': 'fa-globe',
            'desc': lorem_ipsum.words(20),
            'url': '#'
        },
        {
            'title': f'100% Free, no ads',
            'icon': 'fa-headset',
            'desc': lorem_ipsum.words(20),
            'url': '#'
        },
    ]
    return result

def sidebar(mode:str):
    if mode == "master":
        return [
            { 'name': 'coh', 'url': reverse('accounting:coh_list'), 'verbose': 'account group'},
            { 'name': 'coa', 'url': reverse('accounting:coa_list'), 'verbose': 'chart of account'},
            { 'name': 'ccf', 'url': reverse('accounting:ccf_list'), 'verbose': 'chart of cash flow'},
            { 'name': 'bsg', 'url': reverse('accounting:bsg_list'), 'verbose': 'business segment'},
        ]
    elif mode == "report":
        return [
            { 'name': 'tb', 'url': reverse('accounting:report_tb'), 'verbose': 'trial balance'},
            { 'name': 'gnl', 'url': reverse('accounting:report_gnl'), 'verbose': 'general ledger'},
            { 'name': 'cfl', 'url': reverse('accounting:report_cfl'), 'verbose': 'cash flow ledger'},
            { 'name': 'is', 'url': reverse('accounting:report_is'), 'verbose': 'income statement'},
            { 'name': 'es', 'url': '#is', 'verbose': 'equity statement'},
            { 'name': 'bs', 'url': '#bs', 'verbose': 'balance sheet'},
            { 'name': 'cf', 'url': '#cf', 'verbose': 'cash flow'},
        ]
    else:
        return [
            { 'name': 'jrb', 'url': reverse('accounting:jrb_list'), 'verbose': 'batch journal'},
            { 'name': 'jre', 'url': reverse('accounting:jre_list'), 'verbose': 'journal entries'},
        ]

def stat_card(n:int):
    result = []
    for i in range(1, n+1):
        data = {
            'id':i, 
            'number':randrange(1000, 9999), 
            'status': lorem_ipsum.words(randrange(2,4))
        }
        result.append(data)
    return result

def service_card(n:int):
    result = []
    icons = ('fa-search', 'fa-code', 'fa-globe')
    for i in range(1, n+1):
        ic = icons[i-1] if i<=len(icons) else icons[len(icons)-1]
        data = {
            'id':i, 
            'icon':ic, 
            'title': lorem_ipsum.words(randrange(2,5)),
            'content': lorem_ipsum.words(randrange(10,15)),
            'url': slugify(lorem_ipsum.words(randrange(1,3))),
        }
        result.append(data)
    return result

def feature_card(n:int):
    result = []
    icons = ('fa-search', 'fa-code', 'fa-globe')
    for i in range(1, n+1):
        rnd_idx = randrange(0, len(icons))
        ic = icons[i-1] if i<=len(icons) else icons[rnd_idx]
        data = {
            'id':i, 
            'icon':ic, 
            'title': lorem_ipsum.words(randrange(2,5)),
            'content': lorem_ipsum.words(randrange(10,15)),
            'url': slugify(lorem_ipsum.words(randrange(1,3))),
        }
        result.append(data)
    return result

def blog_card(n:int):
    result = []
    img_root = settings.STATIC_URL + 'images/section/blog/'
    images = (img_root + 'blog-1.jpg', img_root + 'blog-2.jpg', img_root + 'blog-3.jpg', img_root + 'blog-4.jpg')
    for i in range(1, n+1):
        rnd_idx = randrange(0, len(images))
        img = images[i-1] if i<=len(images) else images[rnd_idx]
        data = {
            'id':i, 
            'title': lorem_ipsum.words(randrange(2,5)),
            'content': lorem_ipsum.words(randrange(10,15)),
            'url': slugify(lorem_ipsum.words(randrange(1,3))),
            'comments': randrange(1,7000),
            'img': img,
            'share': "#share",
            'report': "#report",
        }
        result.append(data)
    return result

def hero():
    img_url = settings.STATIC_URL + 'images/section/hero/hero-banner.png'
    result = {
        'title': "the best free yet powerfull accounting system for your business",
        'subtitle': "100% free, full accounting standard report",
        'content': lorem_ipsum.words(randrange(30,100)),
        'url': slugify(lorem_ipsum.words(randrange(1,3))),
        'image': img_url,
    }
    return result

def about():
    img_url = settings.STATIC_URL + 'images/banners/about-banner.png'
    data = {
        '10 years experiences',
        'more than 50 clients',
        'accounting system by a real accountant',
    }
    result = {
        'title': "Why choose us..?",
        'content': lorem_ipsum.words(randrange(30,100)),
        'image': img_url,
        'listdt': data
    }
    return result