from bs4 import BeautifulSoup
import asyncio
import aiohttp
from fake_useragent import UserAgent
import os

from db import NewsCommands

ua = UserAgent()

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image"
              "/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    'user-agent': f'{ua.chrome}'
}

db = NewsCommands()

news = []
old_news = []


async def bbc_scraper():
    url = 'https://push.api.bbci.co.uk/batch?t=%2Fdata%2Fbbc-morph-lx-commentary-data-paged' \
          '%2Fabout%2Fe745fc56-51bf-46b5-9b74-f0f529ea4d8e%2FisUk%2Ffalse%2Flimit%2F20' \
          '%2FnitroKey%2Flx-nitro%2FpageNumber%2F1%2Fversion%2F1.5.6?timeout=5'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            data = await response.json()
            items = data.get('payload')[0].get('body').get('results')
            for item in items:
                try:
                    title = item.get('title').strip()
                except:
                    title = 'no title'

                try:
                    url = item.get('url').strip()
                except:
                    url = '0'

                try:
                    published = item.get('lastPublished').split('T')[0].replace('-', '.')
                except:
                    published = "no date"

                if not db.check_news('bbc', title=title, url='https://www.bbc.com' + url):
                    db.insert_news('bbc', title, published, 'https://www.bbc.com' + url)
                    news.append(
                        {
                            'title': title,
                            'url': 'https://www.bbc.com' + url,
                            'date': published,
                        }
                    )
                old_news.append(title)


async def guardian_scraper():
    url = 'https://www.theguardian.com/uk/technology'

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            response_text = await response.text()
            with open('template/guardian_scraper.html', 'w', encoding='utf-8') as f:
                f.write(response_text)
            with open('template/guardian_scraper.html', 'r', encoding='utf-8') as f:
                response_text = f.read()

            soup = BeautifulSoup(response_text, "html.parser")

            items = soup.find_all('div', class_='fc-item__content')

            urls = []

            for item in items:
                urls.append(item.find('a', class_='fc-item__link').get('href'))

            for url in urls:
                async with aiohttp.ClientSession() as session_local:
                    async with session_local.get(url=url, headers=headers) as response_local:
                        response_text_local = await response_local.text()

                        soup = BeautifulSoup(response_text_local, "html.parser")
                        try:
                            title = soup.find('h1', class_='dcr-y70mar').text.strip()
                        except:
                            try:
                                title = soup.find('h1', class_='dcr-1kwg2vo').text.strip()
                            except:
                                try:
                                    title = soup.find('span', class_='dcr-1ttbui0').text.strip()
                                except:
                                    try:
                                        title = soup.find('h1', class_='dcr-186f9ox').text.strip()
                                    except:
                                        try:
                                            title = soup.find('h1',
                                                              class_='content__headline').text.strip()
                                        except:
                                            try:
                                                title = soup.find('h1',
                                                                  class_='dcr-147zz9e').text.strip()
                                            except:
                                                title = '0'

                        try:
                            date = soup.find('span', class_='dcr-u0h1qy').text.strip()
                        except:
                            try:
                                date = soup.find('div', class_='dcr-eb59kw').text.strip()
                            except:
                                try:
                                    date = soup.find('time',
                                                     class_='content__dateline-wpd').text.strip()
                                except:
                                    try:
                                        date = soup.find('div',
                                                         class_='dcr-gp80yp').text.strip()
                                    except:
                                        date = '0'

                        if not db.check_news('guardian', title=title, url=url):
                            db.insert_news('guardian', title,
                                           date.split(' ')[1] + date.split(' ')[2] + date.split(' ')[3],
                                           url)
                            news.append({
                                'title': title,
                                'url': url,
                                'date': date,
                            })
                        old_news.append(title)


