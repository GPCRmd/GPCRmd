from django import template
from django.conf import settings


register = template.Library()

logo_dict = {
        'logo_path': 'home/logo/' + settings.SITE_NAME + '/main.png',
        'logo_width': '75',
        'logo_path2': 'home/logo/' + settings.SITE_NAME + '/main2.png',
        'logo_width2': '73',
        'logo_path3': 'home/logo/' + settings.SITE_NAME + '/main3.png',
        'logo_width3': '76',

    }

@register.simple_tag
def get_logos():
    return logo_dict

@register.inclusion_tag('home/mainmenu.html')
def mainmenu():
    data = {
        'site_title': settings.SITE_TITLE,
        'menu_template': 'home/mainmenu_' + settings.SITE_NAME + '.html',
        'documentation_url': settings.DOCUMENTATION_URL,
    }
    data.update(logo_dict)
    return data


