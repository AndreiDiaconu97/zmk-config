#!/bin/bash

## REFERENCE COMMAND ##
# west build -b nice_nano_v2 -d build/left -- -DSHIELD=cradio_left -DZMK_CONFIG="/workspaces/zmk-config/config"

BOARD="nice_nano_v2"
SHIELD="cradio"
SIDES="left right"

readonly ORIGINAL_PATH="$(pwd)"
ZMK_DIR="/workspaces/zmk/app"
CONF_DIR="/workspaces/zmk-config"
OUT_DIR="${CONF_DIR}/build/artifacts"
LOG_DIR="${CONF_DIR}/build/logs"

# Parse input arguments
while [[ $# -gt 0 ]]; do
  case $1 in
  -c | --clear-cache)
    CLEAR_CACHE="true"
    ;;

  # comma or space separated list of boards (use quotes if space separated)
  # if ommitted, will compile list of boards in build.yaml
  -b | --board)
    BOARD="$2"
    shift
    ;;

  -s | --sides)
    SIDES="$2"
    shift
    ;;

  --conf-dir)
    CONF_DIR="$2"
    shift
    ;;

  --zmk-dir)
    ZMK_DIR="$2"
    shift
    ;;

  --out-dir)
    OUT_DIR="$2"
    shift
    ;;

  --log-dir)
    LOG_DIR="$2"
    shift
    ;;

  --)
    WEST_OPTS=($2)
    break
    ;;

  *)
    echo "Unknown option $1"
    exit 1
    ;;

  esac
  shift
done

build_board() {
  local side="$1"
  local shield="${SHIELD}_${side}"
  local logfile="${LOG_DIR}/zmk_build_${shield}.log"

  printf "\e[32mBuilding %s...\e[0m\n" "$shield"

  if ! west build -b "${BOARD}" -d "build/${side}" "${WEST_OPTS[@]}" \
    -- -DSHIELD="${shield}" -DZMK_CONFIG="${CONF_DIR}/config" \
    -Wno-dev 2>&1 | tee "${logfile}"; then
    printf "\e[31mError: %s failed\e[0m\n" "$shield" >&2
    return 1
  fi
}

archive_board() {
  local side="$1"
  local artifact="${SHIELD}_${side}-${BOARD}-zmk.uf2"

  printf "\e[32mArchiving %s...\e[0m\n" "$artifact"
  [ -f build/${side}/zephyr/zmk.uf2 ] && mv build/${side}/zephyr/zmk.uf2 "${OUT_DIR}/${artifact}"
}

build_and_archive() {
  local side="$1"

  build_board "${side}"
  archive_board "${side}"
}

printf "\e[32mStarting ZMK build process...\e[0m\n"
mkdir -p "${OUT_DIR}"
mkdir -p "${LOG_DIR}"
cd "${ZMK_DIR}"

for side in $(echo "${SIDES}" | sed 's/,/ /g'); do
  build_and_archive "${side}"
done

cd "${ORIGINAL_PATH}"
printf "\e[33mZMK build process completed.\e[0m\n"
