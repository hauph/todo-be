MESSAGE_RETENTION_PERIOD = 345600  # 4 days


def is_in_retention_period(created_at: int, remind_at: int):
    if created_at > remind_at:
        return True
    return remind_at - created_at <= MESSAGE_RETENTION_PERIOD
