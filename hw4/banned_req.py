# type: ignore
from google.cloud import pubsub_v1
from google.cloud import logging

client = logging.Client()
log_name = "requester_countries_logs"
client.setup_logging()
logger = client.logger(log_name)


def callback(message):
    logger.log_text(f"Received {message}.")
    print(f"Received {message}.")
    message.ack()


def create_subscription():
    subscriber_name = "banned_request_countries-sub"
    PROJECT_ID= "cloudcomputingcourse-398918"
    subscriber = pubsub_v1.SubscriberClient()

    subscription_path = subscriber.subscription_path(
            PROJECT_ID, subscriber_name
            )
    with subscriber:
        future = subscriber.subscribe(subscription_path, callback)
        try:
            future.result()
        except KeyboardInterrupt:
            future.cancel()


# https://cloud.google.com/python/docs/reference/pubsub/latest
def main():
    create_subscription()


main()
