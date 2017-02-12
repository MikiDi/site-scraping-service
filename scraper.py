#!/usr/bin/python3

import os
import urllib
import html.parser

import w3lib.html #Part of the scrapy package
import scrapy.selector

import helpers, escape_helpers

def get_encoding(doc): # Get document encoding from html "meta"-tag
    try:
        return scrapy.selector.Selector(text=doc).xpath('//meta/@charset')\
            .extract()[0].strip()# html5
    except Exception as e:
        try:
            content = scrapy.selector.Selector(text=doc).xpath('//meta[@http-equiv="Content-Type"]/@content')\
                .extract()[0].strip()# html4
            for frag in content.split(';'): # http://stackoverflow.com/questions/4352468/how-to-get-http-equivs-in-python
                s = frag.strip().lower()
                i = s.find('charset=')
                if i > -1:
                    return frag[i+8:] # 8 == len('charset=')
        except Exception:
            return None

def scrape(url):
    try:
        response = urllib.request.urlopen(url)
        encoded_res = response.read()
        enc = get_encoding(encoded_res) if get_encoding(encoded_res) else 'utf-8'
        helpers.log('Determined encoding: {}'.format(enc))
        return encoded_res.decode(enc)
    except urllib.error.HTTPError as e:
        helpers.log('The server at {} couldn\'t fulfill the request.' +
            '\nError code: {}'.format(url, e.code))
        return None
    except urllib.error.URLError as e:
        helpers.log('We failed to reach {}.\nReason: {}'.format(url, e.reason))
        return None

def get_lang(doc): # Get document language from html "lang"-tag
    try:
        return scrapy.selector.Selector(text=doc).xpath('//html/@lang')\
            .extract()[0].split('-')[0].strip().lower()
    except Exception as e:
        return None

def cleanup(doc): #doc = string
    #https://github.com/scrapy/w3lib/blob/master/w3lib/html.py
    res = w3lib.html.remove_tags_with_content(doc, ('script', 'style'))
    res = html.parser.HTMLParser().unescape(res) # stuff like "&amp;"
    res = w3lib.html.replace_tags(res, ' ') # Replace every tag with a space
    res = w3lib.html.remove_comments(res)
    res = w3lib.html.replace_escape_chars(res, which_ones=('\n', '\t', '\r'), \
    replace_by='')
    return res

def run():
    # select_query_form = """
    # SELECT ?url WHERE {{
    #     GRAPH <{0}> {{
    #
    #     }}
    # }}
    # """

    insert_query_form = """
    INSERT DATA {{
        GRAPH <{0}> {{
            <{1}> <{2}> {3}{4}.
        }}
    }}
    """

    select_query = os.getenv('URL_QUERY')
    # select_query = select_query_form.format(os.getenv("MU_APPLICATION_GRAPH"),
    #     os.getenv("SITE_PREDICATE"))

    try:
        results = helpers.query(select_query)["results"]["bindings"]
    except Exception as e:
        helpers.log("Querying SPARQL-endpoint failed:\n{}".format(e))

    for result in results:
        try:
            url = result["url"]["value"]
        except KeyError as e:
            helpers.log('SPARQL query must contain "?url"')
        # if url in urls: #check if url already has scraped text in store
        #     continue
        try:
            helpers.log("Getting URL \"{}\"".format(url))
            doc_before = scrape(url)
            if  not doc_before: continue
            doc_lang = get_lang(doc_before)
            doc_after = cleanup(doc_before)
            insert_query = insert_query_form.format(os.getenv('MU_APPLICATION_GRAPH'),
                url, os.getenv('CONTENT_PREDICATE'),
                escape_helpers.sparql_escape(doc_after),
                '@'+doc_lang if doc_lang else '')
            try:
                helpers.update(insert_query)
            except Exception as e:
                helpers.log("Querying SPARQL-endpoint failed:\n{}".format(e))
                continue
        except Exception as e:
            helpers.log("Something went wrong ...\n{}".format(str(e)))
            continue
