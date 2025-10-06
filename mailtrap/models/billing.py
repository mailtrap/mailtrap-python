from datetime import datetime

from pydantic.dataclasses import dataclass


@dataclass
class MessagesCount:
    current: int
    limit: int


@dataclass
class UsageTesting:
    sent_messages_count: MessagesCount
    forwarded_messages_count: MessagesCount


@dataclass
class UsageSending:
    sent_messages_count: MessagesCount


@dataclass
class Plan:
    name: str


@dataclass
class Testing:
    plan: Plan
    usage: UsageTesting


@dataclass
class Sending:
    plan: Plan
    usage: UsageSending


@dataclass
class Billing:
    cycle_start: datetime
    cycle_end: datetime


@dataclass
class BillingCycleUsage:
    billing: Billing
    testing: Testing
    sending: Sending
