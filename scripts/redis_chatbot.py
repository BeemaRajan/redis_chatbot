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
        Hello! I'm RedisBot, and I'm here to make your messaging experience smoother. 
        I handle the behind-the-scenes magic: storing your messages, managing channels, and serving up interesting tidbits whenever you need them. 
        Here are the commands I support:
            !help: List of commands
            !fact: Random fun fact
            !weather <city>: Weather update
            !whoami: Your user information
            !updateinfo: Update your user information
            !joinchannel <channel>: Join a channel
            !sendmessage <channel>: Send a message to a channel
            !leavechannel <channel>: Leave a channel
            !readmessages <channel>: Read all messages from a channel
            !directmessage: Message the bot
        """
        print(intro)

    def store_fun_facts(self):
        # Save fun facts for special function
        self.client.sadd("random:facts", 
            "There are more chess positions than there are atoms in the observable universe.",
            "A single cloud can weigh more than a million pounds.",
            "Sharks have been around longer than trees - sharks evolved about 400 million years ago, while trees appeared around 350 million years ago.",
            "Bananas are berries, but strawberries are not!",
            "The shortest war in history was between Britain and Zanzibar in 1896 - it lasted only 38-45 minutes."
        )

    def get_random_fact(self):
        # Get a random fact
        fact = self.client.srandmember("random:facts")
        print(f"\n{fact.decode('utf-8')}")
    
    def store_weather_data(self):
        # Save weather data for cities
        weather_data = {
            "nashville": "Sunny, 72°F",
            "new york": "Cloudy, 68°F", 
            "chicago": "Rainy, 60°F",
            "san francisco": "Foggy, 65°F",
            "miami": "Hot and humid, 85°F",
            "plovdiv": "Partly Cloudy, 70°F"
        }
        for city, weather in weather_data.items():
            self.client.hset("weather", city, weather)

    def get_weather_data(self, city):
        # Get weather data for a particular city
        city = city.lower()
        weather_data = self.client.hget("weather", city)

        if weather_data:
            print(f"\tWeather in {city.title()}: {weather_data.decode('utf-8')}")
        else:
            print(f"\tWeather data for {city.title()} is not available. Try: nashville, new york, chicago, san francisco, miami, plovdiv")

    def identify(self):
        # Store user details in Redis
        username = input("\nPlease enter a username: ")
        age = input("Please enter your age: ")
        gender = input("Please enter your gender: ")
        location = input("Please enter your location: ")

        user_key = f"user:{username}"
        self.client.hset(user_key, mapping={
            "name": username,
            "age": age,
            "gender": gender,
            "location": location
        })
        self.username = username
        
    def who_am_i(self):
        # Get own user info
        user_key = f"user:{self.username}"
        name = self.client.hget(user_key, "name")
        age = self.client.hget(user_key, "age")
        gender = self.client.hget(user_key, "gender")
        location = self.client.hget(user_key, "location")
        print(f"""User data:
            Name: {name.decode('utf-8')}
            Age: {age.decode('utf-8')}
            Gender: {gender.decode('utf-8')}
            Location: {location.decode('utf-8')}
        """)
    
    def join_channel(self, channel):
        # Join a channel
        self.pubsub.subscribe(channel)

        while True:
            print(f"Listening to channel: {channel} ...")
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    print(f"[{channel}] {message['data'].decode('utf-8')}")

    def leave_channel(self, channel):
        # Leave a channel
        self.pubsub.unsubscribe(channel)
        print(f"Left channel: {channel}")

    def send_message(self, channel):
        # Send a message
        print(f"\nSending messages to channel: {channel} (type '!quit' to exit)...")
        while True:
            message = input("\nEnter your message: ")
            formatted_message = f"[{self.username}] - {message}"
            
            if message.lower() == '!quit':
                print("\nStopped sending messages.")
                break
                
            self.client.publish(channel, formatted_message)
            self.save_message(channel, self.username, message)
            print("Message sent!")

    def save_message(self, channel, username, message):
        # Save message to Redis for reading
        username = username
        formatted_message = f"[{username}]: {message}"  
        
        message_key = f"messages:{channel}"
        self.client.lpush(message_key, formatted_message)
        

    def read_messages(self, channel):
        # Read messages from a channel
        message_key = f"messages:{channel}"
        messages = self.client.lrange(message_key, 0, -1)

        if not messages:
            print(f"No messages in channel: {channel}")
            return

        print(f"\n--- Messages from {channel} ---")
        for message in messages:
            print(message.decode('utf-8'))

    def direct_message(self):
        # Send a direct message to the chatbot
        print("\nSending messages to me! (type '!quit' to exit) ...")
        while True:
            message = input("\nPlease enter your message: ")
            self.client.publish("chatbot:dm", message)
            print(f"\n[{self.username}]: {message}")

            print(f"[Redisbot]: While I would love to chat with you, I must get back to keeping track of everyone's usernames and messages!")
            break # added the while loop in case I wanted to expand on this feature

    def process_commands(self, message):
        # Handle special chatbot commands
        message = message.lower()

        if message == "!help":
            print("""
            Here is a list of commands this bot supports:
                !help: List of commands
                !fact: Random fun fact
                !weather <city>: Weather update
                !whoami: Your user information
                !updateinfo: Update your user information
                !joinchannel <channel>: Join a channel
                !sendmessage <channel>: Send a message to a channel
                !leavechannel <channel>: Leave a channel
                !readmessages <channel>: Read all messages from a channel
                !directmessage: Message the bot
            """)

        elif message == "!fact":
            self.get_random_fact()

        elif message.startswith("!weather"):
            parts = message.split(" ", 1)
            if len(parts) > 1:
                city = parts[1]
                self.get_weather_data(city)
            else:
                print("\nPlease specify a city. Usage: !weather <city>\n")

        elif message == "!whoami":
            self.who_am_i()

        elif message == "!updateinfo":
            self.identify()

        elif message.startswith("!joinchannel"):
            parts = message.split(" ", 1)
            if len(parts) > 1:
                channel = parts[1]
                self.join_channel(channel)
            else:
                print("\nPlease specify a channel. Usage: !joinchannel <channel>")

        elif message.startswith("!sendmessage"):
            parts = message.split(" ", 1)
            if len(parts) > 1:
                channel = parts[1]
                self.send_message(channel)
            else:
                print("\nPlease specify a channel. Usage: !sendmessage <channel>")

        elif message.startswith("!leavechannel"):
            parts = message.split(" ", 1)
            if len(parts) > 1:
                channel = parts[1]
                self.leave_channel(channel)
            else:
                print("\nPlease specify a channel. Usage: !leavechannel <channel>")

        elif message.startswith("!readmessages"):
            parts = message.split(" ", 1)
            if len(parts) > 1:
                channel = parts[1]
                self.read_messages(channel)
            else:
                print("\nPlease specify a channel. Usage: !readmessages <channel>")

        elif message == "!directmessage":
            self.direct_message()

        else:
            print("\nCommand not recognized. Use !help to see all commands.")

if __name__ == "__main__":
    bot = Chatbot()

    # Initialize weather data and fun facts
    bot.store_weather_data()
    bot.store_fun_facts()

    # Force user to set username and info upon opening
    print("\nBefore we begin, please enter your user info: ")
    bot.identify()
    print("\nThank you for registering!")

    bot.introduce()

    ## Main interaction loop here
    while True:
        prompt = input("\nPlease enter a command (or '!quit' to exit): ")
        
        if prompt.lower() == '!quit':
            print("\nGoodbye!\n")
            break
        elif prompt.startswith("!"):
            bot.process_commands(prompt)
        else:
            print("\nPlease enter a command. Use !help to see all commands.")