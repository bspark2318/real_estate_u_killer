#!/usr/bin/env python3
import argparse
from website_driver import WebsiteDriver

def main():
    parser = argparse.ArgumentParser(description='Login to Real Estate U')
    parser.add_argument('-u', '--username', required=True, help='Username')
    parser.add_argument('-p', '--password', required=True, help='Password')

    args = parser.parse_args()

    w_driver = WebsiteDriver(args.username, args.password)
    w_driver.start_studying()


if __name__ == '__main__':
    main()