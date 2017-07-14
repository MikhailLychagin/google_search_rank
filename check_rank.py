import argparse
import re
import requests
import logging

from lxml import html

GOOGLE_SEARCH_URL = 'https://www.google.ru'


def get_search_rank(search_query, searched_url):
    url_re = re.compile(searched_url)

    def get_google_search_results(search_query, search_results_offset=0):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36"}
        requests.get(GOOGLE_SEARCH_URL, headers=headers)
        resp = requests.get(GOOGLE_SEARCH_URL + "/search",
                            params={"q": search_query, "start": search_results_offset},
                            headers=headers)
        return resp.text

    href_position_on_page = None
    hrefs_not_matched = 0
    for offset in (0, 10):
        resp = get_google_search_results(search_query, offset)
        tree = html.fromstring(resp)
        all_hrefs = [i.get("href")
                     for i in tree.xpath('//div[@class="g"]//.//h3[@class="r"]//a')
                     if i.get("target") == "_blank" and not i.get("class") == 'sla']
        logging.info("offset={} search_query={} searched_url={} all_hrefs={}".format(offset, search_query, searched_url, all_hrefs))
        try:
            href_position_on_page = (i[0] + 1 for i in enumerate(all_hrefs) if url_re.search(i[1])).__next__()
            return (hrefs_not_matched + href_position_on_page)
        except StopIteration:
            hrefs_not_matched += len(all_hrefs)
    if not href_position_on_page:
        return None


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="Check Google search rank")
    arg_parser.add_argument("search_query", type=str, help="Any query to be searched to check site's rank")
    arg_parser.add_argument("url",
                            type=str,
                            help="Url which rank would be cheched on the first 2 pages of Google search results for search_query")
    args = arg_parser.parse_args()
    search_query = args.search_query
    searched_url = args.url

    res = get_search_rank(search_query, searched_url)
    if res:
        print("The {} rank in search query '{}' is {}".format(searched_url,
                                                              search_query,
                                                              res))
    else:
        print("Site {} is not found on the first 2 pages of Google search on query '{}'".format(searched_url,
                                                                                                search_query))

