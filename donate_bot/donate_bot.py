import os
import time
from slackclient import SlackClient

import re

""" 
    DonateBot Class. It will account for the responses and be the main class 
    Use this link to find api methods https://api.slack.com/methods
    ex of api call for sending message: self._slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)  
"""

class DonateBot(object):

    def __init__(self, slack_client, BOT_ID):
        """
            There will be dictionaries for mistakes (count how many donation command mistakes there are), the boolean
            attempting_to_donate, the boolean first_donate_message to check if the user in the 
            confirmation section of donation, the last 2 responses and commands, the org the user last donated to
            and the dollar amount, the potential bot responses back. 

            The user, channel slack_client and the BOT_ID. The slack_client and the BOT_ID won't 
            change but the user will constantly be changing the dictionaries will keep track of the info for each
            user. The last instance variable will be the self._test_non_profits which will be where you keep the non 
            profits that can be donated to. For now, there are only 5 who can be donated to.
        """

        #self._mistakes counts how many mistakes someone makes during the donate process.
        self._mistakes = {}
        #self._attempting_to_donate will be set to True when the person is having a convo with the bot and is the donate command process
        self._attempting_to_donate = {}
        #self._first_donate_message_occured will be set to True after the person had the 'would you like to donate to ...' pop up
        self._first_donate_message_occured = {}

        self._response = {}
        self._old_response = {}
        self._old_command = {}
        self._command = {}

        self._org = {}
        self._dollar_amount = {}
        self._name = {}

        #self._bot_responses is dictonary where the values will be arrays containing all the possible responses the bot can say lowercased for each user
        self._bot_responses = {}
        #5 test non profits that can be donated to
        self._test_non_profits = ["UNICEF", "Red Cross", "Beagle Freedom Project", "Oxfam", "Save The Children"]        


        #Slack client and BOT_ID (arguments)
        self._slack_client = slack_client
        self._BOT_ID = BOT_ID
        #user and channel which are currently set to None when you start this class
        self._user = None
        self._channel = None 
        #users will be an array keeping track of each of the ids in the team
        self._users = []       

    """ 
        Setters and getters for the slack_client, channel, command and old_command(previous command said to the donatebot)
    """    

    def get_slack_client(self):
        return self._slack_client

    def get_channel(self):
        return self._channel

    def set_channel(self, channel):
        self._channel = channel 

    def get_self_users(self):
        return self._users

    def get_users(self):
        #calls the slack_client's api call to list out info of the users. You can get the names of the users
        users_list = self._slack_client.api_call("users.list")
        for x in users_list["members"]:
            #get ids of users
            self._users.append(x["id"])
            self._name[x["id"]] = x["name"]
        for user in self._users:
            #create initial holders for the user's information that needs to be recorded
            self._mistakes[user] = 0
            self._attempting_to_donate[user] = False
            self._first_donate_message_occured[user] = False
            self._response[user] = ""
            self._old_response[user] = None
            self._old_command[user] = ""
            self._command[user] = ""
            self._org[user] = ""
            self._dollar_amount[user] = ""   
            self._bot_responses[user] = ["would you like to donate $" + self._dollar_amount[user].lower() + " to " + self._org[user].lower() + ", respond with yes or no", "thanks for donating to " + self._org[user].lower(),
            "canceling donation. thank you for your time.", "you have made too many mistakes. i'm cancelling the donation",
            "please respond with either yes to confirm the donation or no to cancel it.", "sup...", "hello. nice to meet you!",
            "the available commands are \n*commands* : to list all the possible commands \n*donate* : to start donating to your favorite charities\n      _ex: donate to " + 
            "'name of your charity' $20.00_ \n*hello*, *hi*, *hey*, *sup* : to say hi to the bot!", "not sure what you mean. message donatebot by typing 'commands' " + 
            "to find all the available commands", "please make sure to include a dollar amount (ex: 25 = $25.00) and a partnered organization (ex: unicef) to make " + 
            "the donation"]

    def updateUsers(self):
        users_list = self._slack_client.api_call("users.list")  
        for x in users_list["members"]:
            if x["id"] not in self._users:
                self._users.append(x["id"])
                self._mistakes[x["id"]] = 0
                self._attempting_to_donate[x["id"]] = False
                self._first_donate_message_occured[x["id"]] = False
                self._response[x["id"]] = ""
                self._old_response[x["id"]] = None
                self._old_command[x["id"]] = ""
                self._command[x["id"]] = ""
                self._org[x["id"]] = ""
                self._name[x["id"]] = x["name"]
                self._dollar_amount[x["id"]] = ""   
                self._bot_responses[x["id"]] = ["would you like to donate $" + self._dollar_amount[x["id"]].lower() + " to " + self._org[x["id"]].lower() + ", respond with yes or no", "thanks for donating to " + self._org[x["id"]].lower(),
                "canceling donation. thank you for your time.", "you have made too many mistakes. i'm cancelling the donation",
                "please respond with either yes to confirm the donation or no to cancel it.", "sup...", "hello. nice to meet you!",
                "the available commands are \n*commands* : to list all the possible commands \n*donate* : to start donating to your favorite charities\n      _ex: donate to " + 
                "'name of your charity' $20.00_ \n*hello*, *hi*, *hey*, *sup* : to say hi to the bot!", "not sure what you mean. message donate by typing 'commands' " + 
                "to find all the available commands", "please make sure to include a dollar amount (ex: 25 = $25.00) and a partnered organization (ex: unicef) to make " + 
                "the donation"]                                     

    def handle_command(self, command, channel, user):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.

            Some of if statements will look this: if command[:3].startswith("yes"): ... 
            This is because, after the whitespace in the string has been removed via strip(), the client will
            check the first characters in the string. If we didn't have the command[:3] but just command,
            someone could have the command start with yesa, and the bot will respond accordingly which we 
            don't want. The number in command[:'number'].startswith(...) should be the same length as the word
            you are looking for in the beginning.

            You don't always have to look for the word to begin in the sentence. I only do this for commands, but you can 
            check if the substring you want is in the command string through a simple if x.lower() in command.lower():
            make sure to lower(), that way it is more user friendly and users don't need to have exact capitalization, ex:
            unicef vs UNICEF
        """

        #Handles the donate command
        if command.startswith("donate"):
            # make sure it is a valid partner then set attempting_to_donate to true
            #first parse through and find floats. returns empty array if no float
            numbers = re.findall(r'[-+]?\d*\.\d+|\d+', command)
            if numbers != []:
                for org in self._test_non_profits:
                    #set first float to the dollar amount the user wants to donate
                    self._dollar_amount[user] = numbers[0]
                    if org.lower() in command.lower():
                        self._org[user] = org
                        self._response[user] = "Would you like to donate $" + self._dollar_amount[user] + " to " + self._org[user] + ", respond with yes or no"
                        self._bot_responses[user][0] = "would you like to donate $" + self._dollar_amount[user] + " to " + self._org[user].lower() + ", respond with yes or no"
                        self._attempting_to_donate[user] = True
                        self._first_donate_message_occured[user] = True 
                        break
                    else:
                        self._response[user] = "Please make sure to include a dollar amount (ex: 25 = $25.00) and a partnered organization (ex: UNICEF) to make the donation"
            else:
                self._response[user] = "Please make sure to include a dollar amount (ex: 25 = $25.00) and a partnered organization (ex: UNICEF) to make the donation"
        elif command[:3].startswith("yes") and self._attempting_to_donate[user] == True:
            self._response[user] = "Thanks for donating to " + self._org[user]  
            self._bot_responses[user][1] = "thanks for donating to " + self._org[user].lower()  
            self._attempting_to_donate[user] = False
            self._first_donate_message_occured[user] = False
            self._org[user] = "" 
            self._mistakes[user] = 0                
        elif command[:2].startswith("no") and self._attempting_to_donate[user] == True:                 
            self._response[user] = "Canceling donation. Thank you for your time." 
            self._attempting_to_donate[user] = False
            self._first_donate_message_occured[user] = False
            self._org[user] = "" 
            self._mistakes[user] = 0           
        elif self._mistakes[user] == 2 and self._attempting_to_donate[user] == True:              
            self._response[user] = "You have made too many mistakes. I'm cancelling the donation"    
            self._mistakes[user] = 0
            self._attempting_to_donate[user] = False
            self._first_donate_message_occured[user] = False
            self._org[user] = ""                                
        elif self._first_donate_message_occured[user] == True and self._attempting_to_donate[user] == True and (command[:3].startswith("yes") == False 
            or command[:2].startswith("no") == False):
            self._response[user] = "Please respond with either yes to confirm the donation or no to cancel it."
            self._mistakes[user] = self._mistakes[user] + 1



        #The rest of the commands
        elif command[:2].startswith("hi") and command[:3].strip() == command[:2]:
            self._response[user] = "Hello. Nice to meet you!"
        elif command[:5].startswith("hello") and command[:6].strip() == command[:5]:
            self._response[user] = "Hello. Nice to meet you!"
        elif command[:3].startswith("hey") and command[:4].strip() == command[:3]:
            self._response[user] = "Hello. Nice to meet you!"
        elif command[:3].startswith("sup") and command[:4].strip() == command[:3]:
            self._response[user] = "sup..."                                             
        elif command[:8].startswith("commands") and command[:9].strip() == command[:8]:
            self._response[user] = "The available commands are \n*commands* : to list all the possible commands \n*donate* : to start donating to your favorite charities\n      _ex: donate to 'name of your charity' $20.00_ \n*hello*, *hi*, *hey*, *sup* : to say hi to the bot!"                
        else :
            self._response[user] = "Not sure what you mean. Message donatebot by typing 'commands' to find all the available commands"
            self._attempting_to_donate[user] = False
            self._first_donate_message_occured[user] = False   

        #posts message 
        if user != os.environ.get("BOT_ID"): 
            if channel.startswith("D"):            
                self._slack_client.api_call("chat.postMessage", channel=channel, text=self._response[user], as_user=True)
            else:
                self._response[user] = "<@" + self._name[user] + ">: " + self._response[user]
                self._slack_client.api_call("chat.postMessage", channel=channel, text=self._response[user], as_user=True)                    

    def get_channel_user_from_rtm(self, slack_rtm_output):
        """
            Retrieves the channel through slack_client_rtm_read() which is passed in as an argument
            returns the channel if text is in the output and assigns self._channel to that channel
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output:
                    self._channel = output['channel']
                    self._user = output['user']
                    return self._channel, self._user
        return None, None

    def sending_message_in_channels(self, slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and self._BOT_ID in output['text']:
                    # return text after the @ mention, whitespace removed
                    self._user = output['user']
                    return output['text'].split(self._BOT_ID)[1].strip().lower()
        return None

    def sending_direct_messages(self, slack_rtm_output, user):
        """
            Similar to sending_message_in_channels method. however, it doesn't check if self._BOT_ID in output['text']
            so it will fall into a loop as it will keep reading the same line and responding over and over again.
            In order to bypass this, we have a self._old_command variable that will keep track of the previous command
            and will return None, if our prev command and our current command are the same. However, we need a second check b/c
            with only if self._command != self._old_command:, the response will be repeated twice. for ex: user says 'hi'. the current
            command is 'hi' and the prev command is none. so the bot replies. now the new command is 'the reply' and the prev command is 'hi'
            the slack_client will read the donatebot's responses as well. in order to fix this, there is a second check where we check
            if the new command is any of standard bot responses and if it is, we set the new command and the old command to None
        """
        output_list = slack_rtm_output
        for output in output_list:
            if output and 'text' in output:
                self._command[user] = output['text'].strip().lower()
                for x in self._bot_responses[user]:
                    if self._command[user] == x:
                        self._command[user] = None
                        self._old_command[user] = None
                return self._command[user]
        return None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 0.25 # 0.25 second delay between reading from firehose
    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    BOT_ID = "<@" + os.environ.get("BOT_ID") + ">:"
    #donate_bot
    donate_bot = DonateBot(slack_client, BOT_ID)
    if donate_bot.get_slack_client().rtm_connect():
        donate_bot.get_users()
        count = 0
        print("DonateBot connected and running!")
        while True:
            output_list = donate_bot.get_slack_client().rtm_read()
            channel, user = donate_bot.get_channel_user_from_rtm(output_list)
            donate_bot.set_channel(channel)
            command = None
            if channel != None and user != None and user in donate_bot.get_self_users():
                #dm channel ids start with 'D', so if the channel starts with D, then its a dm. we use the sending_direct_messages(output_list)
                #for that instead. channel messages start with 'C'.
                if channel.startswith('D'):
                    command = donate_bot.sending_direct_messages(output_list, user)
                else: 
                    command = donate_bot.sending_message_in_channels(output_list)
            if command and channel:
                donate_bot.handle_command(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
            #update users every 100/4 = 25s. 4 because the READ_WEBSOCKET_DELAY is 0.25s so 4 to make 1 second    
            if count % 100 == 0:
                donate_bot.updateUsers()
            count += 1
            #reset the counter
            if count == 1000:
                count = 0
    else:
        print("Connection failed. Invalid Slack token or bot ID?")





