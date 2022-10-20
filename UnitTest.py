import unittest
import os
# from os import path

class BasicTest(unittest.TestCase):
   
    def test(self):
        
        if(os.path.exists('Assignment_2.py')):
            self.assertTrue(True)
        else:
            self.assertTrue(False)

 
        

if __name__ == '__main__':

        unittest.main()



 

