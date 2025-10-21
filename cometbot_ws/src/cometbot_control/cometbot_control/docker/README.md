Excavator Docker quickstart

Build the Docker image from the package root (this Dockerfile expects the
package contents to be available at build time):

  docker build -t cometbot_excavator -f cometbot_control/docker/Dockerfile .

Run the node (the image uses the ROS 2 Humble base image):

  docker run --rm --name excavator_node cometbot_excavator

Notes:
- The base image provides the ROS 2 runtime (rclpy, std_msgs). If you need
  additional Python packages, add them to docker/requirements.txt.
- For integration testing with a host ROS 2 environment, consider running
  the container with network=host and sourcing the same ROS_DOMAIN_ID.
