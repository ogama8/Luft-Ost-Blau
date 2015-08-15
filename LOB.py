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


### MAKE SSL HAPPY   --------------------------------------------------------
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()


### LOB   -------------------------------------------------------------------
import lob
from api_key import sel_key

key_select = 0
sys.stdout.write('\033[93m' + "\nUse the Live API Key? (y/N): " + '\033[0m')
keystroke = raw_input()
if (keystroke == 'y' or keystroke == 'Y'):
   key_select = 1

lob.api_key        = sel_key(key_select)
SENDER_NAME        = "Eli Backer"
SENDER_DESCRIPTION = "Home"


### DEFINES FOR CUSTOM TUPLE   ----------------------------------------------
INDEX       = 0
NAME        = 1
DESCRIPTION = 2
ID          = 3

def indexFromName(name_list, name):
   names     = [x[NAME] for x in name_list] 
   to_return = []
   offset    = 0
   while name in names:
      to_return.append(names.index(name) + offset)
      names.remove(name)
      offset += 1
   return to_return


### -------------------------------------------------------------------------
### MAIN CODE
### -------------------------------------------------------------------------

## Validity Check   -------------------------------------
if (len(sys.argv) != 2):
   print("\n" +
         '\033[93m' + "Illegal Use!\n" + '\033[0m' + 
         "  Correct use is:\n" +
         "  LOB.py [Image Filepath]\n")
   sys.exit(0)


## File Path Setup   ------------------------------------
if(key_select == 1):
   if (not os.path.exists("sent")):
      os.makedirs("sent")
   os.chdir("sent")
else:
   if (not os.path.exists("sent_test")):
      os.makedirs("sent_test")
   os.chdir("sent_test")



## Address List   ---------------------------------------
address_list = lob.Address.list(count = 100)

names = [(id_num, address.name, address.description, address.id) for (id_num, address) in enumerate(reversed(address_list.data))]

while True:
   os.system("clear")   # This is Unix specific
   
   print('\033[104m' + "ID# " + u'\u2502' + " Name                               " + u'\u2502' + " Description                " + '\033[0m')
   for i in range(0, 70):
      if (i == 4 or i == 41):
         sys.stdout.write(u'\u253c')
      else:
         sys.stdout.write(u'\u2500')
   print ' '

   i = 0
   for person in sorted(names, key=lambda tup: tup[NAME]):
      if (i % 2 == 1):
         sys.stdout.write('\033[100m')
      else:
         sys.stdout.write('\033[0m')
      i += 1

      print str(person[INDEX]).rjust(3) + " " + u'\u2502' + " " + person[NAME].ljust(34) + " " + u'\u2502' + " " + person[DESCRIPTION].ljust(26)

   while True:
      sys.stdout.write('\033[0m' + "\nPlease enter an ID number to mail to ('q' to exit): ")
      keystroke = raw_input()
      if (keystroke == 'q' or keystroke == 'Q'):
         sys.exit(0)
      elif (keystroke.isdigit()):
         break
      else:
         print '\033[91m' + "Invalid input '" + keystroke + "'" + '\033[0m'

   to_index       = int(keystroke)
   to_name        = names[to_index][NAME]
   to_description = names[to_index][DESCRIPTION]
   to_id          = names[to_index][ID]

   sys.stdout.write("\nMailing to " + to_name + "? (Y/n): ")
   
   keystroke = raw_input()
   if(keystroke == '' or keystroke == 'y' or keystroke == 'Y'):
      break


## Recipient-Based Archive Directory Changes   ----------
if (not os.path.exists(to_name)):
   os.makedirs(to_name)
os.chdir(to_name)

if (not os.path.exists(to_description)):
   os.makedirs(to_description)
os.chdir(to_description)

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
   message_file.write("<!-- This is a message to {name}, {description} written on {date} -->\n<p>\n\n</p>\n<p>\n\n</p>\n<p>\n\n</p>\n<p>\n\n</p>\n<p>\n   Eli&mdash;\n</p>\n".format(name=to_name, description=to_description, date=today))
   message_file.close()

call([EDITOR, "message.html"])
call(["aspell", "-x", "-c", "message.html"])


## Image Resize   ---------------------------------------
front_im = Image.open(sys.argv[1])

size = front_im.size

front_im = front_im.crop((0, 0, size[0], int(float(size[0]) / WIDTH * HEIGHT)))
front_im = front_im.rotate(90)

front_im = front_im.resize((HEIGHT, WIDTH), PIL.Image.LANCZOS)
front_im.save('front' + '.jpg', 'JPEG')


## Postcard Send   --------------------------------------
indices = indexFromName(names, SENDER_NAME)
for index in indices:
   if SENDER_DESCRIPTION in names[index]:
      sender_index = index
sender_id = names[sender_index][ID]

sys.stdout.write('\033[96m' + "Are you sure you want to send? (Y/n): " + '\033[0m')
keystroke = raw_input()
if (keystroke == 'n' or keystroke == 'N'):
   sys.exit(0)

postcard_response = lob.Postcard.create(
   description  = to_name + ", " + to_description + " - " + str(times_written + 1).zfill(3),
   to_address   = to_id,
   from_address = sender_id,
   front = open("front.jpg", 'rb'),
   back  = """
   <html>
      <head>
         <title>4x6 Postcard Back Template modified by Eli Backer</title>
         <style>
            @font-face {
               font-family: 'Hepworth';
               font-style: normal;
               font-weight: 400;
               src: url('https://github.com/ogama8/Luft-Ost-Blau/blob/master/hepworth-regular-webfont.ttf?raw=true') format('truetype');
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

            <div class="text">""" +
               open("message.html", 'r').read() +
            """
            </div>
         </div>
      </body>
   </html>
   """
)

sys.stdout.write('\033[92m' + "\n\nThe postcard has been created and should be delivered by " + postcard_response.expected_delivery_date + "." + '\033[0m' + "\nWould you like to view the card? (y/N): ")

keystroke = raw_input()
if (keystroke == 'y' or keystroke == 'Y'):
   webbrowser.open_new_tab(postcard_response.url)

print ' '

