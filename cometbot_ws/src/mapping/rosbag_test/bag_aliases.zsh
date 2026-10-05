# Mac-side wrappers: run the bag_aliases.sh commands inside the CAN devcontainer.
# Source from ~/.zshrc:
#   source ~/Documents/CAN/cometbot_ws/src/mapping/rosbag_test/bag_aliases.zsh

_can_container() {
  local id
  id=$(docker ps -aq --filter "label=devcontainer.local_folder=$HOME/Documents/CAN" | head -1)
  if [[ -z $id ]]; then
    echo "CAN devcontainer not found; open ~/Documents/CAN in VS Code and Reopen in Container" >&2
    return 1
  fi
  docker start "$id" >/dev/null && echo "$id"
}

_can_run() {
  local id
  id=$(_can_container) || return 1
  docker exec -it -u vscode "$id" bash -ic "$*"
}

rtab()     { _can_run rtab "$@" }
fox()      { _can_run fox "$@" }
bagplay()  { _can_run bagplay "$@" }
bagreset() { _can_run bagreset "$@" }
