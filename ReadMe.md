# Docker image for Confluence Server

Based on the Atlassian Confluence image, this image can be used to run the Confluence service in a non-root container.

On top of the variables supported by the [base image](https://hub.docker.com/r/atlassian/confluence-server), the following are also supported:

* `ATL_TOMCAT_STUCK_THREAD_DETECTION_VALVE_TIMEOUT`: Timeout for detecting stuck threads. Defaults to 60s.

The images gets the various Confluence logs redirected to stdout for easier logging with Kubernetes, etc

Maitained by the ACP team
