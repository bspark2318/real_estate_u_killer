#!/usr/bin/env python3
import argparse
from website_driver import login


def main():
    parser = argparse.ArgumentParser(description='Login to Real Estate U')
    parser.add_argument('-u', '--username', required=True, help='Username')
    parser.add_argument('-p', '--password', required=True, help='Password')

    args = parser.parse_args()

    login(args.username, args.password)


if __name__ == '__main__':
    main()