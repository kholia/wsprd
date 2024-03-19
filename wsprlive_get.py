import urllib.request
import json

def wsprlive_get(query):
    # put together the request url
    url = "https://db1.wspr.live/?query=" + urllib.parse.quote_plus(query + " FORMAT JSON")

    # download contents from wspr.live
    contents = urllib.request.urlopen(url).read()

    # return the json decoded data
    return json.loads(contents.decode("UTF-8"))["data"]

if __name__ == "__main__":
    print(wsprlive_get("SELECT * FROM rx LIMIT 1"))
