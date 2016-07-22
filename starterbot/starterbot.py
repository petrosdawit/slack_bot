import os
import time
from slackclient import SlackClient

""" 
    StarterBot Class. It will account for the responses and be the main class 
    Use this link to find api methods https://api.slack.com/methods
    ex of api call: self._slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)  
"""

class StarterBot(object):

    def __init__(self, slack_client, BOT_ID):
        """
         Receives the mistakes (count how many donation command mistakes there are), the boolean
            attempting_to_donate, the boolean first_donate_message to check if the user in the 
            confirmation section of donation, the slack_client and the BOT_ID
        """
        #self._mistakes counts how many mistakes someone makes during the #donate process.
        self._mistakes = 0
        # self._attempting_to_donate will be set to True when the person is having a convo with the bot and is the donate command process
        self._attempting_to_donate = False
        #self._first_donate_message_occured will be set to True after the person had the 'would you like to donate to ...' pop up
        self._first_donate_message_occured = False
        self._response = ""
        self._old_response = None
        self._channel = None
        self._old_command = None
        self._command = None
        self._bot_responses = ["would you like to #donate to xyz, respond with yes or no", "thanks for donating to xyz",
         "canceling donation. thank you for your time.", "you have made too many mistakes. i'm cancelling the donation",
         "please respond with either yes to confirm the donation or no to cancel it.", "hello. nice to meet you!",
         "the available commands are \n*commands* : to list all the possible commands \n*#donate* : to start donating to your favorite charities\n      _ex: #donate to 'name of your charity' $20.00_ \n*hello*, *hi*, *hey*, *sup* : to say hi to the bot!",
         "not sure what you mean. message starterbot by typing 'commands' to find all the available commands"]
        #Slack client and BOT_ID (arguments)
        self._slack_client = slack_client
        self._BOT_ID = BOT_ID

    """ 
        Setters and getters for the slack_client, channel, command and old_command(previous command said to the starterbot)
    """    

    def get_slack_client(self):
        return self._slack_client

    def get_channel(self):
        return self._channel

    def set_channel(self, channel):
        self._channel = channel 

    def set_command(self, command):
        self._command = command

    def get_command(self):
        return self._command                        

    def set_old_command(self, old_command):
        self._old_command = old_command

    def get_old_command(self):
        return self._old_command

    def handle_command(self, command, channel):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        if command.startswith("#donate"):
            # make sure it is a valid partner then set attempting_to_donate to true
            self._response = "Would you like to #donate to XYZ, respond with yes or no"
            self._attempting_to_donate = True
            self._first_donate_message_occured = True
        elif command[:3].startswith("yes") and self._attempting_to_donate == True:
            self._response = "Thanks for donating to XYZ"  
            self._attempting_to_donate = False
            self._first_donate_message_occured = False   
        elif command[:2].startswith("no") and self._attempting_to_donate == True:                 
            self._response = "Canceling donation. Thank you for your time." 
            self._attempting_to_donate = False
            self._first_donate_message_occured = False          
        elif self._mistakes == 2 and self._attempting_to_donate == True:              
            self._response = "You have made too many mistakes. I'm cancelling the donation"    
            self._mistakes = 0
            self._attempting_to_donate = False
            self._first_donate_message_occured = False                                
        elif self._first_donate_message_occured == True and self._attempting_to_donate == True and (command[:3].startswith("yes") == False 
            or command[:2].startswith("no") == False):
            self._response = "Please respond with either yes to confirm the donation or no to cancel it."
            self._mistakes = self._mistakes + 1
        elif command[:2].startswith("hi") and command[:3].strip() == command[:2]:
            self._response = "Hello. Nice to meet you!"
        elif command[:5].startswith("hello") and command[:6].strip() == command[:5]:
            self._response = "Hello. Nice to meet you!"
        elif command[:3].startswith("hey") and command[:4].strip() == command[:3]:
            self._response = "Hello. Nice to meet you!"
        elif command[:3].startswith("sup") and command[:4].strip() == command[:3]:
            self._response = "sup..."                                             
        elif command[:7].startswith("commands") and command[:8].strip() == command[:7]:
            self._response = "The available commands are \n*commands* : to list all the possible commands \n*#donate* : to start donating to your favorite charities\n      _ex: #donate to 'name of your charity' $20.00_ \n*hello*, *hi*, *hey*, *sup* : to say hi to the bot!"                
        else :
            self._response = "Not sure what you mean. Message starterbot by typing 'commands' to find all the available commands"
            self._attempting_to_donate = False
            self._first_donate_message_occured = False   
        #posts message               
        self._slack_client.api_call("chat.postMessage", channel=channel, text=self._response, as_user=True)

    def get_channel_from_rtm(self, slack_rtm_output):
        """
            Retrieves the channel through slack_client_rtm_read() which is passed in as an argument
            returns the channel if text is in the output and assigns self._channel to that channel
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output:
                    self._channel = output['channel']
                    return self._channel
        return None

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
                    return output['text'].split(self._BOT_ID)[1].strip().lower()
        return None

    def sending_direct_messages(self, slack_rtm_output):
        """
            Similar to sending_message_in_channels method. however, it doesn't check if self._BOT_ID in output['text']
            so it will fall into a loop as it will keep reading the same line and responding over and over again.
            In order to bypass this, we have a self._old_command variable that will keep track of the previous command
            and will return None, if our prev command and our current command are the same. However, we need a second check b/c
            with only if self._command != self._old_command:, the response will be repeated twice. for ex: user says 'hi'. the current
            command is 'hi' and the prev command is none. so the bot replies. now the new command is 'the reply' and the prev command is 'hi'
            the slack_client will read the starterbot's responses as well. in order to fix this, there is a second check where we check
            if the new command is any of standard bot responses and if it is, we set the new command and the old command to a same long string
            (highly unlikely someone will ever write that string) so that it won't repeat itself twice. If someone were to dm the bot the long
            string, the bot won't respond (but who will ever do that).
        """
        output_list = slack_rtm_output
        for output in output_list:
            if output and 'text' in output:
                self._command = output['text'].strip().lower()
                for x in self._bot_responses:
                    if self._command == x:
                        self._command = 'shshkdkjsfodshfhsdlfhlsdkfjsldfhlsdkhflksdhddhfsdfhsdldlfsdhfhsdljhkllkallll2828282282828f'
                        self._old_command = 'shshkdkjsfodshfhsdlfhlsdkfjsldfhlsdkhflksdhddhfsdfhsdldlfsdhfhsdljhkllkallll2828282282828f'
                if self._command != self._old_command:
                    self._old_command = self._command
                    self._command = self._old_command
                    return self._command
        return None


            
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 0.5 # 0.5 second delay between reading from firehose
    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    BOT_ID = "<@" + os.environ.get("BOT_ID") + ">:"
    starter_bot = StarterBot(slack_client, BOT_ID)
    if starter_bot.get_slack_client().rtm_connect():
        print("StarterBot connected and running!")
        while True:
            output_list = starter_bot.get_slack_client().rtm_read()
            starter_bot.set_channel(starter_bot.get_channel_from_rtm(output_list))
            channel = starter_bot.get_channel()
            command = starter_bot.get_command()
            if channel != None:
                #dm channel ids start with 'D', so if the channel starts with D, then its a dm. we use the sending_direct_messages(output_list)
                #for that instead. channel messages start with 'C'.
                if channel.startswith('D'):
                    command = starter_bot.sending_direct_messages(output_list)
                else: 
                    command = starter_bot.sending_message_in_channels(output_list)
            if command and channel:
                starter_bot.handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)   
    else:
        print("Connection failed. Invalid Slack token or bot ID?")





