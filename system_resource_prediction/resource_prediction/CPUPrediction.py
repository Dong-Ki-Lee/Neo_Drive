import elasticsearch
import json

es_client = elasticsearch.Elasticsearch("localhost:9200")

docs = es_client.search(index='system_information',
                        doc_type='doc',
                        body={
                            {
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
                                      "range": {
                                        "@timestamp": {
                                          "gte": 1516238370297,
                                          "lte": 1516843170297,
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
                            }
                        }
                        )
print(json.dumps(docs, indent=2))
print(es_client.indices.get_alias().keys())