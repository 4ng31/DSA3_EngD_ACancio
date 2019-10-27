import os, sys, gc
import argparse
import fileinput
    
def main(args):

    f = fileinput.FileInput(args.schd, inplace=True, backup='.bak')
    for line in f:
        print line
    f.close()
    
    with open(args.schd, 'r') as fp:
        text=fp.read().replace('\r', ' \n')
    
    with open(args.schd, 'w') as fo:
        fo.write(text)
    
    text=''
    with open(args.schd, 'r') as fp:  
        lines = fp.readlines()
        for line in lines:
            if not line.strip(): continue  # skip the empty line
            line=line.replace('\n','')
            line=' '.join(line.split())
            line=line.replace(' ', ',')+',200000,16'+'\n'
            text=text+line
    
    with open(args.schd, 'w') as fo:
        fo.write(text)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Convert schedule to CSV.')
    parser.add_argument('-s', '--schedule', dest='schd',type=str,
                        help='Read schedule fiel.', required=True)
    args = parser.parse_args()
    main(args)