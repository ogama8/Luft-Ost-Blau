"""
Luft Ost Blau (LOB) (Air East Blue) is a client for sending postcards using
the Lob service, by taking in a picture to send and person to send to.  The
program then prompts the user for the back text of the postcard and uses 
Lob's API to pass this data on to them.

Started June 2015 by Eli Backer.
"""

### GLOBALS   ---------------------------------------------------------------
DPI         = 600
WIDTH       = int(6.25 * DPI)
HEIGHT      = int(4.25 * DPI)
PADDING     = int((0.25 + 0.125) * DPI)


### IMPORTS   ---------------------------------------------------------------
import sys
import math
import PIL


### IMAGE/TEXT HANDLING   ---------------------------------------------------
from PIL import Image, ImageFont, ImageDraw
TEXT_MULT = 4     # This is the scaler to get better looking text by
                  # rendering big and then downscaling with Anti-Aliasing

serif_font      = ImageFont.truetype("resources/hepworth-regular.ttf", 60 * TEXT_MULT)
TEXT_HEIGHT     = 100

# From the top of the Safe Zone to the KEEP OUT is exactly 1.25"
# From the left of the Safe Zone to the KEEP OUT is exactly 2.25"
NUM_FULL_LINES  = math.floor(DPI / TEXT_HEIGHT * 1.25)
FULL_LINE_WIDTH = int(WIDTH - 2*PADDING) * TEXT_MULT
HALF_LINE_WIDTH = int(2.25 * DPI) * TEXT_MULT
NEW_LINE        = 0.35      # This, plus 1 will be the line spacing for a \n


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


message = "<p>I LOOKED AT MY NOTES AND I DIDN'T LIKE THEM.  I'd spent three days at U.S. Robots and might as well have spent them at home with the Encyclopedia Tellurica.</p>" + "<p>Susan Calvin had been born in the year 1982, they said, which made her seventy-five now.  Everyone knew that. Appropriately enough, U.S. Robot and Mechanical Men, Inc. was seventy-five also, since it had been in the year of Dr. Calvin's birth that Lawrence Robertson had first taken out incorporation papers for what eventually became the strangest industrial giant in man's history. Well, everyone knew that, too.</p>" + "<p>At the age of twenty, Susan Calvin had been part of the particular Psycho-Math seminar at which Dr. Alfred Lanning of U.S. Robots had demonstrated the first mobile robot to be equipped with a voice. It was a large, clumsy unbeautiful robot, smelling of machine-oil and destined for the projected mines on Mercury. But it could speak and make sense.</p>"


'''

message_arr = message.split(' ')
message_arr.append(' ')     # Final character gets rid of annoying edge case.
# Additionally, this final character being a space, which is impossible after
# the split operation gives us a nice signal value to look for.

back_im = Image.new('RGB', (WIDTH * TEXT_MULT, HEIGHT * TEXT_MULT), (255, 255, 255))
draw = ImageDraw.Draw(back_im)

cur_line = 0
while (message_arr[0] != ' '):
   current_text = message_arr[0]
   old_text = ''
   line_space = 1

   while (draw.textsize(current_text, serif_font)[0] <\
         (FULL_LINE_WIDTH if cur_line < NUM_FULL_LINES else HALF_LINE_WIDTH)\
         and message_arr[0] != ' '\
         and '\n' not in message_arr[0]):
      current_text += " " + message_arr[1]
      old_text += " " + message_arr.pop(0)   # get rid of element 0
   
   if ('\n' in message_arr[0]):
      old_text += " " + message_arr.pop(0)
      line_space += NEW_LINE

   draw.text((PADDING * TEXT_MULT, (PADDING + cur_line*TEXT_HEIGHT) * TEXT_MULT), old_text, (0, 0, 0), font=serif_font)
   cur_line += line_space


#back_im = back_im.resize((WIDTH, HEIGHT), Image.LANCZOS)

back_im = back_im.rotate(90)
back_im.save('back' + '.pdf', 'PDF')

#back_im.show()
#sys.exit(0)

'''







postcard_response = lob.Postcard.create(
   description  = 'Test 8',
   to_address   = 'adr_74a812cd49adc342',
   from_address = 'adr_74a812cd49adc342',
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

