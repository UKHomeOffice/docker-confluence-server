FROM atlassian/confluence-server:7.3.2

ENV ATLASSIAN_INSTALL_DIR /opt/atlassian
ENV CONFLUENCE_HOME /var/atlassian/application-data/confluence

# The id of the confluence user is 2002
RUN chown -R 2002:2002 ${ATLASSIAN_INSTALL_DIR}

COPY bin/hardening.py /hardening.py
# modify the original entrypoint.py to call our hardening functions
RUN sed -i '/from entrypoint_helpers/a from hardening import gen_cfg_no_chown, all_logs_to_stdout, gen_configs' /entrypoint.py && \
    sed -i '/start_app(/i all_logs_to_stdout()' /entrypoint.py && \
    sed -i 's/^gen_cfg/gen_cfg_no_chown/' /entrypoint.py && \
    sed -i '/CONFLUENCE_HOME =/a gen_configs(env)' /entrypoint.py && \
    sed -i '/1catalina.org.apache.juli.FileHandler.rotatable/d' /opt/atlassian/confluence/conf/logging.properties && \
    sed -i '/1catalina.org.apache.juli.AsyncFileHandler.level/i 1catalina.org.apache.juli.FileHandler.rotatable = false' /opt/atlassian/confluence/conf/logging.properties && \
    sed -i '/2localhost.org.apache.juli.FileHandler.rotatable/d' /opt/atlassian/confluence/conf/logging.properties && \
    sed -i '/2localhost.org.apache.juli.AsyncFileHandler.level/i 2localhost.org.apache.juli.FileHandler.rotatable = false' /opt/atlassian/confluence/conf/logging.properties && \
    sed -i '/3manager.org.apache.juli.FileHandler.rotatable/d' /opt/atlassian/confluence/conf/logging.properties && \
    sed -i '/3manager.org.apache.juli.AsyncFileHandler.level/i 3manager.org.apache.juli.FileHandler.rotatable = false' /opt/atlassian/confluence/conf/logging.properties && \
    sed -i '/4host-manager.org.apache.juli.FileHandler.rotatable/d' /opt/atlassian/confluence/conf/logging.properties && \
    sed -i '/4host-manager.org.apache.juli.AsyncFileHandler.level/i 4host-manager.org.apache.juli.FileHandler.rotatable = false' /opt/atlassian/confluence/conf/logging.properties

# modify the server.xml template to include a parameterized valve timeout
RUN sed -i '/org.apache.catalina.valves.StuckThreadDetectionValve/{N;s/threshold=".*"/threshold="{{ atl_tomcat_stuck_thread_detection_valve_timeout | default('"'"'60'"'"') }}"/}' \
       ${ATLASSIAN_INSTALL_DIR}/etc/server.xml.j2 && \
       sed -i '/redirectPort=/i debug="0"' ${ATLASSIAN_INSTALL_DIR}/etc/server.xml.j2 && \
       sed -i '/redirectPort=/i URIEncoding="UTF-8"' ${ATLASSIAN_INSTALL_DIR}/etc/server.xml.j2

RUN chown -R 2002:2002 ${CONFLUENCE_HOME}

# Atlassian's gen_cfg and our gen_cfg_no_chown should have the same signature
# Fail the build if that's not the case
COPY bin/check_signatures.sh /
RUN chmod +x /check_signatures.sh && /check_signatures.sh

USER 2002

CMD ["/entrypoint.py", "-fg"]
