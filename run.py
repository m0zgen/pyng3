#!/usr/bin/env python3
# Created by Yevgeniy Goncharov, https://lab.sys-adm.in
# Script for check and analyze response times of servers
# Version 1.0
# Example: python3 run.py servers.txt

import argparse
import socket
from ping3 import ping
from tqdm import tqdm


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error while determining the local IP address: {e}")
        return None


def read_server_list(file_path):
    try:
        with open(file_path, 'r') as file:
            server_list = [line.strip() for line in file if line.strip()]
        return server_list
    except Exception as e:
        print(f"Error while reading the file {file_path}: {e}")
        return []


def check_ping(ip_address):
    try:
        response_time = ping(ip_address, timeout=3, unit='ms')
        return response_time
    except Exception as e:
        print(f"Error while pinging {ip_address}: {e}")
        return None


def find_fastest_and_slowest_servers(server_list, local_ip):
    fastest_server = None
    slowest_server = None
    fastest_response_time = float('inf')
    slowest_response_time = 0

    for server in tqdm(server_list, desc="Checking speed", leave=False):
        # Check if the IP is local
        if server != local_ip:
            response_time = check_ping(server)
            if response_time is not None:
                if response_time < fastest_response_time:
                    fastest_response_time = response_time
                    fastest_server = server
                if response_time > slowest_response_time:
                    slowest_response_time = response_time
                    slowest_server = server

    return fastest_server, fastest_response_time, slowest_server, slowest_response_time


def calculate_average_response_time(server_list, local_ip):
    total_response_time = 0
    valid_servers = 0

    for server in tqdm(server_list, desc="Checking speed", leave=False):
        # Check if the IP is local
        if server != local_ip:
            response_time = check_ping(server)
            if response_time is not None:
                total_response_time += response_time
                valid_servers += 1

    if valid_servers > 0:
        average_response_time = total_response_time / valid_servers
        return average_response_time
    else:
        return None


def main():
    parser = argparse.ArgumentParser(description="Check and analyze response times of servers.")
    parser.add_argument("file_path", help="Path to the file containing a list of servers.")
    args = parser.parse_args()

    local_ip = get_local_ip()

    if local_ip is None:
        print("Failed to determine the local IP address. Exiting the script.")
        return

    print(f"Local IP address: {local_ip}")

    server_list = read_server_list(args.file_path)

    if not server_list:
        print(f"The server list from the file {args.file_path} is empty or cannot be read.")
    else:
        # Exclude the local IP from the server list
        server_list = [server for server in server_list if server != local_ip]

        fastest_server, fastest_response_time, slowest_server, slowest_response_time = find_fastest_and_slowest_servers(
            server_list, local_ip)

        if fastest_server is not None:
            print(f"Fastest server in first time response: {fastest_server}")
            print(f"Response time: {fastest_response_time} ms")

        # Slower in first time test
        if slowest_server is not None:
            print(f"Second fastest server in first time response: {slowest_server}")
            print(f"Response time: {slowest_response_time} ms")

        if len(server_list) >= 2:
            server_list.remove(fastest_server)
            second_fastest_server, second_fastest_response_time, _, _ = find_fastest_and_slowest_servers(server_list,
                                                                                                         local_ip)
            print(f"Third test fastest server (exclude first server): {second_fastest_server}")
            print(f"Response time: {second_fastest_response_time} ms")

        # print("\nStatistics for the remaining servers (sorted by response time):")
        # sorted_servers = sorted(server_list, key=lambda x: check_ping(x) if check_ping(x) is not None else float(
        # 'inf'))
        print("\nStatistics for the remaining servers (sorted by response time):")
        sorted_servers = sorted([(server, check_ping(server)) for server in server_list],
                                key=lambda x: x[1] or float('inf'))
        for server, response_time in sorted_servers:
            if response_time is not None:
                print(f"{server}: Response time: {response_time} ms")

        average_response_time = calculate_average_response_time(server_list, local_ip)
        if average_response_time is not None:
            print(f"\nAverage response time for all servers: {average_response_time} ms")


if __name__ == "__main__":
    main()
