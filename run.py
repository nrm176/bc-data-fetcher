import argparse
from handler import DownloadHanlder

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Arguments of bc-data-fetcher')
    parser.add_argument('--num_of_requests', help='how many requests to create', default='1')
    args = parser.parse_args()
    d = DownloadHanlder()
    d.run(args.num_of_requests)