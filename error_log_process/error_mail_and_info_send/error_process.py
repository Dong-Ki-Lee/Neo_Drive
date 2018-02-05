import pymongo
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MAIL_ACCOUNT = "vinedingproject@gmail.com"
MAIL_PASSWORD = "onlysendmail"


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
            output_list.append(admin['email_address'])

        return output_list
    except Exception as e:
        print(e)
    finally:
        client.close()


def create_email_content(error_json):

    email_content = 'host : ' \
               + error_json['_id']['error_ip'] \
               + ' error name : ' \
               + error_json['_id']['error_name'] \
               + ' ' + str(error_json['count']) \
               + ' times alert\n'
    return email_content


def get_error_host_and_description():
    try:
        # connect local mongodb server
        client = pymongo.MongoClient("localhost", 26543)

        # setting database and collection name
        error_db = client["server_data"]
        error_coll = error_db["error_log"]
        error_aggregation = error_coll.aggregate(
            [
                {
                    "$group": {
                        "_id": {"error_name": "$error_name", "error_ip": "$error_ip"},
                        "count": {"$sum": 1}
                    }
                }
            ]
        )

        output_list = []
        for error in error_aggregation:
            print(error)
            output_list.append(error)

        error_coll.drop()
        return output_list

    except Exception as e:
        print(e)
    finally:
        client.close()

alarm_timing = input("input alarm interval(minute) : ")

while(True):
    administrator_list = get_administrator_email_list()

    error_list = get_error_host_and_description()

    content = ''
    if len(error_list) > 0:
        for error in error_list:
            content += create_email_content(error)

        print(content)

        send_via_gmail(administrator_list, "Alarm_email", content)
    else:
        print("no_error_list")
    print("wait " + str(alarm_timing) + " minutes")
    time.sleep(60 * int(alarm_timing))
