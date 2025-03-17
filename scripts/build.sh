#!/usr/bin/env bash
#
# ZMK Firmware Build Script
# -------------------------
# Automates building ZMK firmware for keyboards with Docker or local environments

# Default configuration
DEFAULT_ZEPHYR_VERSION="3.5"
DEFAULT_LOG_DIR="/tmp"
DEFAULT_HOST_ZMK_DIR="/mnt/storage_ssd/Programming/zmk"
DEFAULT_HOST_CONFIG_DIR="/mnt/storage_ssd/Programming/zmk_ferris_sweep"
DEFAULT_EXTRA_MODULES="/mnt/storage_ssd/Programming/zmk_modules/zmk-adaptive-key"

# Initialize configuration with defaults
ZEPHYR_VERSION=""
RUNWITH_DOCKER=""
LOG_DIR=""
HOST_ZMK_DIR=""
HOST_CONFIG_DIR=""
BOARDS=""
CLEAR_CACHE=""
SUDO=""
WEST_OPTS=""
EXTRA_MODULES=""

# Function to display usage information
show_usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]
Build ZMK firmware for specified keyboards.

Options:
  -s, --su               Use sudo for Docker commands
  -l, --local            Build locally instead of using Docker
  -c, --clear-cache      Clear Docker cache volumes before building
  -b, --board BOARDS     Comma or space separated list of boards (use quotes if space separated)
                         Format as "board:shield" or just "board" (shield defaults to board)
                         If omitted, will compile list of boards from build.yaml
  -v, --version VER      Zephyr version to use (default: $DEFAULT_ZEPHYR_VERSION)
  -o, --output-dir DIR   Directory to save firmware files (default: $DEFAULT_OUTPUT_DIR)
  --log-dir DIR          Directory to save build logs (default: $DEFAULT_LOG_DIR)
  --host-config-dir DIR  Local ZMK config directory (default: $DEFAULT_HOST_CONFIG_DIR)
  --host-zmk-dir DIR     Local ZMK source directory (default: $DEFAULT_HOST_ZMK_DIR)
  --extra-modules PATHS  Semicolon-separated paths to external ZMK modules
  --                     Pass remaining options directly to west build
EOF
  exit 1
}

# Parse command-line arguments
parse_arguments() {
  while [[ $# -gt 0 ]]; do
    case $1 in
    -s | --su)
      SUDO="sudo"
      ;;
    -l | --local)
      RUNWITH_DOCKER="false"
      ;;
    -c | --clear-cache)
      CLEAR_CACHE="true"
      ;;
    -b | --board)
      BOARDS="$2"
      shift
      ;;
    -v | --version)
      ZEPHYR_VERSION="$2"
      shift
      ;;
    --log-dir)
      LOG_DIR="$2"
      shift
      ;;
    --host-config-dir)
      HOST_CONFIG_DIR="$2"
      shift
      ;;
    --host-zmk-dir)
      HOST_ZMK_DIR="$2"
      shift
      ;;
    --extra-modules)
      EXTRA_MODULES="$2"
      shift
      ;;
    -h | --help)
      show_usage
      ;;
    --)
      WEST_OPTS="${@:2}"
      break
      ;;
    *)
      echo "Unknown option $1"
      show_usage
      ;;
    esac
    shift
  done
}

