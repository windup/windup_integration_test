FROM python:3.8

# Update and install FTP
RUN apt -y update && apt -y install ftp

# Upgrade pip and install required packages
RUN pip install --upgrade pip
RUN pip install pytest importscan pyftpdlib

# Copy the windup_integration_test repo into /tmp/integration_tests
RUN mkdir /tmp/integration_tests
WORKDIR /tmp/integration_tests
COPY . .

# Add interop env file to mta/conf/env.yaml
COPY dockerfiles/interop/src/env.yaml mta/conf/env.yaml

# Create the /ftpuser directory
RUN mkdir -p /home/ftpuser/mtr/applications

# Add WAR file for testing
COPY dockerfiles/interop/src/acmeair-webapp-1.0-SNAPSHOT.war /home/ftpuser/mtr/applications/acmeair-webapp-1.0-SNAPSHOT.war

# Add ftp_server.py script
COPY dockerfiles/interop/src/ftp_server.py /tmp/ftp_server.py

# Set required permissions for OpenShift usage
RUN chgrp -R 0 /tmp && \
    chmod -R g=u /tmp

RUN chgrp -R 0 /home && \
    chmod -R g=u /home

CMD ["/bin/bash"]
