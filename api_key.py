"""
api_key.py defines the function 'my_key()' which may be called by another
script to get the Lob API Key.  This is in a seperate file so as to make
my github public commits more secure/not hand out free postcards like candy.

Started June 2015 by Eli Backer.
"""

def sel_key(key):
   if (key == 1):
      return "live_keygoeshere"
   else:
      return "test_keygoeshere" 

