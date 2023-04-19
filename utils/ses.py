import boto3
from botocore.exceptions import ClientError
from utils.env_loader import EMAIL, AWS_REGION_NAME
from utils.error import print_error

if EMAIL is None:
    raise BaseException("Missing env variable EMAIL")

# Create an SES client
ses = boto3.client("ses", region_name=AWS_REGION_NAME)


def is_email_in_ses(email: str):
    try:
        response = ses.list_identities(IdentityType="EmailAddress")
        return email in response["Identities"]
    except ClientError as e:
        print_error(f"Error checking if email {e} is in SES")
        raise Exception(f"Error checking if email {e} is in SES")


def verify_email(email: str):
    try:
        if is_email_in_ses(email):
            print("Email already verified")
            return
        ses.verify_email_identity(EmailAddress=email)
        print("Email verification sent to " + email)
    except ClientError as e:
        print_error("Error verifying email: ", e)
        raise Exception("Error verifying email: ", e)


def send_email_ses(to_address, subject, body):
    # Create the email message
    message = {"Subject": {"Data": subject}, "Body": {"Text": {"Data": body}}}

    try:
        # Send the email using SES
        ses.send_email(
            Source=EMAIL, Destination={"ToAddresses": [to_address]}, Message=message
        )
        print("Email sent to " + to_address)
    except ClientError as e:
        print_error(f"Error sending email to {to_address}", e)
        raise Exception(f"Error sending email to {to_address}", e)
