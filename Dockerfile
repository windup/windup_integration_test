FROM fedora:31

MAINTAINER Shveta Sachdeva <sshveta@redhat.com>
LABEL description="Red Hat Application Migration Toolkit Web-Console"


RUN dnf -y update && dnf clean all
RUN dnf -y install java java-devel unzip wget python3-virtualenv && dnf clean all

# set java env
ENV JAVA_HOME /usr/lib/jvm/java-openjdk
ENV BASE_URL="https://repo1.maven.org/maven2/org/jboss/windup"
ENV WEB_CONSOLE="rhamt-web-distribution"
ENV VERSION="4.3.1.Beta1"
ENV WEB_DISTRIBUTION="${WEB_CONSOLE}-${VERSION}"
ENV WEB_CONSOLE_FILE="${WEB_DISTRIBUTION}-with-authentication.zip"
ENV WEB_CONSOLE_FILE_PATH="${BASE_URL}/web/${WEB_CONSOLE}/${VERSION}/${WEB_CONSOLE_FILE}"


# https://repo1.maven.org/maven2/org/jboss/windup/web/rhamt-web-distribution/4.3.1.Beta1/rhamt-web-distribution-4.3.1.Beta1-with-authentication.zip
# https://repo1.maven.org/maven2/org/jboss/windup/rhamt-cli/4.3.1.Beta1/rhamt-cli-4.3.1.Beta1-offline.zip

RUN wget -o - $WEB_CONSOLE_FILE_PATH -P /tmp| wc -l > /number && unzip -o /tmp/$WEB_CONSOLE_FILE -d /tmp

RUN useradd jboss \
        && usermod -G jboss jboss \
        && mkdir /opt/rhamt \
        && mkdir /opt/submitted-ears \
        && mkdir /opt/rhamt-data

WORKDIR /opt/rhamt

RUN mv -r /tmp/${WEB_DISTRIBUTION}/* ./ && chown jboss:jboss /opt -R

EXPOSE 8080

USER jboss

ENTRYPOINT ["/opt/rhamt/run_rhamt.sh", "-b 0.0.0.0", "-Dwindup.data.dir=/opt/rhamt-h2-data"]
