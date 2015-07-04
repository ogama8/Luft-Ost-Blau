"""
Luft Ost Blau (LOB) (Air East Blue) is a client for sending postcards using
the Lob service, by taking in a picture to send and person to send to.  The
program then prompts the user for the back text of the postcard and uses 
Lob's API to pass this data on to them.

Started June 2015 by Eli Backer.
"""

### IMPORTS   ---------------------------------------------------------------
import sys
import os
import math
import datetime
import PIL
import webbrowser
from   subprocess import call

### IMAGE HANDLING   --------------------------------------------------------
from PIL import Image
DPI         = 600
WIDTH       = int(6.25 * DPI)
HEIGHT      = int(4.25 * DPI)
PADDING     = int((0.25 + 0.125) * DPI)


### MAKE SSL HAPPY   --------------------------------------------------------
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()


### LOB   -------------------------------------------------------------------
import lob
from api_key import my_key
lob.api_key = my_key()
SENDER_NAME = "Eli Backer"


### MAIN CODE   -------------------------------------------------------------
## Validity Check   -------------------------------------
if (len(sys.argv) != 2):
   print("\n" +
         '\033[93m' + "Illegal Use!\n" + '\033[0m' + 
         "  Correct use is:\n" +
         "  LOB.py [Image Filepath]\n")
   sys.exit(0)

#"""
## File Path Setup   ------------------------------------
if (not os.path.exists("sent")):
   os.makedirs("sent")
os.chdir("sent")


## Address List   ---------------------------------------
address_list = lob.Address.list(count = 100)


# This is sort-of messed up.  I make a dictionary with the names as keys so
# I can alphabetize by key, then another one with IDs as keys so I can look
# up addresses by their ID.  Ideally there'd be a tuple in here somewhere.
names_n = {address.name: id_num for (id_num, address) in enumerate(reversed(address_list.data))}
names_id = {id_num: address for (id_num, address) in enumerate(reversed(address_list.data))}


while True:
   os.system("clear")   # This is Unix specific
   
   print("ID# " + u'\u2502' + " Name                               " + u'\u2502' + " Description")
   for i in range(0, 69):
      if (i == 4 or i == 41):
         sys.stdout.write(u'\u253c')
      else:
         sys.stdout.write(u'\u2500')
   print

   for name in sorted(names_n):
      print str(names_n[name]).rjust(3) + " " + u'\u2502' + " " + name.ljust(34) + " " + u'\u2502' + " " + names_id[names_n[name]].description

   sys.stdout.write("\nPlease enter an ID number to mail to: ")
   # Yes, I know this input is not sanatary.
   to_id = int(raw_input())
   to_name = names_id[to_id].name
   
   sys.stdout.write("\nMailing to " + to_name + "? (Y/n): ")
   
   keystroke = raw_input()
   if(keystroke == '' or keystroke == 'y' or keystroke == 'Y'):
      break


## Recipient-Based Archive Directory Changes   ----------
if (not os.path.exists(to_name)):
   os.makedirs(to_name)
os.chdir(to_name)

if (not os.path.exists(names_id[to_id].description)):
   os.makedirs(names_id[to_id].description)
os.chdir(names_id[to_id].description)

times_written = len(next(os.walk('./'))[1])

today = datetime.date.today().isoformat()
if (os.path.exists(today)):
   print '\033[91m' + "\nYou've already written to " + to_name + " today!" + '\033[0m'
   sys.exit(0)
os.makedirs(today)
os.chdir(today)


## Launch Editor for Message   --------------------------
EDITOR = os.environ.get('EDITOR') if os.environ.get('EDITOR') else 'vim'

if (not os.path.isfile("message.html")):
   message_file = open("message.html", 'w')
   message_file.write("<!-- This is a message to {name} written on {date} -->\n<p>\n\n</p>\n".format(name=to_name, date=today))
   message_file.close()

call([EDITOR, "message.html"])
call(["aspell", "-x", "-c", "message.html"])
#"""

## Image Resize   ---------------------------------------
front_im = Image.open(sys.argv[1])

size = front_im.size

front_im = front_im.crop((0, 0, size[0], int(size[0] / WIDTH * HEIGHT)))
front_im = front_im.rotate(90)

front_im = front_im.resize((HEIGHT, WIDTH), PIL.Image.LANCZOS)
front_im.save('front' + '.jpg', 'JPEG')

sys.exit(0)


## Postcard Send   --------------------------------------
postcard_response = lob.Postcard.create(
   description  = to_name + " - " + str(times_written + 1).zfill(3),
   to_address   = names_id[to_id].id,
   from_address = names_id[names_n[SENDER_NAME]].id,
   front = open("front.jpg", 'rb'),
   back  = """
   <html>
      <head>
         <title>4x6 Postcard Back Template modded by Eli Backer</title>
         <style>
            @font-face {
               font-family: 'Hepworth';
               font-style: normal;
               font-weight: 400;
               src: url('http://download995.mediafire.com/e8996eql1asg/lh7jzetc7p8f4t2/hepworth-regular-webfont.ttf') format('truetype');
            }

            *, *:before, *:after {
               -webkit-box-sizing: border-box;
               -moz-box-sizing: border-box;
               box-sizing: border-box;
            }
            body {
               width: 6.25in;
               height: 4.25in;
               margin: 0;
               padding: 0;
            }
            #safe-area {
               position: absolute;
               width: 6in;
               height: 4in;
               left: 0.125in;
               top: 0.125in;
            }
            #keep-out-top {
               float: right;
               width: 0.1in;
               height: 1.4in;
            }      
            #keep-out {
               float: right;
               clear: both;
               width: 3.5in;
               height: 2.6in;
            }      

            .text {
               margin: 0.125in;
               font-family: 'Hepworth', sans-serif;
               font-size: 12px;
               font-weight: 400;
               color: black;
            }
         </style>
      </head>

      <body>
         <div id="safe-area">
            <div id="keep-out-top"></div>
            <div id="keep-out"></div>

            <div class="text">
               {{message}}
            </div>
         </div>
      </body>
   </html>
   """,
   data  = {'message': open("message.html", 'r').read()}
)

sys.stdout.write("The postcard has been successfully created.  It will be sent to " + to_name + " and should be delivered by " + postcard_response.expected_delivery_date + ".  Would you like to view the card? (Y/n): ")

keystroke = raw_input()
if(keystroke == '' or keystroke == 'y' or keystroke == 'Y'):
   webbrowser.open_new_tab(postcard_response.url)

print '\n'
