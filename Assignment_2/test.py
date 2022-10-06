import unittest
import os

class SimpleTest(unittest.TestCase):
    
 
    def test(self):
        file_list = ['README.md']
        CURR_DIR = os.getcwd()
        dir_list = os.listdir(CURR_DIR)
        output = True
        for files in file_list:
            if files in dir_list:
                break
            else:
               output = False
        self.assertTrue(output)

if __name__ == '__main__':

        unittest.main()
