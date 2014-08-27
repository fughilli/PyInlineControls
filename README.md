![SampleImage](https://raw.githubusercontent.com/fughilli/PyInlineControls/master/inlineMicImage.png)

You will need to install PyAudio from here: http://people.csail.mit.edu/hubert/pyaudio/ and pywin32 from here: http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/

***Get the 32 bit binaries if you are not absolutely certain that you need 64 bit ones. I have a 64 bit machine but the 64 bit binaries wouldn't work with my 32 bit python installation.***

To set up this project manually, you have to create a task with the Task Scheduler. 
```
To do this, go to the start menu/screen and type "Schedule tasks"; select "Schedule tasks".

On the right side of the resulting window, select "Create Task..."
	Give it a sensible name, such as "Python inline controls"
	Give it a sensible description
	Select "Run with highest privileges"
	
	Jump to the "Triggers" tab.
	Select "New..."
		Select "At log on" from the dropdown
		Select "OK"

	Jump to the "Actions" tab.
	Select "New..."
		Select "Start a program..." from the dropdown
		Enter "wscript.exe" in the program box
		Copy and paste this into the arguments box: ".\invisible.vbs .\inline_control_watchdog.bat"
		Enter the directory containing this text file (the directory into which you cloned the git project) into the "Start in (optional)" box
	
	Jump to the "Conditions" tab.
		Uncheck "Start the task only if the computer is on AC power". This allows the script to run when you're on battery, too.
```

Hit "OK" on everything, and you're all set!

Optionally, go to the Settings tab under the Task Properties window and check these:
```
Allow task to be run on demand
Run task as soon as possible after a scheduled start is missed
If the task fails, restart every: 1 minute
If the running task does not end when requested, force it to stop
```
