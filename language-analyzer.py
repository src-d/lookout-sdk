#!/usr/bin/env python3

# Example Analyser gRPC service implementation.
# Posts file-level comments for every file with language detected.

port_to_listen = 2021
data_srv_addr = "localhost:10301"

def main():
    print("starting gRPC Analyzer server at port {}".format(port_to_listen))
    #TODO: start grpc Server

if __name__ == "__main__":
    main()