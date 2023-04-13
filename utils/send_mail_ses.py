import boto3
from botocore.exceptions import ClientError
from utils.env_loader import EMAIL

if EMAIL is None:
    raise BaseException("Missing env variable EMAIL")

# Create an SES client
ses = boto3.client("ses")


def send_email(to_address, subject, body):
    # Create the email message
    message = {"Subject": {"Data": subject}, "Body": {"Text": {"Data": body}}}

    try:
        # Send the email using SES
        response = ses.send_email(
            Source=EMAIL, Destination={"ToAddresses": [to_address]}, Message=message
        )
        print("Email sent to " + to_address)
    except ClientError as e:
        print("Error sending email to " + to_address + ": " + str(e))
