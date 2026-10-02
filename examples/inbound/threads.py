import os

import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.inbound import InboundThread
from mailtrap.models.inbound import InboundThreadsListResponse

API_KEY = os.environ["MAILTRAP_API_KEY"]
INBOX_ID = int(os.environ["MAILTRAP_INBOUND_INBOX_ID"])

client = mt.MailtrapClient(token=API_KEY)
threads_api = client.inbound_api.threads


def list_threads(inbox_id: int) -> InboundThreadsListResponse:
    # Pass last_id from the previous page to paginate.
    return threads_api.get_list(inbox_id)


def search_threads(inbox_id: int, search: str) -> InboundThreadsListResponse:
    return threads_api.get_list(inbox_id, search=search)


def get_thread(inbox_id: int, thread_id: str) -> InboundThread:
    return threads_api.get_by_id(inbox_id, thread_id)


def delete_thread(inbox_id: int, thread_id: str) -> DeletedObject:
    return threads_api.delete(inbox_id, thread_id)


if __name__ == "__main__":
    page = list_threads(INBOX_ID)
    print(f"{len(page.data)} of {page.total_count} threads")
    print(search_threads(INBOX_ID, "invoice"))

    if page.data:
        thread_id = page.data[0].id
        print(get_thread(INBOX_ID, thread_id))
        print(delete_thread(INBOX_ID, thread_id))
