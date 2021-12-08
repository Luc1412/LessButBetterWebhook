import json
import time

import bs4
import requests
import discord


def get_kbd_fans_updates():
    resp = requests.get('https://kbdfans.com/a/groupbuyupdates')
    html = bs4.BeautifulSoup(resp.text, 'html.parser')
    for faq_item in html.find_all('div', {'class': 'faqPlusAppFaq'}):
        if not faq_item.find_next('label').text == 'EPBT LESS BUT BETTER':
            continue
        data = {}
        for info_item in faq_item.find_all('p'):
            spans = info_item.find_all('span')
            if len(spans) < 1 or spans[0].text in ['Update', 'Product Link ']:
                continue
            name = spans.pop(0).text
            data[name] = ''.join(span.text for span in spans)
        return data
    return None


def get_kono_availability():
    variant_ids = ['39388290252999', '39388290351303', '39388290384071', '39388290482375', '39388290515143', '39409128341703']
    data = {}
    for variant_id in variant_ids:
        resp = requests.get(f'https://kono.store/products/epbt-less-but-better?variant={variant_id}')
        html = bs4.BeautifulSoup(resp.text, 'html.parser')
        status = html.find('span', {'class': 'atc-button--text'}).text.strip()
        name = html.find('span', {'class': 'variants-ui__option-name option-name'}).find('span').text.strip()
        data[name] = status == 'Pre-order'
    return data


def get_daily_clack_availability():
    data = {}
    resp = requests.get(f'https://dailyclack.com/products/epbt-less-but-better')
    html = bs4.BeautifulSoup(resp.text, 'html.parser')
    for variant in html.find_all('option'):
        if variant.attrs.get('value') not in ['Base Kit', 'Novelties', 'Colour Dots Kit', 'Less Kit', 'Capital Alphas Kit', 'International']:
            continue
        status = variant.attrs.get('class') is None
        data[variant.text] = status
    return data


def send_webhook_update(embed):
    with open('config.txt') as f:
        webhook = discord.Webhook.from_url(f.read(), adapter=discord.RequestsWebhookAdapter())
    webhook.send('@everyone', embed=embed)


if __name__ == '__main__':
    while True:
        with open('data.json', 'r') as f:
            old_data = json.load(f)
        kbd_fans_data = get_kbd_fans_updates()
        kono_data = get_kono_availability()
        daily_clack_data = get_daily_clack_availability()

        if old_data['kbdfans'] != kbd_fans_data:
            old_data['kbdfans'] = kbd_fans_data
            embed = discord.Embed(color=0x000000)
            embed.set_author(name='KBD Fans Updates', url='https://kbdfans.com/a/groupbuyupdates')
            for name, value in kbd_fans_data.items():
                embed.add_field(name=name, value=value)
            send_webhook_update(embed)

        if old_data['kono'] != kono_data:
            old_data['kono'] = kono_data
            embed = discord.Embed(color=discord.Color.blue())
            embed.set_author(name='Kono.Store', url='https://kono.store/products/epbt-less-but-better')
            for name, value in kono_data.items():
                embed.add_field(name=name, value=':white_check_mark:' if value else ':x:')
            send_webhook_update(embed)

        if old_data['daily_clack'] != daily_clack_data:
            old_data['daily_clack'] = daily_clack_data
            embed = discord.Embed(color=discord.Color.red())
            embed.set_author(name='Daily Clack Availability', url='https://dailyclack.com/products/epbt-less-but-better')
            for name, value in kono_data.items():
                embed.add_field(name=name, value=':white_check_mark:' if value else ':x:')
            send_webhook_update(embed)

        with open('data.json', 'w') as f:
            json.dump(old_data, f)
        time.sleep(60 * 60)