# Apply default values for unset variables
apply_defaults() {
  [[ -z $ZEPHYR_VERSION ]] && ZEPHYR_VERSION="$DEFAULT_ZEPHYR_VERSION"
  [[ -z $RUNWITH_DOCKER ]] && RUNWITH_DOCKER="true"
  [[ -z $LOG_DIR ]] && LOG_DIR="$DEFAULT_LOG_DIR"
  [[ -z $HOST_ZMK_DIR ]] && HOST_ZMK_DIR="$DEFAULT_HOST_ZMK_DIR"
  [[ -z $HOST_CONFIG_DIR ]] && HOST_CONFIG_DIR="$DEFAULT_HOST_CONFIG_DIR"
  [[ -z $CLEAR_CACHE ]] && CLEAR_CACHE="false"
  [[ -z $EXTRA_MODULES ]] && EXTRA_MODULES="$DEFAULT_EXTRA_MODULES"

  # Auto-detect boards from build.yaml if not specified
  if [[ -z $BOARDS ]]; then
    BOARDS=$(awk '
      BEGIN { FS=": " }
      /^[[:space:]]*-[[:space:]]*board:/ { board = $2 }
      /^[[:space:]]*shield:/ { shield = $2; print board ":" shield }
    ' "$HOST_CONFIG_DIR/build.yaml")
  fi
}

# Update config options based on combo usage
update_combo_config() {
  local config_dir="$1"
  if [[ ! -f "$config_dir/features/combos.dtsi" ]]; then
    return
  fi

  echo "Updating combo configuration settings..."
  local combo_keys
  combo_keys=$(grep -Eo '[LR][TMBLRH][01234PRMICLR]' "$config_dir/features/combos.dtsi" | sort | uniq)

  # Exit if no combos are detected
  if [[ -z "$combo_keys" ]]; then
    echo "  No combos detected. Skipping update."
    return
  fi

  # Update maximum combos per key
  local max_combos_per_key=$(
    tail -n +1 "$config_dir/features/combos.dtsi" |
      grep -Eo '[LR][TMBLRH][01234PRMICLR]' |
      sort | uniq -c | sort -nr |
      awk 'NR==1{print $1}'
  )
  sed -Ei "/CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY/s/=.+/=$max_combos_per_key/" "$config_dir"/*.conf
  echo "  Setting MAX_COMBOS_PER_KEY to $max_combos_per_key"

  # Update maximum keys per combo
  local max_keys_per_combo=$(
    tail -n +1 "$config_dir/features/combos.dtsi" |
      grep -o -n '[LR][TMBLRH][01234PRMICLR]' |
      cut -d : -f 1 | uniq -c | sort -nr |
      awk 'NR==1{print $1}'
  )
  sed -Ei "/CONFIG_ZMK_COMBO_MAX_KEYS_PER_COMBO/s/=.+/=$max_keys_per_combo/" "$config_dir"/*.conf
  echo "  Setting MAX_KEYS_PER_COMBO to $max_keys_per_combo"
}

# Setup Docker environment and create Docker command
setup_docker() {
  echo "Build mode: docker"
  DOCKER_IMG="zmkfirmware/zmk-dev-arm:$ZEPHYR_VERSION"
  DOCKER_ZMK_DIR="/workspace/zmk"
  DOCKER_CONFIG_DIR="/workspace/zmk-config"

  # Handle external modules in Docker
  DOCKER_MODULES_MOUNTS=""
  DOCKER_MODULES_PATHS=""

  if [[ -n "$EXTRA_MODULES" ]]; then
    local counter=1
    IFS=';' read -ra MODULE_PATHS <<<"$EXTRA_MODULES"

    for module_path in "${MODULE_PATHS[@]}"; do
      # Trim whitespace
      module_path=$(echo "$module_path" | xargs)

      if [[ -n "$module_path" ]]; then
        local module_name=$(basename "$module_path")
        local docker_module_path="/workspace/modules/$module_name"

        # Add mount for this module
        DOCKER_MODULES_MOUNTS+=" --mount type=bind,source=$module_path,target=$docker_module_path"

        # Add path to the Docker modules list
        [[ -n "$DOCKER_MODULES_PATHS" ]] && DOCKER_MODULES_PATHS+=';'
        DOCKER_MODULES_PATHS+="$docker_module_path"

        counter=$((counter + 1))
      fi
    done
  fi

  # Create Docker run command with all mounts (binds + volumes for cache)
  DOCKER_CMD="$SUDO docker run --name zmk-$ZEPHYR_VERSION --rm \
        --mount type=bind,source=$HOST_ZMK_DIR,target=$DOCKER_ZMK_DIR \
        --mount type=bind,source=$HOST_CONFIG_DIR,target=$DOCKER_CONFIG_DIR \
        --mount type=volume,source=zmk-root-user-$ZEPHYR_VERSION,target=/root \
        --mount type=volume,source=zmk-zephyr-$ZEPHYR_VERSION,target=$DOCKER_ZMK_DIR/zephyr \
        --mount type=volume,source=zmk-zephyr-modules-$ZEPHYR_VERSION,target=$DOCKER_ZMK_DIR/modules \
        --mount type=volume,source=zmk-zephyr-tools-$ZEPHYR_VERSION,target=$DOCKER_ZMK_DIR/tools \
        $DOCKER_MODULES_MOUNTS"

  # Reset Docker volumes if cache clearing is requested
  if [[ $CLEAR_CACHE = true ]]; then
    echo "Clearing Docker cache volumes..."
    $SUDO docker volume rm $($SUDO docker volume ls -q | grep "^zmk-.*-$ZEPHYR_VERSION$")
  fi

  # Initialize west and update if needed
  echo "[west] Initializing and updating ZMK..."
  OLD_WEST="/root/west.yml.old"
  $DOCKER_CMD -w "$DOCKER_ZMK_DIR" "$DOCKER_IMG" /bin/bash -c " \
        if [[ ! -f .west/config ]]; then \
            echo 'Initializing west...'; \
            west init -l app/; \
        fi \
        && if [[ -f $OLD_WEST ]]; then \
            md5_old=\$(md5sum $OLD_WEST | cut -d' ' -f1); \
        fi \
        && if [[ \$md5_old != \$(md5sum app/west.yml | cut -d' ' -f1) ]]; then \
            echo 'Updating west modules...'; \
            west update; \
            cp app/west.yml $OLD_WEST; \
        else \
            echo 'ZMK is up to date'; \
        fi"

  # Set build prefix and suffix for docker mode
  DOCKER_PREFIX="$DOCKER_CMD -w $DOCKER_ZMK_DIR/app $DOCKER_IMG"
  BUILD_SUFFIX="${ZEPHYR_VERSION}_docker"
  CONFIG_DIR="$DOCKER_CONFIG_DIR/config"

  # Update EXTRA_MODULES to use Docker paths
  if [[ -n "$DOCKER_MODULES_PATHS" ]]; then
    EXTRA_MODULES="$DOCKER_MODULES_PATHS"
  fi
}

# Setup for local build environment
setup_local() {
  echo "Build mode: local"
  DOCKER_PREFIX=""
  BUILD_SUFFIX="${ZEPHYR_VERSION}"
  CONFIG_DIR="$HOST_CONFIG_DIR/config"
}

# Build firmware for a single board-shield pair
compile_board() {
  local board="$1"
  local shield="$2"
  local build_dir="${board}_${shield}_$BUILD_SUFFIX"
  local logfile="$LOG_DIR/zmk_build_${board}_${shield}.log"

  # Prepare build command with extra modules if provided
  local modules_cmd=""
  if [[ -n "$EXTRA_MODULES" ]]; then
    modules_cmd="-DZMK_EXTRA_MODULES=\"$EXTRA_MODULES\""
  fi

  local build_cmd="$DOCKER_PREFIX west build -d \"build/$build_dir\" -b \"$board\" $WEST_OPTS -- -DSHIELD=\"${shield}\" -DZMK_CONFIG=\"$CONFIG_DIR\" $modules_cmd -Wno-dev"

  echo -e "\n\033[0;32mBuilding $board:$shield... \033[0m"
  echo "Executing: $build_cmd"

  eval $build_cmd >"$logfile" 2>&1

  if [[ $? -eq 0 ]]; then
    echo -e "\033[0;32mdone\033[0m"
    echo "Build log saved to \"$logfile\"."

    # Determine firmware file type and copy to output location
    if [[ -f "$HOST_ZMK_DIR/app/build/$build_dir/zephyr/zmk.uf2" ]]; then
      TYPE="uf2"
    else
      TYPE="bin"
    fi

    OUTPUT="$HOST_CONFIG_DIR/build/${board}_${shield}-zmk.$TYPE"
    mkdir -p "$(dirname "$OUTPUT")"

    # Backup existing file if it's not a symlink
    [[ -f "$OUTPUT" ]] && [[ ! -L "$OUTPUT" ]] && mv "$OUTPUT" "$OUTPUT.bak"

    # Copy the firmware file
    cp "$HOST_ZMK_DIR/app/build/$build_dir/zephyr/zmk.$TYPE" "$OUTPUT"
    echo "Firmware saved to $OUTPUT"
  else
    echo -e "\n\033[0;31mError: $board:$shield build failed\033[0m"
    echo "Check the log file for details: $logfile"
    cat "$logfile" | tail -n 20
  fi
}

# Main function to orchestrate the build process
main() {
  parse_arguments "$@"
  apply_defaults

  echo "ZMK Build Script"
  echo "----------------"

  # Update configuration based on combo usage
  cd "$HOST_CONFIG_DIR"
  update_combo_config "$HOST_CONFIG_DIR/config"

  # Set up build environment (Docker or local)
  if [[ $RUNWITH_DOCKER = true ]]; then
    setup_docker
  else
    setup_local
  fi

  # Build firmware for each board-shield pair
  cd "$HOST_ZMK_DIR/app"
  echo "----------------"
  echo "CONFIG_DIR: $CONFIG_DIR"

  # Display extra modules if any
  if [[ -n "$EXTRA_MODULES" ]]; then
    echo "Using extra modules: $EXTRA_MODULES"
  fi

  echo "Building firmware for board:shield pairs: $(echo $BOARDS | tr '\n' ' ')"

  # Split entries on newlines, spaces, commas, or tabs
  mapfile -t entries <<<"$BOARDS"
  for entry in "${entries[@]}"; do
    # Skip empty entries caused by multiple delimiters
    [[ -z "$entry" ]] && continue

    IFS=':' read -r board shield <<<"$entry"
    shield=${shield:-$board} # Default shield to board if not specified

    compile_board "$board" "$shield"
  done

  echo -e "\n\033[0;32mBuild process completed!\033[0m"
}

main "$@"
