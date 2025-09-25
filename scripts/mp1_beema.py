import redis
import json
import random

class Chatbot:
    def __init__(self, host='redis', port=6379):
        self.client = redis.StrictRedis(host=host, port=port)
        self.pubsub = self.client.pubsub()
        self.username = None

    def introduce(self):
        # Provide an introduction and list of commands
        intro = """
        Hi! I am RedisHelper. I'm here to support a variety of needs.
        Here are the commands this bot supports:
        !help: List of commands
        !weather <city>: Weather update
        !fact: Random fun fact
        !whoami: Your user information
        and anything else you enabled your bot to do
        """
        print(intro)

    def identify(self, username, age, gender, location):
        # Store user details in Redis
        # set userNames 'username'
        pass

    def join_channel(self, channel):
        # Join a channel
        pass

    def leave_channel(self, channel):
        # Leave a channel
        pass

    def send_message(self, channel, message):
        # Send a message to a channel
        pass

    def read_message(self, channel):
        # Read messages from a channel
        pass

    def process_commands(self, message):
        # Handle special chatbot commands
        pass

    def direct_message(self, message):
        # Send a direct message to the chatbot
        pass

if __name__ == "__main__":
    bot = Chatbot()
    bot.introduce()
    # Main interaction loop here
