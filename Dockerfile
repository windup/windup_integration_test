FROM fedora:31

MAINTAINER Shveta Sachdeva <sshveta@redhat.com>
LABEL description="Migration Toolkit for Applications Web-Console"


RUN dnf -y update && dnf clean all
RUN dnf -y install java java-devel unzip wget xterm python3-virtualenv && dnf clean all

# set java env
ENV JAVA_HOME /usr/lib/jvm/java-openjdk
ENV BASE_URL="https://repo1.maven.org/maven2/org/jboss/windup"
ENV WEB_CONSOLE="mta-web-distribution"
ENV VERSION="4.3.1.Beta1"
ENV WEB_DISTRIBUTION="${WEB_CONSOLE}-${VERSION}"
ENV WEB_CONSOLE_FILE="${WEB_DISTRIBUTION}-with-authentication.zip"
ENV WEB_CONSOLE_FILE_PATH="${BASE_URL}/web/${WEB_CONSOLE}/${VERSION}/${WEB_CONSOLE_FILE}"


RUN wget -o - $WEB_CONSOLE_FILE_PATH -P /tmp| wc -l > /number && unzip -o /tmp/$WEB_CONSOLE_FILE -d /tmp

RUN useradd jboss \
        && usermod -G jboss jboss \
        && mkdir /opt/mta \
        && mkdir /opt/submitted-ears \
        && mkdir /opt/mta-data

WORKDIR /opt/mta

RUN mv /tmp/${WEB_DISTRIBUTION}/* ./ && chown jboss:jboss /opt -R

EXPOSE 8080

USER jboss

ENTRYPOINT ["/opt/mta/run_mta.sh", "-b 0.0.0.0", "-Dwindup.data.dir=/opt/mta-h2-data"]
