FROM atlassian/confluence-server:6.15.6-adoptopenjdk8

ENV ATLASSIAN_INSTALL_DIR /opt/atlassian
ENV CONFLUENCE_HOME /var/atlassian/application-data/confluence

# The id of the confluence user is 2002
RUN chown -R 2002:2002 ${ATLASSIAN_INSTALL_DIR}

ADD bin/entrypoint.py /entrypoint.py
RUN chmod 755 /entrypoint.py

ADD install/etc/server.xml.j2 ${ATLASSIAN_INSTALL_DIR}/etc/
RUN chown 2002:2002 ${ATLASSIAN_INSTALL_DIR}/etc/server.xml.j2

RUN chown -R 2002:2002 ${CONFLUENCE_HOME}

USER 2002

CMD ["/entrypoint.py", "-fg"]
