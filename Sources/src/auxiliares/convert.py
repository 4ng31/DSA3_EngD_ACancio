import os, sys, gc

def main(args):
    with open(args.filename) as fin, open(args.filename+'.csv', "w") as fout:
        for line in fin:
            fout.write(line.replace(' ', ',', )
                       
if __name__ == "__main__":
    
    start_time = time.time()
    parser = argparse.ArgumentParser(description='Convert schedule to CSV.')
    parser.add_argument('-s', '--schedule', dest='schd',type=argparse.FileType('r'),
                        help='Read schedule fiel.', required=True)
    
    args = parser.parse_args()
    main(args)