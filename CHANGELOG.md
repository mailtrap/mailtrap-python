## [2.3.0] - 2025-10-24
* Fix issue #24: Add batch_send method to SendingApi, add models by @Ihor-Bilous in https://github.com/mailtrap/mailtrap-python/pull/47
* Fix issue #42: Add GeneralApi, related models, examples, tests. by @Ihor-Bilous in https://github.com/mailtrap/mailtrap-python/pull/48
* Fix issue #41: Add ContactExportsApi, related models, tests and examples by @Ihor-Bilous in https://github.com/mailtrap/mailtrap-python/pull/49
* Fix issue #45: Add ContactEventsApi, related models, tests and examples by @Ihor-Bilous in https://github.com/mailtrap/mailtrap-python/pull/51

## [2.2.0] - 2025-09-18
- Potential fix for code scanning alert no. 1: Workflow does not contain permissions by @mklocek in https://github.com/railsware/mailtrap-python/pull/15
- Fix issue #29. Add support of Emails Sandbox (Testing) API: Projects by @Ihor-Bilous in https://github.com/railsware/mailtrap-python/pull/31
- Issue 25 by @Ihor-Bilous in https://github.com/railsware/mailtrap-python/pull/33
- Fix issue #18: Add api for EmailTemplates, add tests and examples by @Ihor-Bilous in https://github.com/railsware/mailtrap-python/pull/34
- Fix issue #19: Add ContactFieldsApi, related models, tests, examples by @Ihor-Bilous in https://github.com/railsware/mailtrap-python/pull/35
- Fix issue #20: Add ContactListsApi, related models, tests, examples by @Ihor-Bilous in https://github.com/railsware/mailtrap-python/pull/36
- Fix issue #21: Add ContactsApi, related models, tests, examples by @Ihor-Bilous in https://github.com/railsware/mailtrap-python/pull/37
- Fix issue #22: Add ContactImportsApi, related models, tests, examples by @Ihor-Bilous in https://github.com/railsware/mailtrap-python/pull/38
- Fix issue #23: Add SuppressionsApi, related models, tests and examples by @Ihor-Bilous in https://github.com/railsware/mailtrap-python/pull/39
- Fix issue #27: Add InboxesApi, related models, tests, examples. by @Ihor-Bilous in https://github.com/railsware/mailtrap-python/pull/40
- Fix issue #26: Add MessagesApi, releated models, examples, tests by @Ihor-Bilous in https://github.com/railsware/mailtrap-python/pull/43
- Fix issue #28: Add AttachmentsApi, related models, tests, examples by @Ihor-Bilous in https://github.com/railsware/mailtrap-python/pull/44

## [2.1.0] - 2025-05-12
- Add sandbox mode support in MailtrapClient
  - It requires inbox_id parameter to be set
- Add bulk mode support in MailtrapClient
- Drop support python 3.6 - 3.8
- Add support for python 3.12 - 3.13

## [2.0.1] - 2023-05-18
- Add User-Agent header to all requests

## [2.0.0] - 2023-03-11

- Initial release of the official mailtrap.io API client.
- This release is a completely new library, incompatible with v1.
- Send mails using the new Mailtrap Sending API.

## [1.0.1] - 2020-10-03

- Renamed to [Sendria](https://github.com/msztolcman/sendria). An SMTP server that makes all received mails accessible via a web interface and REST API.
