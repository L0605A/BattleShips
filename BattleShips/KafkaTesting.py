from kafka import KafkaProducer, KafkaConsumer
import json
import threading  # Import threading module

topic = 'game'


class MessageProducer:
    def __init__(self, servers='localhost:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=servers,
            key_serializer=lambda k: k.encode('utf-8'),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send(self, topic, key, value):
        self.producer.send(topic, key=key, value=value)
        self.producer.flush()


class MessageConsumer(threading.Thread):  # Subclass threading.Thread

    player = None
    received_message = None

    def __init__(self, topic, group_id, servers='localhost:9092'):
        super().__init__()  # Initialize the thread
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=servers,
            group_id=group_id,
            auto_offset_reset='earliest',
            key_deserializer=lambda k: k.decode('utf-8'),
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
        #self.player = None
        #self.received_message = None
        self.stop_event = threading.Event()  # Event to signal stop

    def run(self):

        print("Consumer thread started")

        while not self.stop_event.is_set():
            try:
                while not self.stop_event.is_set():
                    msg_pack = self.consumer.poll(timeout_ms=1000)
                    for tp, msg in msg_pack.items():
                        #print(tp)
                        msg = msg[0]
                        #print(msg)

                        MessageConsumer.player = msg.key
                        MessageConsumer.received_message = msg.value

                        #print(self.player)
                        #print(MessageConsumer.player)
                        #print(f"Consumed message: key={msg.key}, value={msg.value}")
                    self.consumer.commit()  # Commit offsets if needed
            except Exception as e:
                print(f"Exception in consumer thread: {e}")
            finally:
                #self.consumer.close()
                print("Consumer thread stopped")

    def stop(self):
        self.stop_event.set()  # Set the event to stop the consumer


def kafkaSend(player, message):
    producer = MessageProducer()
    producer.send(topic, key=player, value=message)


def kafkaReceive():
    #print("Entered receiving")
    consumer = MessageConsumer(topic, group_id='test_group')
    consumer.start()  # Start the consumer thread
    # Optionally, you can wait for the thread to finish or continue doing other work
    # consumer.join()  # Uncomment if you want to wait for consumer thread to finish
    return consumer


# Example usage:
# Do other work here while consumer is running in the background
# consumer_thread.join()  # Optionally wait for consumer thread to finish

# To stop the consumer thread at some point:
# consumer_thread.stop()
