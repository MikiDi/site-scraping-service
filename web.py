import helpers, escape_helpers


@app.route("/")
def exampleMethod():
    return escape_helpers.sparql_escape('the man\'s world is "hello world"')

@app.route("/a")
def exampleMethod2():
    return "ac"

@app.route("/b")
def exampleMethod3():
    return "ac"
