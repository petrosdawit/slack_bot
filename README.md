# slack_bot
first attempt at a slack bot using the python-slackclient

The only files that have my code are the staterbot.py and the print_bot_id.py which can be found in the starterbot folder. You only need to reference these 2 files if you understand how the python-slackclient works. I needed the rest of the files b/c this bot is being ran on the python-slackclient. If you want to review the python-slackclient, check out this https://github.com/slackhq/python-slackclient. 

This slack_bot can hold a conversation with a user through a channel or direct message on slack. Once the slack_bot is integrated into the channel and added into the team slack, it can be talked to by @starterbot: in a channel or through regular message (without atting it) in a dm

The commands it has so far are "donate(holds a small conversation with some follow up requests), commands which list out the commands, and hi, hello, hey and sup"

If the commands are not any of these, the bot will reply by saying it doesn't understand and will ask to clarify or type 'commands' to get a list of all the commands. Also, variations of the commands listed above don't work. Typing 'high' will not prompt the hello message for 'hi' but instead have the bot be confused and say its not sure of what you mean

The bot runs on a user's terminal and not on cloud performer like Heroku. There are tutorials online that make it easy to integrate. I know Heroku can offer a 24 hour cloud platform but it costs (I believe) 7 bucks a month. 


