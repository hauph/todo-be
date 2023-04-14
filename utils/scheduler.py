import boto3
import datetime
import time
from utils.env_loader import SQS_URL
from utils.send_mail_normal import send_email
from utils.ses import send_email_ses, is_email_in_ses
from utils.error import print_error

if SQS_URL is None:
    raise BaseException("Missing env variables SQS_URL")

# Create an SQS client
sqs = boto3.client("sqs")


def scheduler():
    print("=============Scheduler starts=============")
    while True:
        print("=============Scheduler is running=============")
        try:
            # Receive messages from the SQS queue
            response = sqs.receive_message(
                QueueUrl=SQS_URL,
                MessageAttributeNames=["All"]
                # MaxNumberOfMessages=10,
                # VisibilityTimeout=30,
                # WaitTimeSeconds=20,
            )
            print("=============Scheduler received message=============")
            print(response)
            # Check if any messages were received
            if "Messages" in response:
                # Process each message
                for message in response["Messages"]:
                    # Extract the message body
                    body = message["Body"]

                    # Extract the message attributes
                    to_address = message["MessageAttributes"]["ToAddress"][
                        "StringValue"
                    ]
                    subject = message["MessageAttributes"]["Subject"]["StringValue"]
                    delivery_time = message["MessageAttributes"]["DeliveryTime"][
                        "StringValue"
                    ]

                    # Check if the delivery time has been reached
                    if datetime.datetime.now() >= datetime.datetime.strptime(
                        delivery_time, "%Y-%m-%d %H:%M:%S.%f"
                    ):
                        if is_email_in_ses(to_address):
                            # Send the email using SES
                            send_email_ses(to_address, subject, body)
                        else:
                            # Send the email using SMTP
                            send_email(to_address, subject, body)

                        # Delete the message from the SQS queue
                        sqs.delete_message(
                            QueueUrl=SQS_URL, ReceiptHandle=message["ReceiptHandle"]
                        )
                    # else:
                    #     print(
                    #         "Message with delivery time "
                    #         + delivery_time
                    #         + " has not been delivered yet."
                    #     )
            else:
                print("No messages received from queue.")
        except Exception as e:
            print_error("Error processing queue messages", e)
            raise e

        # Sleep for a period of time before checking the queue again
        time.sleep(60)
