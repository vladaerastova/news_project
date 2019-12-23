import os
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from news_project import mailgun_api_key, celery


@celery.task
def send_email(to, subject, template):
    message = Mail(
        from_email='from_email@example.com',
        to_emails=to,
        subject=subject,
        html_content=template)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


def get_validate(email):
    return requests.get(
        "https://api.mailgun.net/v4/address/validate",
        auth=("api", mailgun_api_key),
        params={"address": email})

