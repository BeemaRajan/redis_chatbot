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
        Hi! I am RedisHelper. I'm here to support a variety of needs. Here are the commands I support:
        !help
        
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
        print(f"{fact}\n")
    
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
            print(f"Weather in {city}: {weather_data}")
        else:
            print(f"Weather data for {city} is not available. Try: nashville, new york, chicago, san francisco, miami, plovdiv")

    def identify(self):
        # Store user details in Redis
        username = input("Please enter a username: ")
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
            Name: {name}
            Age: {age}
            Gender: {gender}
            Location: {location}
        """)
    
    def join_channel(self, channel):
        # Join a channel
        self.pubsub.subscribe(channel)
        print(f"Listening to channel: {channel} (type '!quit' to exit)...")

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
        print(f"Sending messages to channel: {channel} (type '!quit' to exit)...")
        while True:
            message = input("Enter your message: ")
            
            if message.lower() == '!quit':
                print("Stopped sending messages.")
                break
                
            self.client.publish(channel, message)
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
        for message in messages:  # Note to self: possibly reverse the list?
            print(message)

    def direct_message(self):
        # Send a direct message to the chatbot
        print("Sending messages to me! (type '!quit' to exit) ...")
        while True:
            message = input("\nPlease enter your message: ")
            self.client.publish("chatbot:dm", message)
            print(f"[user]: {message}")

            print(f"[bot name]: While I would love to chat with you, I must get back to keeping track of everyone's usernames and messages!")
            break # added the while loop so if I wanted to expand on this feature

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
                print("Please specify a city. Usage: !weather <city>\n")

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
                print("Please specify a channel. Usage: !joinchannel <channel>\n")

        elif message.startswith("!sendmessage:"):
            parts = message.split(" ", 1)
            if len(parts) > 1:
                channel = parts[1]
                self.send_message(channel)
            else:
                print("Please specify a channel. Usage: !sendmessage <channel>\n")

        elif message.startswith("!leavechannel:"):
            parts = message.split(" ", 1)
            if len(parts) > 1:
                channel = parts[1]
                self.leave_channel(channel)
            else:
                print("Please specify a channel. Usage: !leavechannel <channel>\n")

        elif message.startswith("!readmessages:"):
            parts = message.split(" ", 1)
            if len(parts) > 1:
                channel = parts[1]
                self.read_messages(channel)
            else:
                print("Please specify a channel. Usage: !readmessages <channel>\n")

        elif message == "!directmessage":
            self.direct_message()

        else:
            print("Command not recognized. Use !help to see all commands.\n")

if __name__ == "__main__":
    bot = Chatbot()

    # Initialize weather data and fun facts
    bot.store_weather_data()
    bot.store_fun_facts()

    # Force user to set username and info upon opening
    print("\nBefore we begin, please enter your user info: \n")
    bot.identify()
    print("\nThank you for registering!\n")

    bot.introduce()

    ## Main interaction loop here
    while True:
        prompt = input("\nPlease enter a command (or '!quit' to exit): ")
        
        if prompt.lower() == '!quit':
            print("Goodbye!")
            break
        elif prompt.startswith("!"):
            bot.process_commands(prompt)
        else:
            print("Please enter a command. Use !help to see all commands.")