import elasticsearch
import datetime


timestamp = datetime.datetime.now().timestamp()
timestamp = int(timestamp*1000)

es_client = elasticsearch.Elasticsearch("localhost:9200")

docs = es_client.search(index='system_information',
                        doc_type='doc',
                        body={
                          "size": 0,
                          "_source": {
                            "excludes": []
                          },
                          "aggs": {
                            "2": {
                              "date_histogram": {
                                "field": "@timestamp",
                                "interval": "1d",
                                "time_zone": "Asia/Tokyo",
                                "min_doc_count": 1
                              },
                              "aggs": {
                                "1": {
                                  "avg": {
                                    "field": "CPU"
                                  }
                                }
                              }
                            }
                          },
                          "stored_fields": [
                            "*"
                          ],
                          "script_fields": {},
                          "docvalue_fields": [
                            "@timestamp"
                          ],
                          "query": {
                            "bool": {
                              "must": [
                                {
                                  "match_all": {}
                                },
                                {
                                  "match_phrase": {
                                    "CLIENT_IP.keyword": {
                                      "query": "192.168.137.24"
                                    }
                                  }
                                },
                                {
                                  "range": {
                                    "@timestamp": {
                                      "gte": timestamp - 2419200000,
                                      "lte": timestamp,
                                      "format": "epoch_millis"
                                    }
                                  }
                                }
                              ],
                              "filter": [],
                              "should": [],
                              "must_not": []
                            }
                          }
                        })

print(len(docs['aggregations']['2']['buckets']))
# After programming, use this value if result value is over 2 week

test_list = []

for doc in docs['aggregations']['2']['buckets']:
    print(int(doc['1']['value']))
    test_list.append(int(doc['1']['value']))

print(test_list)
print(test_list[1])
#print(docs['aggregations']['2']['buckets'])
#print(json.dumps(docs['aggregations']['2']['buckets'], indent=2))

#print(es_client.indices.get_alias().keys())