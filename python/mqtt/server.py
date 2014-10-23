import mosquitto

client = mosquitto.Mosquitto("test", clean_session=True)
client.connect("127.0.0.1", 1883)

client.publish("test", "hello world", 1)

client.loop_forever()
