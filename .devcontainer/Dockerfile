FROM ros:humble

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000
ARG ROS_DISTRO=humble

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install base packages and developer tools (ROS already present in base image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake ninja-build git wget ca-certificates curl gnupg lsb-release locales tzdata sudo \
    python3 python3-pip python3-venv python3-dev python3-colcon-common-extensions \
    python3-numpy \
    ros-${ROS_DISTRO}-joy \
    ros-${ROS_DISTRO}-joy-linux \
    ros-${ROS_DISTRO}-teleop-twist-joy \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

# Install python tooling
RUN python3 -m pip install --no-cache-dir -U pip \
    && python3 -m pip install --no-cache-dir "setuptools<=58.2.0" numpy \
    && python3 -m pip install --no-cache-dir -U rosdep colcon-common-extensions platformio

# Initialize rosdep (best-effort)
RUN rosdep init || true && rosdep update || true

# Create non-root user and give sudo
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && usermod -aG sudo $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Add dialout group for serial access
RUN usermod -a -G dialout $USERNAME || true

WORKDIR /workspace
USER $USERNAME

# Setup PlatformIO Python virtualenv required by micro_ros_platformio
RUN mkdir -p /home/${USERNAME}/.platformio \
    && python3 -m venv --system-site-packages /home/${USERNAME}/.platformio/penv \
    && /home/${USERNAME}/.platformio/penv/bin/pip install --no-cache-dir -U pip "setuptools<=58.2.0" platformio numpy

ENV PATH="/home/${USERNAME}/.platformio/penv/bin:/home/${USERNAME}/.local/bin:${PATH}"

CMD [ "sleep", "infinity" ]
