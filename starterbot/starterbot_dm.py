import os
import time
from slackclient import SlackClient

class StarterBot_DM(object):

    def __init__(self, slack_client, BOT_ID):
        """
         Receives the mistakes (count how many donation command mistakes there are), the boolean
            attempting_to_donate, the boolean first_donate_message to check if the user in the 
            confirmation section of donation, the slack_client and the BOT_ID
        """
        self._mistakes = 0
        self._attempting_to_donate = False
        self._first_donate_message_occured = False
        #Slack client and BOT_ID (arguments)
        self._slack_client = slack_client
        self._BOT_ID = BOT_ID

    def get_slack_client(self) :
        """ 
            Returns the slack_client
        """
        return self._slack_client

    def handle_command(self, command, channel):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        if channel == 'D1SNMA747':
	        if command.startswith("#donate"):
	            # make sure it is a valid partner then set attempting_to_donate to true
	            response = "Would you like to #donate to XYZ, respond with yes or no"
	            self._attempting_to_donate = True
	            self._first_donate_message_occured = True
	        elif command.startswith("yes") and self._attempting_to_donate == True:
	            response = "Thanks for donating to XYZ"  
	            self._attempting_to_donate = False
	            self._first_donate_message_occured = False   
	        elif command.startswith("no") and self._attempting_to_donate == True:                 
	            response = "Canceling donation. Thank you for your time." 
	            self._attempting_to_donate = False
	            self._first_donate_message_occured = False          
	        elif self._mistakes == 2 and self._attempting_to_donate == True:              
	            response = "You have made too many mistakes. I'm cancelling the donation"    
	            self._mistakes = 0
	            self._attempting_to_donate = False
	            self._first_donate_message_occured = False                                
	        elif self._first_donate_message_occured == True and self._attempting_to_donate == True and (command.startswith("yes") == False 
	            or command.startswith("no") == False):
	            response = "Please respond with either yes to confirm the donation or no to cancel it."
	            self._mistakes = self._mistakes + 1
	        elif command.startswith("hello") or command.startswith("hi"):
	            response = "Hello. Nice to meet you!"
	        elif command.startswith("commands"):
	            response = "The available commands are \n*commands* : to list all the possible commands \n*#donate* : to start donating to your favorite charities\n      _ex: #donate to 'name of your charity' $20.00_ \n*hello*, *hi* : to say hi to the bot!"              
	        else :
	            response = "Not sure what you mean. Message starterbot by typing 'commands' to find all the available commands"
	            self._attempting_to_donate = False
	            self._first_donate_message_occured = False   
	        #posts message                
	        self._slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


    def parse_slack_output(self, slack_rtm_output):
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
                    return output['text'].split(self._BOT_ID)[1].strip().lower(), \
                           output['channel']

        return None, None

            
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 0.5 # 0.5 second delay between reading from firehose
    #arguments to the class
    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    BOT_ID = "<@" + os.environ.get("BOT_ID") + ">:"
    starter_bot = StarterBot_DM(slack_client, BOT_ID)
    if starter_bot.get_slack_client().rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = starter_bot.parse_slack_output(starter_bot.get_slack_client().rtm_read())
            if command and channel:
                starter_bot.handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)        
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
