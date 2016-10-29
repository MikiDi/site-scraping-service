from multiprocessing import Process

from .scraper import run

@app.route("/")
def exampleMethod():
    # Make the scraping asynchronous for not timing out the http-request
    p = Process(target=run) #args=('bob',)
    p.start()
    p.join(5) #Wait at most x seconds for the scraper to return, (blocking for x seconds)
    if p.exitcode == 0:
        return "successfully scraped"
    else:
        return "Scraping still running ..."
