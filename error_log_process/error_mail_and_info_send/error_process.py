import pymongo
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MAIL_ACCOUNT = "vinedingproject@gmail.com"
MAIL_PASSWORD = "onlysendmail"
TITLE = ""
CONTENT = ""


def send_via_gmail(to_list, title, description):
    try:
        from_address = MAIL_ACCOUNT
        s = smtplib.SMTP('smtp.gmail.com:587')
        s.starttls()
        s.login(MAIL_ACCOUNT, MAIL_PASSWORD)
        msg = get_message_formatted(from_address, title, description)
        for to in to_list:
            try:
                s.sendmail(from_address, to, msg.as_string())

            except Exception as e:
                print(e)
                print("email_send_error")
    except Exception as e:
        print(e)
        print("login error")


def get_message_formatted(from_address, title, description):
    msg = MIMEMultipart('localhost')
    msg['Subject'] = title
    msg['From'] = from_address

    content = MIMEText(description, 'plain', _charset="utf-8")
    msg.attach(content)
    return msg


def get_administrator_email_list():
    try:
        client = pymongo.MongoClient("localhost", 26543)

        admin_db = client["administrator"]
        admin_coll = admin_db["administrator_list"]

        admin_list = admin_coll.find()

        output_list = []

        for admin in admin_list:
            print(admin['email_address'])
            output_list.append(admin['email_address'])

        return output_list
        # collection.remove({"search_word": search_word})
    except Exception as e:
        print(e)
    finally:
        client.close()


def get_error_host_and_description():
    try:
        # connect local mongodb server
        client = pymongo.MongoClient("localhost", 26543)

        # setting database and collection name
        error_db = client["client_system_limit_error"]
        error_coll = error_db["cpu_over_limit"]
        error_aggregation = error_coll.aggregate(
            [
                {
                    "$group": {
                        "_id": {"error_name": "$error_name", "IP": "$IP"},
                        "count": {"$sum": 1}
                    }
                }
            ]
        )

        output_list = []
        for error in error_aggregation:
            print(error)
            output_list.append(error)

        return output_list

    except Exception as e:
        print(e)
    finally:
        client.close()

# read problem data from mongodb

# remove duplication

# remove old data from elasticsearch

# send problem data to information viewer

# send problem data to administrator use email

test_list = get_administrator_email_list()
print(test_list[0])

test_list2 = get_error_host_and_description()

content = ''
for list in test_list2:
    content += 'host : ' \
               + list['_id']['IP'] \
               + ' error name : ' \
               + list['_id']['error_name'] \
               + ' ' + str(list['count']) \
               + ' times alert\n'

print(content)

send_via_gmail(test_list, "test_email", content)