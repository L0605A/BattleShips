from kafka import KafkaProducer, KafkaConsumer
import json

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

class MessageConsumer:
    def __init__(self, topic, group_id, servers='localhost:9092'):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=servers,
            group_id=group_id,
            auto_offset_reset='earliest',
            key_deserializer=lambda k: k.decode('utf-8'),
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )

    def consume(self):
        try:
            for msg in self.consumer:
                print(f"Consumed message: key={msg.key}, value={msg.value}")
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

if __name__ == "__main__":
    topic = 'my-topic'

    producer = MessageProducer()
    producer.send(topic, key='key1', value='DEBUG DEBUG DEBUG')


    consumer = MessageConsumer(topic, group_id='test_group')
    consumer.consume()