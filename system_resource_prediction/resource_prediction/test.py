
import pymongo


def get_error_host_and_description():
    try:
        # connect local mongodb server
        client = pymongo.MongoClient("localhost", 26543)

        # setting database and collection name
        access_db = client["server_data"]
        access_coll = access_db["access_log"]
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
            output_list.append(ip_address)

        return output_list

    except Exception as e:
        print(e)
    finally:
        client.close()


get_error_host_and_description()