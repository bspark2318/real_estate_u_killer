#!/usr/bin/env python3
import argparse
from website_driver import WebsiteDriver

def main():
    parser = argparse.ArgumentParser(description='Login to Real Estate U')
    parser.add_argument('-u', '--username', required=False, help='Username', default="")
    parser.add_argument('-p', '--password', required=False, help='Password', default="")

    args = parser.parse_args()

    w_driver = WebsiteDriver(args.username, args.password)
    w_driver.start_studying()


if __name__ == '__main__':
    main()