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

### All usage examples

Refer to the [examples](examples) folder for the source code of this and other advanced examples.

### Sending API
- [Sending minimal](examples/sending/minimal_sending.py)
- [Sending advanced](examples/sending/advanced_sending.py)
- [Sending using template](examples/sending/sending_with_template.py)

### Batch Sending API
- [Batch sending minimal](examples/sending/batch_minimal_sending.py)
- [Batch sending advanced](examples/sending/batch_advanced_sending.py)
- [Batch sending using template](examples/sending/batch_sending_with_template.py)

### Sandbox (Email Testing) API
- [Attachments](examples/testing/attachments.py)
- [Inboxes](examples/testing/inboxes.py)
- [Messages](examples/testing/messages.py)
- [Projects](examples/testing/projects.py)

### Contacts API
- [Contacts](examples/contacts/contacts.py)
- [Contact Events](examples/contacts/contact_events.py)
- [Contact Exports](examples/contacts/contact_exports.py)
- [Contact Fields](examples/contacts/contact_fields.py)
- [Contact Imports](examples/contacts/contact_imports.py)
- [Contact Lists](examples/contacts/contact_lists.py)

### Email Templates API
- [Email Templates](examples/email_templates/templates.py)

### Suppressions API
- [Suppressions](examples/suppressions/suppressions.py)

### General API
- [Account Accesses](examples/general/account_accesses.py)
- [Accounts](examples/general/accounts.py)
- [Billing](examples/general/billing.py)
- [Permissions](examples/general/permissions.py)

## Supported functionality

This Python package offers integration with the [official API](https://api-docs.mailtrap.io/) for [Mailtrap](https://mailtrap.io).

Quickly integrate Mailtrap with your Python app.

Currently, with this SDK you can:
- Email API/SMTP
  - Send an email (Transactional and Bulk streams)
  - Send an email with a template (Transactional and Bulk streams)
  - Send a batch of emails (Transactional and Bulk streams)
  - Send a batch of emails with a template (Transactional and Bulk streams)
- Email Sandbox (Testing)
  - Send an email
  - Send an email with a template
  - Send a batch of emails
  - Send a batch of emails with a template
  - Messages management
  - Inboxes management
  - Projects management
  - Attachments management
- Contacts
  - Contacts management
  - Contact Lists management
  - Contact Fields management
  - Contact Events management
  - Contact Exports management
  - Contact Imports management
- Suppressions
  - Suppressions management (find and delete)
- Templates
  - Templates management
- General
  - Account access management
  - Permissions management
  - List accounts you have access to
  - Get current billing information

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
