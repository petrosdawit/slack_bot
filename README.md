# slack_bot
first attempt at a slack bot using the python-slackclient

The only files that have my code is the donate_bot.py which can be found in the donate_bot folder. You only need to reference this file if you understand how the python-slackclient works. I needed the rest of the files b/c this bot is being ran on the python-slackclient. If you want to review the python-slackclient, check out this https://github.com/slackhq/python-slackclient. 

In my code, I export the slack_bot_token and bot_user id. You will have to extract that info from slack when you first create the bot. Once a bot is created, you can get its BOT_ID by running the tester users.list method from api.slack.com. Make sure to copy those values and type in your terminal, export SLACK_BOT_TOKEN='(slack bot token)' and type export BOT_ID='(your bot id)'. Also, you need to run source donate_bot/bin/activate in bash to get the donate_bot activated. Once you have this set up, all you need to do is integrate the bot into your slack team and channels and then run the donate_bot.py in the donate_bot folder in your terminal.

This slack_bot can hold a conversation with a user through a channel or direct message on slack. Once the slack_bot is integrated into the channel and added into the team slack, it can be talked to by (depends on what name you call it, I called it donate_bot) @donate_bot: in a channel or through regular message (without atting it) in a dm. In the slack_bot example, the slack_bot only responds back with text. The slack_bot is capable of integration but that will have to be done through your end if you want to use it. Currently the commands the bot has so far are "donate(holds a small conversation with some follow up requests), commands which list out the commands, and hi, hello, hey and sup"

If the commands are not any of these, the bot will reply by saying it doesn't understand and will ask to clarify or type 'commands' to get a list of all the commands. Also, variations of the commands listed above don't work. Typing 'high' will not prompt the hello message for 'hi' but instead have the bot be confused and say its not sure of what you mean

The bot runs on a user's terminal and not on cloud performer like Heroku. There are tutorials online that make it easy to integrate. I know Heroku can offer a 24 hour cloud platform but it costs (I believe) 7 bucks a month. 


