[![test](https://github.com/mailtrap/mailtrap-python/actions/workflows/main.yml/badge.svg)](https://github.com/mailtrap/mailtrap-python/actions/workflows/main.yml)
[![PyPI](https://shields.io/pypi/v/mailtrap)](https://pypi.org/project/mailtrap/)
[![downloads](https://shields.io/pypi/dm/mailtrap)](https://pypi.org/project/mailtrap/)


# Official Mailtrap Python client

This Python package offers integration with the [official API](https://api-docs.mailtrap.io/) for [Mailtrap](https://mailtrap.io).

Add email sending functionality to your Python application quickly with Mailtrap.

## Compatibility with previous releases

Versions of this package up to 1.0.1 were different, unrelated project, that is now maintained as [Sendria](https://github.com/msztolcman/sendria). To continue using it, see [instructions](#information-for-version-1-users).

## Installation

### Prerequisites

- Python version 3.9+

### Install package

```text
pip install mailtrap
```

## Usage

### Minimal usage (Transactional sending)

```python
import mailtrap as mt

API_TOKEN = "<YOUR_API_TOKEN>"  # your API key here https://mailtrap.io/api-tokens

client = mt.MailtrapClient(token=API_TOKEN)

# Create mail object
mail = mt.Mail(
    sender=mt.Address(email="sender@example.com", name="John Smith"),
    to=[mt.Address(email="recipient@example.com")],
    subject="You are awesome!",
    text="Congrats for sending test email with Mailtrap!",
)

client.send(mail)
```

### Sandbox vs Production (easy switching)

Mailtrap lets you test safely in the Email Sandbox and then switch to Production (Sending).
Remove the inbox_id field or set it to None. Then, remove the sandbox field or set it to False.
You can change the arguments in the code or via another way. Here is an example using environment variables.

Set next environment variables:
```bash
MAILTRAP_API_KEY=your_api_token # https://mailtrap.io/api-tokens
MAILTRAP_USE_SANDBOX=true       # true/false toggle
MAILTRAP_INBOX_ID=123456        # Only needed for sandbox
```

Bootstrap logic:
```python
import os
import mailtrap as mt

API_KEY = os.environ["MAILTRAP_API_KEY"]
IS_SANDBOX = os.environ.get("MAILTRAP_USE_SANDBOX", "true").lower() == "true"
INBOX_ID = os.environ.get("MAILTRAP_INBOX_ID")

client = mt.MailtrapClient(
  token=API_KEY,
  sandbox=IS_SANDBOX,
  inbox_id=INBOX_ID,  # None is ignored for production
)

# Create mail object
mail = mt.Mail(
    sender=mt.Address(email="sender@example.com", name="John Smith"),
    to=[mt.Address(email="recipient@example.com")],
    subject="You are awesome!",
    text="Congrats for sending test email with Mailtrap!",
)

client.send(mail)
```

Bulk stream example (optional) differs only by setting `bulk=True`:
`bulk_client = mt.MailtrapClient(token=API_KEY, bulk=True)`

Recommendations:
- Use separate API tokens for Production and Sandbox.
- Keep initialisation in a single factory object/service so that switching is centralised.

### Full-featured usage example

```python
import base64
import os
from pathlib import Path

import mailtrap as mt

client = mt.MailtrapClient(token=os.environ["MAILTRAP_API_KEY"])

welcome_image = Path(__file__).parent.joinpath("welcome.png").read_bytes()


mail = mt.Mail(
    sender=mt.Address(email="mailtrap@example.com", name="Mailtrap Test"),
    to=[mt.Address(email="your@email.com", name="Your name")],
    cc=[mt.Address(email="cc@email.com", name="Copy to")],
    bcc=[mt.Address(email="bcc@email.com", name="Hidden Recipient")],
    subject="You are awesome!",
    text="Congrats for sending test email with Mailtrap!",
    html="""
    <!doctype html>
    <html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
      </head>
      <body style="font-family: sans-serif;">
        <div style="display: block; margin: auto; max-width: 600px;" class="main">
          <h1 style="font-size: 18px; font-weight: bold; margin-top: 20px">
            Congrats for sending test email with Mailtrap!
          </h1>
          <p>Inspect it using the tabs you see above and learn how this email can be improved.</p>
          <img alt="Inspect with Tabs" src="cid:welcome.png" style="width: 100%;">
          <p>Now send your email using our fake SMTP server and integration of your choice!</p>
          <p>Good luck! Hope it works.</p>
        </div>
        <!-- Example of invalid for email html/css, will be detected by Mailtrap: -->
        <style>
          .main { background-color: white; }
          a:hover { border-left-width: 1em; min-height: 2em; }
        </style>
      </body>
    </html>
    """,
    category="Test",
    attachments=[
        mt.Attachment(
            content=base64.b64encode(welcome_image),
            filename="welcome.png",
            disposition=mt.Disposition.INLINE,
            mimetype="image/png",
            content_id="welcome.png",
        )
    ],
    headers={"X-MT-Header": "Custom header"},
    custom_variables={"year": 2023},
)

client.send(mail)
```

### Minimal usage of email template

```python
import os
import mailtrap as mt

client = mt.MailtrapClient(token=os.environ["MAILTRAP_API_KEY"])

# create mail object
mail = mt.MailFromTemplate(
    sender=mt.Address(email="mailtrap@example.com", name="Mailtrap Test"),
    to=[mt.Address(email="your@email.com")],
    template_uuid="2f45b0aa-bbed-432f-95e4-e145e1965ba2",
    template_variables={"user_name": "John Doe"},
)

client.send(mail)
```

### Sending email directly via SendingApi

This approach is newer. It can be useful when you expect  the response to be model-based rather than dictionary-based, as in MailtrapClient.send().

```python
import os
import mailtrap as mt

client = mt.MailtrapClient(token=os.environ["MAILTRAP_API_KEY"])
sending_api = client.sending_api

# create mail object
mail = mt.Mail(
    sender=mt.Address(email="sender@example.com", name="John Smith"),
    to=[mt.Address(email="recipient@example.com")],
    subject="You are awesome!",
    text="Congrats for sending test email with Mailtrap!",
)

sending_api.send(mail)
```
#### Mailtrap sending responses difference

#### 1. `client.send()`
**Response:**
```python
{
  "success": True,
  "message_ids": ["5162954175"]
}
```

#### 2. `client.sending_api.send()`
**Response:**
```python
SendingMailResponse(success=True, message_ids=["5162955057"])
```

The same situation applies to both `client.batch_send()` and `client.sending_api.batch_send()`.

## Supported functionality & Examples

### Email API:
- Send an email (Transactional and Bulk streams) – [`sending/minimal_sending.py`](examples/sending/minimal_sending.py)
- Send an email with a template (Transactional and Bulk streams) – [`sending/sending_with_template.py`](examples/sending/sending_with_template.py)
- Send a batch of emails (Transactional and Bulk streams) – [`sending/batch_minimal_sending.py`](examples/sending/batch_minimal_sending.py)
- Send a batch of emails with a template (Transactional and Bulk streams) – [`sending/batch_sending_with_template.py`](examples/sending/batch_sending_with_template.py)
- Advanced sending – [`sending/advanced_sending.py`](examples/sending/advanced_sending.py)
- Advanced batch sending – [`sending/batch_advanced_sending.py`](examples/sending/batch_advanced_sending.py)

### Email Sandbox (Testing) API:
- Attachments management – [`testing/attachments.py`](examples/testing/attachments.py)
- Inboxes management – [`testing/inboxes.py`](examples/testing/inboxes.py)
- Messages management – [`testing/messages.py`](examples/testing/messages.py)
- Projects management – [`testing/projects.py`](examples/testing/projects.py)

### Contacts API:
- Contacts management – [`contacts/contacts.py`](examples/contacts/contacts.py)
- Contact Lists management – [`contacts/contact_lists.py`](examples/contacts/contact_lists.py)
- Contact Fields management – [`contacts/contact_fields.py`](examples/contacts/contact_fields.py)
- Contact Events – [`contacts/contact_events.py`](examples/contacts/contact_events.py)
- Contact Exports – [`contacts/contact_exports.py`](examples/contacts/contact_exports.py)
- Contact Imports – [`contacts/contact_imports.py`](examples/contacts/contact_imports.py)

### Email Templates API:
- Templates management – [`email_templates/templates.py`](examples/email_templates/templates.py)

### Suppressions API:
- Suppressions (find & delete) – [`suppressions/suppressions.py`](examples/suppressions/suppressions.py)

### General API:
- Account Accesses management – [`general/account_accesses.py`](examples/general/account_accesses.py)
- Accounts info – [`general/accounts.py`](examples/general/accounts.py)
- Billing info – [`general/billing.py`](examples/general/billing.py)
- Permissions listing – [`general/permissions.py`](examples/general/permissions.py)

## Contributing

Bug reports and pull requests are welcome on [GitHub](https://github.com/mailtrap/mailtrap-python). This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the [code of conduct](CODE_OF_CONDUCT.md).

### Development Environment

#### Clone the repo

```bash
git clone https://github.com/mailtrap/mailtrap-python.git
cd mailtrap-python
```

#### Install [tox](https://tox.wiki/en/latest/installation.html)

`tox` is an environment orchestrator. We use it to setup local environments, run tests and execute linters.

```bash
python -m pip install --user tox
python -m tox --help
```

To setup virtual environments, run tests and linters use:

```bash
tox
```

It will create virtual environments with all installed dependencies for each available python interpreter (starting from `python3.9`) on your machine.
By default, they will be available in `{project}/.tox/` directory. So, for instance, to activate `python3.11` environment, run the following:

```bash
source .tox/py311/bin/activate
```

## Information for version 1 users

If you are a version 1 user, it is advised that you upgrade to [Sendria](https://github.com/msztolcman/sendria), which is the same package, but under a new name, and with [new features](https://github.com/msztolcman/sendria#changelog). However, you can also continue using the last v1 release by locking the version in pip:

```sh
# To use the FORMER version of the mailtrap package, now known as Sendria:
pip install --force-reinstall -v "mailtrap==1.0.1"
```

## License

The project is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).

## Code of Conduct

Everyone interacting in the Mailtrap project's codebases, issue trackers, chat rooms and mailing lists is expected to follow the [code of conduct](CODE_OF_CONDUCT.md)