async def cnn_scraper():
    host = 'https://edition.cnn.com'
    url = 'https://edition.cnn.com/business/tech'
    cookies = {
        'countryCode': 'UZ',
        'stateCode': 'TK',
        'FastAB': '0=6218,1=4737,2=0116,3=5091,4=8629,5=1885,6=0476,7=5618,8=2581,9=6677,10=8351,11=7959,12=1618,13=3704,14=7512,15=0175,16=3476,17=3469,18=8673,19=9709',
        'usprivacy': '1---',
        'optimizelyEndUserId': 'oeu1678823933121r0.5000814841076779',
        'umto': '1',
        '_pbjs_userid_consent_data': '3524755945110770',
        'sato': '1',
        'FastAB_Zion': '5.1',
        'AMCVS_7FF852E2556756057F000101%40AdobeOrg': '1',
        'hkgc': 'f5422276-291e-11ed-9bf8-1c1322df0201',
        's_ecid': 'MCMID%7C46849949609630967873954844457063301207',
        'AMCV_7FF852E2556756057F000101%40AdobeOrg': '-1124106680%7CMCIDTS%7C19431%7CMCMID%7C46849949609630967873954844457063301207%7CMCAAMLH-1679428736%7C3%7CMCAAMB-1679428736%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1678831136s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.2.0',
        's_cc': 'true',
        'seenBreakingNews': '',
        'ug': '6410d2030b6f9e0a3f93a500166cacd8',
        'ugs': '1',
        'bea4': 'g096_7144699266790574707',
        'zwmc': '476228535513668926',
        'kfyn': 'C83FD585-3C03-44EB-B9E0-BA9BDCB330E9',
        'goiz': 'cb9419a373eb4889b0bfcf02632eaab3',
        'ifyr': 'L7DUCROY-4-5X35',
        '_sp_ses.f5fb': '*',
        'btIdentify': '48df64a4-53dd-4595-f4aa-25bd9886e39a',
        '_bts': 'eb79fd72-72ad-47c6-98b2-4b4bfb92f556',
        '_bti': '%7B%22app_id%22%3A%22cnn%22%2C%22bsin%22%3A%22D8DszIPwQyAoILJBKGjUAVCMrNHzN0MYvO8FneFD9ZrKwScv8vlFzQoGX2VWDucEpw5KH7%2BJUAbKCuVewfHFOg%3D%3D%22%2C%22is_identified%22%3Afalse%7D',
        'bounceClientVisit340v': 'N4IgNgDiBcIBYBcEQM4FIDMBBNAmAYnvgKYAmAlguQPYB2AdAMa0OPUC2RIANCAE4wQPEORQB9AObUxKYihQ1aMAGYBDMLN6jJEGXIV0V62QF8gA',
        '__gads': 'ID=1406be75754c6003:T=1678823951:S=ALNI_Mb-1yLmy4F_k4mEH_thJmGBGLO_hA',
        '__gpi': 'UID=00000bc5cb6d4953:T=1678823951:RT=1678823951:S=ALNI_MbIZLbuuoz0vY86XTcCiRTB8EuDxA',
        '_li_dcdm_c': '.cnn.com',
        '_lc2_fpi': 'd7ea6f2d6e56--01gvgv93grj31zeg00hh4bqbtz',
        '_pubcid': 'ccabcbd4-11b8-4e93-884c-aca0b1a15503',
        '_lr_retry_request': 'true',
        '_lr_env_src_ats': 'false',
        'pbjs-unifiedid': '%7B%22TDID%22%3A%22c1f6d796-58f9-43a2-ab72-a01d3fe0e250%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222023-02-14T19%3A59%3A15%22%7D',
        'panoramaId_expiry': '1679428755860',
        '_cc_id': 'e923c8d7b1e99faa7bdfc99b0a5df4d2',
        'panoramaId': '323a16369e911f123ea560bf8d3116d53938451a52684d8534604e02b200bf76',
        '__li_idex_cache': '%7B%7D',
        'pbjs_li_nonid': '%7B%7D',
        '_cb': 'D0c63ZKnGTICmNT8j',
        '_cb_svref': 'null',
        '__qca': 'P0-1678765526-1678824192124',
        'cnprevpage_pn': '%2Fbusiness%2Ftech%2F',
        'OptanonControl': 'ccc=UZ&csc=TK&cic=1&otvers=202211.2.0&pctm=2023-03-14T20%3A03%3A24.651Z&reg=global&ustcs=1---&vers=3.1.26',
        'geoData': 'tashkent|TK|100200|UZ|AS|500|broadband|41.360|69.310|-1',
        '_chartbeat2': '.1678824005764.1678824254669.1.Bc-dWoCZKJ0EBvzkW-7db2bCP6755.3',
        'OptanonAlertBoxClosed': '2023-03-14T20:04:14.894Z',
        'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Mar+15+2023+01%3A04%3A15+GMT%2B0500+(%D0%A3%D0%B7%D0%B1%D0%B5%D0%BA%D0%B8%D1%81%D1%82%D0%B0%D0%BD%2C+%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%BE%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202211.2.0&isIABGlobal=false&hosts=&consentId=a2f3cf25-4345-4181-ad51-74008c42b58c&interactionCount=1&landingPath=NotLandingPage&groups=BG1826%3A1%2Creq%3A1%2Ctdc%3A1%2Cven%3A1%2Cad%3A1%2Csm%3A1%2Cai%3A1%2Csmv%3A1%2Cdid%3A1%2Cpcp%3A1%2Csav%3A1%2Cpfv%3A1%2Cpcd%3A1%2Cmcp%3A1%2Cadv%3A1%2Cbb%3A1%2Cdsa%3A1%2Cdlk%3A1%2Cmap%3A1%2Ccad%3A1%2Cpf%3A1%2Cpzv%3A1%2Cfc%3A1%2Csid%3A1%2Ctc%3A1%2Cpdd%3A1%2Cmra%3A1%2Cgld%3A1%2Cpad%3A1%2Cpap%3A1%2Ccos%3A1%2Csa%3A1%2Csec%3A1&AwaitingReconsent=false&geolocation=UZ%3BTK',
        'kw.session_ts': '1678824255235',
        '_sp_ses.9758': '*',
        '_fbp': 'fb.1.1678824256931.851859042',
        'cto_bundle': 'YPJm_l9wdkRXbWF2N0pXS0NCczEzU0w2cGRMQ1ZDYXZIbUdlYkYlMkZWcHYzYXA4SkZreFhtZTl1USUyQkR3SmlyMiUyRmhqbzhVYyUyRm96NDY5ZkNFOEVrcVNmMzR2aXZBWmpHd3NvJTJGUWJOMGx2MFU0TktwVkNzM1NiNFlqcnM5N1dLcVp1SCUyQm5aSU1aSnlNUjQxR2I0JTJCM3hEaSUyRm9BWWhnJTNEJTNE',
        'kw.pv_session': '11',
        '_sp_id.9758': '6043a49c-2518-4f8f-8964-859fcd9d4448.1678824256.1.1678825006.1678824256.38dd66f4-20c2-4612-a14f-3e4089ccdfdd',
        '_sp_id.f5fb': '1304dac6-8abc-4aa7-916d-c3dafd7cd72b.1678823945.1.1678825019.1678823945.835a51da-dde9-4031-b754-9cfc5d1d221e',
    }
    headers = {
        'authority': 'edition.cnn.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
        'cache-control': 'max-age=0',
        'referer': 'https://edition.cnn.com/',
        'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': f'{ua.chrome}',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers, cookies=cookies) as response:
            response_text = await response.text()
            with open('template/cnn_scraper.html', 'w', encoding='utf-8') as f:
                f.write(response_text)
            with open('template/cnn_scraper.html', 'r', encoding='utf-8') as f:
                response_text = f.read()
            soup = BeautifulSoup(response_text, "html.parser")

            items = soup.find_all('a', class_='container__link')
            urls = []
            for item in items:
                urls.append(host + item.get('href'))

            for url in urls:
                async with aiohttp.ClientSession() as session_local:
                    async with session_local.get(url=str(url), headers=headers) as response_local:
                        response_text_local = await response_local.text()

                        soup = BeautifulSoup(response_text_local, "html.parser")
                        try:
                            title = soup.find('h1', class_='headline__text').text.strip()
                        except:
                            title = 'No title'

                        try:
                            date = soup.find('div', class_='timestamp').text.strip()
                            date = date.split(',')[1] + date.split(',')[2]
                        except:
                            date = 'No date'

                        if not db.check_news('cnn', title=title, url=url):
                            db.insert_news('cnn', title, date, url)
                            news.append({
                                'title': title,
                                'url': url,
                                'date': date,
                            })
                        old_news.append(title)


def delete_news():

    for saved_news in db.get_news():
        if not (saved_news[0] in old_news):
            db.delete_news(saved_news[0])

    os.remove('template/cnn_scraper.html')
    os.remove('template/guardian_scraper.html')


async def gather_data():
    tasks = [
        asyncio.create_task(bbc_scraper()),
        asyncio.create_task(guardian_scraper()),
        asyncio.create_task(cnn_scraper()),
    ]

    await asyncio.gather(*tasks)
    delete_news()


def main():
    asyncio.run(gather_data())


if __name__ == '__main__':
    main()
