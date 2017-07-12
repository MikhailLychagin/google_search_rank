import argparse
import re
from http.client import HTTPSConnection
from urllib import parse

from lxml import html

GOOGLE_SEARCH_URL = 'https://www.google.ru'


def get_search_rank(search_query, searched_url):
    url_re = re.compile(searched_url)

    def get_google_search_results(search_query, search_results_offset=0):
        con = HTTPSConnection(parse.urlparse(GOOGLE_SEARCH_URL).hostname, 80, timeout=10)
        con.request("GET", "/search?" + parse.urlencode({"q": search_query, "start": search_results_offset}))
        resp = con.getresponse()
        return str(resp.read())

    href_position_on_page = None
    hrefs_not_matched = 0
    for offset in (0, 10):
        try:
            resp = get_google_search_results(search_query, offset)
        except OSError as e:
            print("Can't get search rank: " + str(e))
            return
        tree = html.fromstring(resp)
        all_hrefs = [i.get("href")
                     for i in tree.xpath('//div[@class="g"]//.//h3[@class="r"]//a')
                     if i.get("target") == "_blank" and not i.get("class") == 'sla']
        try:
            href_position_on_page = (i[0] + 1 for i in enumerate(all_hrefs) if url_re.search(i[1])).__next__()
            print("Site {} rank in search query '{}' is {}".format(searched_url,
                                                                   search_query,
                                                                   hrefs_not_matched + href_position_on_page))
            break
        except StopIteration:
            hrefs_not_matched += len(all_hrefs)
    if not href_position_on_page:
        print("Site {} is not found on the first 2 pages of Google search on query '{}'".format(searched_url,
                                                                                                search_query))


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="Check Google search rank")
    arg_parser.add_argument("search_query", type=str, help="Any query to be searched to check site's rank")
    arg_parser.add_argument("url",
                            type=str,
                            help="Url which rank would be cheched on the first 2 pages of Google search results for search_query")
    args = arg_parser.parse_args()

    res = get_search_rank(args.search_query, args.url)
