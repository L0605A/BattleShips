from kafka import KafkaProducer, KafkaConsumer
import json

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

        self.player = None
        self.received_message = None

    def consume(self):
        print("consuming")
        try:
            print("try")
            msg_pack = self.consumer.poll(timeout_ms=1000)
            for tp, message in msg_pack.items():
                for msg in self.consumer:
                    print("in kafka")
                    self.player = msg.key
                    self.received_message = msg.value
                    print(f"Consumed message: key={msg.key}, value={msg.value}")
                    return

            print("Nothing recieved")
        except KeyboardInterrupt:
            print("catch")
            pass
        finally:
            self.consumer.close()


def kafkaSend(player, message):
    producer = MessageProducer()
    producer.send(topic, key=player, value=message)


def kafkaRecieve():
    print("Entered receiving")
    consumer = MessageConsumer(topic, group_id='test_group')
    print("Made consumer")
    consumer.consume()
    print("Consumed message")
    return {"Player": consumer.player, "Move": consumer.received_message}
