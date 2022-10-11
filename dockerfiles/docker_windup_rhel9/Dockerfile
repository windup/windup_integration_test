FROM registry.access.redhat.com/ubi9/ubi

MAINTAINER Shveta Sachdeva <sshveta@redhat.com>
LABEL description="Windup Web-Console"


RUN dnf -y update && dnf clean all
RUN dnf -y install  java-11-openjdk-devel unzip wget xterm python3-virtualenv && dnf clean all

ARG VERSION
ARG WEB_CONSOLE_FILE
# set java env
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk
ENV BASE_URL="https://oss.sonatype.org/content/repositories/snapshots/org/jboss/windup"
ENV WEB_CONSOLE="windup-web-distribution"
ENV WEB_DISTRIBUTION="${WEB_CONSOLE}-${VERSION}"
ENV WEB_CONSOLE_FILE_PATH="${BASE_URL}/web/${WEB_CONSOLE}/${VERSION}/${WEB_CONSOLE_FILE}"


RUN wget -o - $WEB_CONSOLE_FILE_PATH -P /tmp| wc -l > /number && unzip -o /tmp/$WEB_CONSOLE_FILE -d /tmp

RUN echo $WEB_CONSOLE_FILE_PATH
RUN echo $WEB_CONSOLE_FILE

RUN useradd jboss \
        && usermod -G jboss jboss \
        && mkdir /opt/windup \
        && mkdir /opt/submitted-ears \
        && mkdir /opt/windup-data

WORKDIR /opt/windup

RUN mv /tmp/${WEB_DISTRIBUTION}/* ./ && chown jboss:jboss /opt -R

# For some reason this dir is not empty on docker image and build fails
# TODO investigate and remove this
RUN rm -rf /opt/windup/standalone/configuration/standalone_xml_history/current/*

EXPOSE 8080

USER jboss

ENTRYPOINT ["/opt/windup/run_windup.sh", "-b 0.0.0.0", "-Dwindup.data.dir=/opt/windup-h2-data"]
