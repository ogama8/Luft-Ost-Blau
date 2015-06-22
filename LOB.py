"""
Luft Ost Blau (LOB) (Air East Blue) is a client for sending postcards using
the Lob service, by taking in a picture to send and person to send to.  The
program then prompts the user for the back text of the postcard and uses 
Lob's API to pass this data on to them.

Started June 2015 by Eli Backer.
"""

### IMPORTS   ---------------------------------------------------------------
import sys
import math
import PIL


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



### MAIN CODE   -------------------------------------------------------------
## Validity Check   -------------------------------------
if (len(sys.argv) != 2):
   print("\n" +
         '\033[93m' + "Illegal Use!\n" + '\033[0m' + 
         "  Correct use is:\n" +
         "  LOB.py [Image Filepath]\n")
   sys.exit(0)

front_im = Image.open(sys.argv[1])

size = front_im.size

front_im = front_im.crop((0, 0, size[0], int(size[0] / WIDTH * HEIGHT)))
front_im = front_im.rotate(90)

front_im = front_im.resize((HEIGHT, WIDTH), PIL.Image.LANCZOS)
front_im.save('front' + '.jpg', 'JPEG')


message = "<p>Hello World (or at least my parents)!</p>" + "<p>By the time you get this, I'm either surfing or gone to RISD.  Either way, I hope it finds you well and that the text is readable.  I'm tired.  It's 2:45a and I have to get up at 5:55a.  That's soon, so I'm keeping this short.  It probably won't even have to wrap around the address box.  This is all pretty hacked together right now.  Hopefully in the future there'll be a spell-checker and other fun things.</p>" + "<p>That's all for now, love you!</p>" + "<p>Eli&mdash;</p>"



postcard_response = lob.Postcard.create(
   description  = 'Tom & JL - 001',
   to_address   = 'adr_1bfeac2bb50caf6f',
   from_address = 'adr_0864417ae5dcef5a',
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
   data  = {'message': message}
   #message = "Hello World!"
   #message = "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.\n" + "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.\n" + "Neque porro quisquam est, qui dolorem ipsum.\n\n" + "Eli"
)

print postcard_response

