FROM atlassian/confluence-server:6.15.6-adoptopenjdk8

# The id of the confluence user is 2002
RUN chown -R 2002:2002 /opt/atlassian/confluence
