import pymongo
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ALARM_MAIL_SEND_ACCOUNT_ID = "vinedingproject@gmail.com"
ALARM_MAIL_SEND_ACCOUNT_PW = "onlysendmail"
SMTP_SERVER_ADDRESS_GMAIL = "smtp.gmail.com:587"
DB_PORT = 26543


def send_email_use_smtp(recipient_list, title, content_string):
    try:
        # connect and login smtp email server
        smtp = smtplib.SMTP(SMTP_SERVER_ADDRESS_GMAIL)
        smtp.starttls()
        smtp.login(
            ALARM_MAIL_SEND_ACCOUNT_ID,
            ALARM_MAIL_SEND_ACCOUNT_PW
        )

        # transform string to email content
        msg = MIMEMultipart('localhost')
        msg['Subject'] = title
        msg['From'] = ALARM_MAIL_SEND_ACCOUNT_ID

        content_email_form = MIMEText(content_string, 'plain', _charset="utf-8")
        msg.attach(content_email_form)

        # send email all recipients
        for recipient in recipient_list:
            try:
                smtp.sendmail(ALARM_MAIL_SEND_ACCOUNT_ID, recipient, msg.as_string())

            except Exception as exception:
                print(exception)
                print("Email is not sent due to error")

    except Exception as exception:
        print(exception)
        print("Login Failed")


def get_administrator_email_list():
    try:
        client = pymongo.MongoClient("localhost", DB_PORT)

        admin_db = client["administrator"]
        admin_coll = admin_db["administrator_list"]

        admin_information = admin_coll.find()

        admin_account_list = []

        for admin in admin_information:
            admin_account_list.append(admin['email_address'])

        return admin_account_list
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
        client = pymongo.MongoClient("localhost", DB_PORT)

        # setting database and collection name
        error_db = client["server_data"]
        error_coll = error_db["error_log"]

        # get error information
        error_aggregation_output = error_coll.aggregate(
            [
                {
                    "$group": {
                        "_id": {"error_name": "$error_name", "error_ip": "$error_ip"},
                        "count": {"$sum": 1}
                    }
                }
            ]
        )
        error_coll.drop()

        error_list = []
        for error_info in error_aggregation_output:
            print(error_info)
            error_list.append(error_info)

        return error_list

    except Exception as e:
        print(e)
    finally:
        client.close()


if __name__ == "__main__":

    alarm_timing = input("input alarm interval(minute) : ")

    while True:
        administrator_list = get_administrator_email_list()

        error_list = get_error_host_and_description()

        content = ''
        if len(error_list) > 0:
            for error in error_list:
                content += create_email_content(error)

            content += '\n자세한 내용은 다음 링크에서 확인하세요\n'
            content += 'http://164.125.14.150:5601/app/kibana#/dashboards'

            send_email_use_smtp(administrator_list, "Alarm_email", content)

            print("send alarm mail")
        else:
            print("no_error_list")
        print("wait " + str(alarm_timing) + " minutes")
        time.sleep(60 * int(alarm_timing))
