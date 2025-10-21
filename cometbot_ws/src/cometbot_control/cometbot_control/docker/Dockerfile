FROM ros:humble-ros-base

# Install python deps and utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip python3-argcomplete \
    && rm -rf /var/lib/apt/lists/*

# Copy package code into image
WORKDIR /opt/cometbot_control
COPY .. /opt/cometbot_control

# Install Python requirements
RUN pip3 install --no-cache-dir -r /opt/cometbot_control/docker/requirements.txt

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/opt/cometbot_control/docker/entrypoint.sh"]
