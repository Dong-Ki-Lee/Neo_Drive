import elasticsearch
import datetime


def calculate_future_usage(input_list):
    for i in range(0, 14):
        diff = input_list[i + 7] - input_list[i]
        input_list.append(input_list[i + 7] + diff)
    return input_list


# Time to calculate the past. Here, based on current
timestamp = datetime.datetime.now().timestamp()
# Modify elasticsearch timestamp format
timestamp = int(timestamp*1000)

# Connect Elasticsearch for getting Usage Value. Now just calculate CPU
es_client = elasticsearch.Elasticsearch("localhost:9200")

ip = "192.168.137.24"

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

# More than 14 days of data must be stored to perform the calculation
if (len(docs['aggregations']['2']['buckets'])) >= 14:

    cpu_usage_list = []

    # Add list CPU usage past 2 weeks
    for doc in docs['aggregations']['2']['buckets']:
        print(int(doc['1']['value']))
        cpu_usage_list.append(int(doc['1']['value']))

    # Call function calculate future usage
    cpu_usage_list = calculate_future_usage(cpu_usage_list)

    # Convert to the format used by elasticsearch

    # Delete historical data from elasticsearch

    # Insert new prediction data

# Less than 14 days of data pass this calculation
# else:
    # if need another process, write this place

# close connection
