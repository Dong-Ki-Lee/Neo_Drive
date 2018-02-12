import elasticsearch
import datetime
import time
import pymongo


def get_client_ip_address_list_in_access_log():
    try:
        # connect local mongodb server
        mongo_client = pymongo.MongoClient("localhost", 26543)

        # setting database and collection name
        server_db = mongo_client["server_data"]
        access_coll = server_db["access_log"]

        # grouping access log by ip address
        ip_address_list = access_coll.aggregate(
            [
                {
                    "$group": {
                        "_id": {"IP": "$IP"},
                        "count": {"$sum": 1}
                    }
                }
            ]
        )

        output_list = []
        for ip_address in ip_address_list:
            print(ip_address['_id']['IP'])
            output_list.append(ip_address['_id']['IP'])

        return output_list

    except Exception as e:
        print(e)
    finally:
        mongo_client.close()


def calculate_future_usage(input_list):
    for i in range(0, 14):
        diff = input_list[i + 7] - input_list[i]
        next_prediction = input_list[i + 7] + diff

        if next_prediction >= 5:
            input_list.append(next_prediction)
        else:
            last_week_value = input_list[i+7]
            input_list.append(last_week_value)
    return input_list


def insert_future_data(input_ip_address):

    # Time to calculate the past. Here, based on current
    timestamp = datetime.datetime.now().timestamp()
    # Modify elasticsearch timestamp format
    timestamp = int(timestamp*1000)

    # Connect Elasticsearch for getting Usage Value. Now just calculate CPU
    es_client = elasticsearch.Elasticsearch("localhost:9200")

    # Get usage data use aggregation
    usage_data = es_client.search(index='system_information',
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
                                          "query": input_ip_address
                                        }
                                      }
                                    },
                                    {
                                      "range": {
                                        "@timestamp": {
                                          "gte": timestamp - 1209600000,
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
    if (len(usage_data['aggregations']['2']['buckets'])) >= 14:

        cpu_usage_list = []

        # Add list CPU usage past 2 weeks
        for doc in usage_data['aggregations']['2']['buckets']:
            # print(int(doc['1']['value']))
            cpu_usage_list.append(int(doc['1']['value']))

        # if get 15 days data, only get recent 14 days data.
        if len(cpu_usage_list) > 14:
            cpu_usage_list = cpu_usage_list[1:]

        # Call function calculate future usage
        cpu_usage_prediction_list = calculate_future_usage(cpu_usage_list)
        print(cpu_usage_prediction_list)
        # Convert to the format used by elasticsearch
        now = datetime.datetime.now()

        default_date = now + datetime.timedelta(days=-13)
        delta_value = 0
        for cpu_usage in cpu_usage_list:
            elastic_data = {
                'date': (default_date + datetime.timedelta(days=delta_value)).strftime('%Y-%m-%d'),
                'cpu_usage': cpu_usage,
                'CLIENT_IP': ip
            }
            # Insert new prediction data
            es_client.index(index="cpu_prediction_data", doc_type="cpu_prediction", body=elastic_data)
            delta_value += 1
        # Delete historical data from elasticsearch


if __name__ == "__main__":

    ip_list = get_client_ip_address_list_in_access_log()
    for ip in ip_list:
        insert_future_data(ip)
    print("wait 1 day")
