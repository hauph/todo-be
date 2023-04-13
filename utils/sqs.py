import boto3
import datetime
from utils.env_loader import SQS_URL
from utils.error import print_error
import uuid

if SQS_URL is None:
    raise BaseException("Missing env variables SQS_URL")

# Create an SQS client
sqs = boto3.client("sqs")
sqs.set_queue_attributes(
    QueueUrl=SQS_URL, Attributes={"ContentBasedDeduplication": "true"}
)

message_group_id = str(uuid.uuid4())


def send_to_queue(data, email: str):
    try:
        due_date = datetime.datetime.strptime(
            data["remind_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
        ).strftime("%d-%m-%Y")
        description = data["description"]
        message_body = (
            f"You have task due on {due_date}\nTask description: {description}"
        )

        # Send message to SQS queue
        response = sqs.send_message(
            QueueUrl=SQS_URL,
            MessageAttributes={
                "ToAddress": {"DataType": "String", "StringValue": email},
                "Subject": {"DataType": "String", "StringValue": "Notify email"},
                "DeliveryTime": {
                    "DataType": "String",
                    "StringValue": datetime.datetime.strptime(
                        data["remind_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            },
            MessageBody=message_body,
            MessageGroupId=message_group_id,
        )
        print("Message sent to SQS queue")
        return response["MessageId"]

    except Exception as e:
        print_error("Error sending message to SQS queue", e)
        raise e
