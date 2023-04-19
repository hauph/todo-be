import boto3
import datetime
import time
import uuid
from utils.env_loader import SQS_URL, AWS_REGION_NAME
from utils.send_mail_normal import send_email
from utils.ses import send_email_ses, is_email_in_ses
from utils.error import print_error
from utils.db import get_db
from utils.time import is_in_retention_period
from utils.sqs import send_to_queue
from controllers.todo import edit_user_todo, get_task_by_message_id

if SQS_URL is None:
    raise BaseException("Missing env variables SQS_URL")

# Create an SQS client
sqs = boto3.client("sqs", region_name=AWS_REGION_NAME)


def scheduler():
    print("=============Scheduler starts=============")
    db = get_db()

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
            # Check if any messages were received
            if "Messages" in response:
                # Process each message
                for message in response["Messages"]:
                    message_id = message["MessageId"]
                    # Extract the message body
                    body = message["Body"]
                    # Extract the message attributes
                    to_address = message["MessageAttributes"]["ToAddress"][
                        "StringValue"
                    ]

                    task = get_task_by_message_id(db, message_id)
                    if task:
                        created_at, remind_at = task.created_at, task.remind_at

                        if is_in_retention_period(
                            int(created_at.timestamp()), int(remind_at.timestamp())
                        ):
                            subject = message["MessageAttributes"]["Subject"][
                                "StringValue"
                            ]
                            delivery_time = message["MessageAttributes"][
                                "DeliveryTime"
                            ]["StringValue"]

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
                                    QueueUrl=SQS_URL,
                                    ReceiptHandle=message["ReceiptHandle"],
                                )
                        else:
                            # Delete the message from the SQS queue
                            sqs.delete_message(
                                QueueUrl=SQS_URL, ReceiptHandle=message["ReceiptHandle"]
                            )

                            # Resend the message to the SQS queue
                            requestBody = {
                                "remind_at": remind_at.strftime(
                                    "%Y-%m-%dT%H:%M:%S.%fZ"
                                ),
                                "description": task.description,
                            }
                            message_id = send_to_queue(
                                requestBody, to_address, str(uuid.uuid4())
                            )
                            edit_user_todo(db, task.id, {"message_id": message_id})
                            print("Messages resent to queue.")

                    else:
                        # Delete the message from the SQS queue
                        sqs.delete_message(
                            QueueUrl=SQS_URL, ReceiptHandle=message["ReceiptHandle"]
                        )
            else:
                print("No messages received from queue.")
        except Exception as e:
            print_error("Error processing queue messages", e)
            raise Exception("Error processing queue messages")

        # Sleep for a period of time before checking the queue again
        time.sleep(60)
