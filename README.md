# CrabBot
A Discord bot to create a weekly [Crab.Fit](https://crab.fit) schedule. 

## Getting Started
- Run the /new-schedule command. If you'd like to customize the options, see below.
- When prompted for your regional timezone, hit "Search by Country" and type in your country.
- Select your current time.
- Select the most appropriate timezone.
- Done! CrabBot will send out a new schedule every week.
- If you'd like to generate a schedule for this week, run /this-week.

## Commands

### /new-schedule
Create a new schedule to send out every week.  
> [!NOTE]  
> After running, the command will prompt you for your time zone. You can follow the instructions to find your time zone, or you can enter it manually. To do so, press "Skip Search" and enter your REGIONAL time zone (e.g. "America/Los_Angeles", NOT "PST"). You can find your time zone on crab.fit.  
#### Parameters:
- ```channel```: A Discord text channel to post each week's crab.fit link to. Defaults to the channel the command is run in.
- ```role-to-ping```: A Discord role to ping with each week's post. Optional.
- ```schedule-name```: The name of your schedule. This is used to determine the title on each crab.fit as well as to identify the schedule if you want to delete it later. Defaults to the server name. However, if you plan on having multiple schedules, change the title to make it distinguishible from other schedules.
- ```daily-start-time```: The time at which each day begins (inclusive). This is a number from 0-23 which corresponds to the hour in 24-hour format. For example, if you want each day to start at 2 PM, the corresponding value should be 14. Defaults to 8 AM.
- ```daily-end-time```: The time at which each day ends (exclusive). This is a number from 0-24 which corresponds to the hour in 24-hour format, with 24 being end of day. For example, if you want each day to end at 10 PM, the corresponding value should be 22. Defaults to 24 (end of the day).
- ```start-of-week```: The weekday you want each crab.fit to start on. The schedule will be sent out at midnight the day before. Defaults to Monday, with links being sent out on Sunday at 0:00 (12:00 AM)

### /this-week
Creates a new schedule for the current week. Use this if you'd like to generate your schedule right after setting it up, or if last weeks crab.fit failed to create due to downtime or a bug.
> [!WARNING] 
> This will ALWAYS create a schedule starting from the PREVIOUS start of week. If it's currently the day in which the bot usually makes the schedule, but it failed, wait until the day AFTER to make the schedule. For example, if the bot fails to create a schedule on Sunday, wait until Monday to run this command, otherwise the schedule will go from the previous Monday to today (the current Sunday).

### /delete-schedule
Deletes a schedule. The bot will prompt you with a dropdown to select which schedule you would like to delete.
