FROM registry.access.redhat.com/ubi9/ubi

MAINTAINER Shveta Sachdeva <sshveta@redhat.com>
LABEL description="Migration Toolkit for Applications Web-Console"


RUN dnf -y update && dnf clean all
RUN dnf -y install  java-11-openjdk-devel unzip wget && dnf clean all
RUN dnf -y install python

# set java env
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk
ENV BASE_URL="https://repo1.maven.org/maven2/org/jboss/windup"
ENV WEB_CONSOLE="mta-web-distribution"
ENV VERSION=5.3.1.Final
ENV WEB_DISTRIBUTION="${WEB_CONSOLE}-${VERSION}"
ENV WEB_CONSOLE_FILE="${WEB_DISTRIBUTION}-with-authentication.zip"
ENV WEB_CONSOLE_FILE_PATH="${BASE_URL}/web/${WEB_CONSOLE}/${VERSION}/${WEB_CONSOLE_FILE}"
RUN echo $WEB_CONSOLE_FILE_PATH

RUN wget -o - $WEB_CONSOLE_FILE_PATH --show-progress --progress=dot -P /tmp| wc -l > /number && unzip -o /tmp/$WEB_CONSOLE_FILE -d /tmp 

RUN echo $WEB_CONSOLE_FILE_PATH
RUN echo $WEB_CONSOLE_FILE

RUN useradd jboss \
        && usermod -G jboss jboss \
        && mkdir /opt/mta \
        && mkdir /opt/submitted-ears \
        && mkdir /opt/mta-data

WORKDIR /opt/mta

RUN mv /tmp/${WEB_DISTRIBUTION}/* ./ && chown jboss:jboss /opt -R

# For some reason this dir is not empty on docker image and build fails
# TODO investigate and remove this
RUN rm -rf /opt/mta/standalone/configuration/standalone_xml_history/current/*

EXPOSE 8080

USER jboss

ENTRYPOINT ["/opt/mta/run_mta.sh", "-b 0.0.0.0", "-Dwindup.data.dir=/opt/mta-h2-data"]
