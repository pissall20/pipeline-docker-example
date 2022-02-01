import imp
import json
import time
import random
import datetime
from kafka import KafkaProducer


SYMBOLS = ["APPL", "TSLA", "BTC", "GM", "SONY"]

# Mu, Sigma for prices to use in random.normalvariate()
mu, sigma = 200, 50


def main():
    # https://kafka-python.readthedocs.io/en/master/usage.html

    # write your logic here

    # Set the kafka bootstrap server and topic name
    server, topic = 'kafka:9092', 'prices'
    # Create the KafkaProducer object to send data to kafka
    producer = KafkaProducer(bootstrap_servers=[server], value_serializer=lambda m: json.dumps(m).encode('ascii'), retries=5)

    # Create 5000 random messages and send them to producer
    for _ in range(5000):
        # Create the json data with ts, symbol and price keys
        json_data = {
            'ts': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'symbol': random.choice(SYMBOLS),
            'price': round(random.normalvariate(mu, sigma), 2)
        }
        # Send the data to the producer
        producer.send(topic, json_data)
        
    print("Messages sent.")
    exit(0)


if __name__ == "__main__":
    main()
