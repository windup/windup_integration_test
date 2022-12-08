import logging

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def main():
    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = DummyAuthorizer()

    # Define a new user having full r/w permissions and a read-only
    authorizer.add_user("ftpuser", "ftpuser", "/home/ftpuser/", perm="elradfmwMT")

    # Instantiate FTP handler class
    handler = FTPHandler
    handler.authorizer = authorizer
    # Passive ports
    handler.passive_ports = range(5000, 5020)
    handler.permit_foreign_addresses = True

    handler.banner = "MTR Interop Test FTP Server"

    # connect using an address 0.0.0.0 with port 21
    address = ("127.0.0.1", 3333)
    server = FTPServer(address, handler)

    # set a limit for connections
    server.max_cons = 5
    server.max_cons_per_ip = 5

    # Add logging
    logging.basicConfig(filename="/tmp/ftp_log.txt", level=logging.DEBUG)

    # start ftp server
    server.serve_forever()


if __name__ == "__main__":
    main()
