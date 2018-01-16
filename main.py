# Author: Sezer Yavuzer Bozkir <admin@sezerbozkir.com>
# Created Date: 16.01.2018
import requests
from bs4 import BeautifulSoup
from json import dump
import xlsxwriter


def scrape_redirects(site_link, domain_base):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(site_link, headers=headers)
    site_source = r.content
    try:
        soup = BeautifulSoup(site_source, "html.parser")
        href_links = soup.find_all(href=True)
        if href_links:
            for link in href_links:
                tmp_link = link.get('href')
                check_url(site_link, tmp_link)
                if domain_base in tmp_link and tmp_link != site_link and tmp_link not in scanned:
                    # print("href: ", tmp_link)
                    scanned.append(tmp_link)
                    scrape_redirects(tmp_link, domain_base=domain_base)
        img_links = soup.find_all("img")
        if img_links:
            for link in soup.find_all("img"):
                tmp_link = link['src']
                check_url(site_link, tmp_link)
                if domain_base in tmp_link and tmp_link != site_link and tmp_link not in scanned and not tmp_link.endswith(('.png', '.jpg')):
                    # print("src: ", tmp_link)
                    scanned.append(tmp_link)
                    scrape_redirects(tmp_link, domain_base=domain_base)
        script_links = soup.find_all("script", {'src': True})
        if script_links:
            for link in soup.find_all("script", {'src': True}):
                tmp_link = link['src']
                check_url(site_link, tmp_link)
                if domain_base in tmp_link and tmp_link != site_link and tmp_link not in scanned:
                    # print("script: ", tmp_link)
                    scanned.append(tmp_link)
                    scrape_redirects(tmp_link, domain_base=domain_base)
        style_links = soup.find_all("a", {"style": True})
        for link in style_links:
            tmp_link = link['style'].split("('", 1)[1].split("')")[0]
            check_url(site_link, tmp_link)
            if domain_base in tmp_link and tmp_link != site_link and tmp_link not in scanned:
                # print("style: ", tmp_link)
                scanned.append(tmp_link)
                scrape_redirects(tmp_link, domain_base=domain_base)
    except Exception as e:
        print(e)


def check_url(path, url):
    if url.startswith("http://"):
        path = path if not path.endswith("/") else path[:-1]
        if path in http_links.keys():
            if url not in http_links[path]:
                http_links[path].append(url)
        else:
            http_links[path] = [url]


if __name__ == '__main__':
    scanning_domains = {
        "sezerbozkir": "https://sezerbozkir.com",
    }
    save_type = {
        "json": True,
        "excel": False
    }
    if save_type["excel"]:
        workbook = xlsxwriter.Workbook('http_kalan_linkler.xlsx', {'strings_to_urls': False})
    for site_name, site_url in scanning_domains.items():
        http_links = {}
        scanned = []
        scrape_redirects(site_url, site_name)
        if save_type["excel"]:
            worksheet = workbook.add_worksheet(site_name)
            cell_format = workbook.add_format({'bold': True})
            worksheet.write(0, 0, "Site Adresi", cell_format)
            worksheet.write(0, 1, "Http linkler", cell_format)
            row_order = 1
            for link, content in http_links.items():
                worksheet.write(row_order, 0, link)
                worksheet.write(row_order, 1, "\n".join(x for x in content))
                row_order += 1
        if save_type['json']:
            with open(site_name + ".json", 'w') as fp:
                dump(http_links, fp)
    if save_type['excel']:
        workbook.close()
