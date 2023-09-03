import boto3
import logging
from decouple import config
from botocore.exceptions import ClientError


class SESService:
    """Encapsulates functions to send emails with Amazon SES."""

    def __init__(self):
        self.key = config("AWS_ACCESS_KEY")
        self.secret = config("AWS_SECRET")
        self.ses_client = boto3.client(
            "ses",
            region_name=config("AWS_REGION"),
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret,
        )

    def send_email(self,
                   source,
                   destination,
                   subject,
                   text,
                   html,
                   reply_tos=None
                   ):
        """
        Send email.

        Note: If your account is in the Amazon SES  sandbox, the source and
        destination email accounts must both be verified.

        :param source: The source email account.
        :param destination: The destination email account.
        :param subject: The subject of the email.
        :param text: The plain text version of the body of the email.
        :param html: The HTML version of the body of the email.
        :param reply_tos: Email accounts that will receive a reply if the
                          recipient replies to the message.
        :return: The ID of the message, assigned by Amazon SES.
        """
        send_args = {
            'Source': source,
            # 'Destination': destination.to_service_format(),
            'Destination': {
                "ToAddresses": destination,
                "CcAddresses": [],
                "BccAddresses": []
            },
            'Message': {
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': text}, 'Html': {'Data': html}}}
        }
        if reply_tos is not None:
            send_args['ReplyToAddresses'] = reply_tos
        try:
            response = self.ses_client.send_email(**send_args)
            message_id = response['MessageId']
            logging.info(
                "Sent mail %s from %s to %s.",
                message_id,
                source,
                destination[0]  # Hardcoded first direction
            )
        except ClientError:
            logging.exception(
                "Couldn't send mail from %s to %s.",
                source,
                destination[0]  # Hardcoded first direction
            )
            raise
        else:
            return message_id
