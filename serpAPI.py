from bs4 import BeautifulSoup
import requests
import webbrowser as wb
import random
import pprint


url_links = []
titles = []
pretty_links = []
valid_imgs_link = []


def main():
    global url_links
    global titles
    global pretty_links
    global valid_imgs_link
    while True:
        query = input(': ')
        url = 'https://www.google.com/search?client=firefox-b-d&q=' + query
        html_text = requests.get(url=url).text
        soup = BeautifulSoup(html_text, 'lxml')
        links = soup.find_all('a')

        for link in links:
            if link.find('h3'):  # selecting only those which have meaningful title
                boom = link.find('h3')
                url_links.append(link['href'])
                titles.append(boom.text)

            # if link['href'].startswith('/search?client'):
            #     pass
            # else:
            #     try:
            #         boom = link.find('h3')
            #         # print(boom.text + ' : ' + link['href'])
            #         url_links.append(link['href'])
            #         titles.append(boom.text)
            #     except:
            #         pass

        # if len(url_links) == len(titles):
        #     print(f'title: {len(titles)} url_links: {len(url_links)}')
        #     for i in range(len(titles)):
        #         print(
        #             '[*]' + titles[i] + '       -----------     ' + url_links[i], end='\n\n\n'
        #         )

        # getting clean links
        for i in range(len(url_links)):
            if 'google' in url_links[i]:
                pass
            else:
                if url_links[i].startswith('/url?q='):
                    pretty_link = (
                        url_links[i]
                        .replace('/url?q=', '')
                        .split('&sa=')[0]
                        .replace(f'%3Fv%3D', '?v=')
                    )
                    # print(f'[*] {titles[i]}')
                    # print('google.com' + url_links[i])
                    # print()
                    pretty_links.append(pretty_link)

        for i in range(3):
            y = random.randint(0, len(pretty_links) - 1)
            print(pretty_links[y])
            wb.open(pretty_links[y])
            html_text1 = requests.get(pretty_links[y]).text
            soup1 = BeautifulSoup(html_text, 'lxml')
            imgs = soup1.find_all('img')
            try:
                if query.lower() in imgs['alt'].replace(' ', '').lower():
                    valid_imgs_link = valid_imgs_link.append('https:' + imgs['source'])

            except:
                print('Sorry Sir, No images found.')

            for i in range(min(1, len(valid_imgs_link))):
                wb.open(valid_imgs_link[i])


main()
