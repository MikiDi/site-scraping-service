FROM mikidi/mu-python-template:latest
MAINTAINER Michaël Dierick <michael@dierick.io>

ENV CONTENT_PREDICATE="http://mu.semte.ch/vocabularies/ext/topic-tools/scrapedContent"

ENV URL_QUERY="SELECT DISTINCT ?url WHERE {\
    GRAPH <http://mu.semte.ch/application> {\
        ?id <http://w3id.org/ost/ns#infoUrl> ?url.\
    }\
}"
