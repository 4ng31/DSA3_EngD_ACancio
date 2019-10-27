#!/usr/bin/python
# -*- coding: utf-8 -*-
#"""
#@author: Angel Cancio
#"""

def function(thefile):
	return 0
    
def main(args):
    print args.filename
    
    if args.filename:
        upload(args.filename)
    
    return 0
    
if __name__ == '__main__':
      
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-f', '--filename', help='File to process', default='False')
    
    args = parser.parse_args()
   
    main(args)
