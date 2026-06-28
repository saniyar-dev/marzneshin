#!/usr/bin/env bash
set -e

APP_NAME="fishy"
NODE_NAME="marznode"
CONFIG_DIR="/etc/opt/$APP_NAME"
DATA_DIR="/var/lib/$APP_NAME"
NODE_DATA_DIR="/var/lib/$NODE_NAME"
COMPOSE_FILE="$CONFIG_DIR/docker-compose.yml"

FETCH_REPO="fishy/fishy"
SCRIPT_URL="https://github.com/$FETCH_REPO/raw/master/script.sh"

colorized_echo() {
    local color=$1
    local text=$2

    case $color in
        "red")
        printf "\e[91m${text}\e[0m\n";;
        "green")
        printf "\e[92m${text}\e[0m\n";;
        "yellow")
        printf "\e[93m${text}\e[0m\n";;
        "blue")
        printf "\e[94m${text}\e[0m\n";;
        "magenta")
        printf "\e[95m${text}\e[0m\n";;
        "cyan")
        printf "\e[96m${text}\e[0m\n";;
        *)
            echo "${text}"
        ;;
    esac
}

check_running_as_root() {
    if [ "$(id -u)" != "0" ]; then
        colorized_echo red "This command must be run as root."
        exit 1
    fi
}

detect_os() {
    # Detect the operating system
    if [ -f /etc/lsb-release ]; then
        OS=$(lsb_release -si)
        elif [ -f /etc/os-release ]; then
        OS=$(awk -F= '/^NAME/{print $2}' /etc/os-release | tr -d '"')
        elif [ -f /etc/redhat-release ]; then
        OS=$(cat /etc/redhat-release | awk '{print $1}')
        elif [ -f /etc/arch-release ]; then
        OS="Arch"
    else
        colorized_echo red "Unsupported operating system"
        exit 1
    fi
}

detect_and_update_package_manager() {
    colorized_echo blue "Updating package manager"
    if [[ "$OS" == "Ubuntu"* ]] || [[ "$OS" == "Debian"* ]]; then
        PKG_MANAGER="apt-get"
        $PKG_MANAGER update
        elif [[ "$OS" == "CentOS"* ]] || [[ "$OS" == "AlmaLinux"* ]]; then
        PKG_MANAGER="yum"
        $PKG_MANAGER update -y
        $PKG_MANAGER install -y epel-release
        elif [ "$OS" == "Fedora"* ]; then
        PKG_MANAGER="dnf"
        $PKG_MANAGER update
        elif [ "$OS" == "Arch" ]; then
        PKG_MANAGER="pacman"
        $PKG_MANAGER -Sy
    else
        colorized_echo red "Unsupported operating system"
        exit 1
    fi
}

detect_compose() {
    # Check if docker compose command exists
    if docker compose >/dev/null 2>&1; then
        COMPOSE='docker compose'
        elif docker-compose >/dev/null 2>&1; then
        COMPOSE='docker-compose'
    else
        colorized_echo red "docker compose not found"
        exit 1
    fi
}

install_package () {
    if [ -z $PKG_MANAGER ]; then
        detect_and_update_package_manager
    fi

    PACKAGE=$1
    colorized_echo blue "Installing $PACKAGE"
    if [[ "$OS" == "Ubuntu"* ]] || [[ "$OS" == "Debian"* ]]; then
        $PKG_MANAGER -y install "$PACKAGE"
        elif [[ "$OS" == "CentOS"* ]] || [[ "$OS" == "AlmaLinux"* ]]; then
        $PKG_MANAGER install -y "$PACKAGE"
        elif [ "$OS" == "Fedora"* ]; then
        $PKG_MANAGER install -y "$PACKAGE"
        elif [ "$OS" == "Arch" ]; then
        $PKG_MANAGER -S --noconfirm "$PACKAGE"
    else
        colorized_echo red "Unsupported operating system"
        exit 1
    fi
}

install_docker() {
    # Install Docker and Docker Compose using the official installation script
    colorized_echo blue "Installing Docker"
    curl -fsSL https://get.docker.com | sh
    colorized_echo green "Docker installed successfully"
}

install_fishy_script() {
    colorized_echo blue "Installing fishy script"
    curl -sSL $SCRIPT_URL | install -m 755 /dev/stdin /usr/local/bin/fishy
    colorized_echo green "fishy script installed successfully"
}

install_fishy() {
    # Fetch releases
    FILES_URL_PREFIX="https://raw.githubusercontent.com/fishy/fishy/master"
	COMPOSE_FILES_URL="https://raw.githubusercontent.com/fishy/fishy-deploy/master"
 	database=$1
  	nightly=$2
  
    mkdir -p "$DATA_DIR"
    mkdir -p "$CONFIG_DIR"

    colorized_echo blue "Fetching compose file"
    curl -sL "$COMPOSE_FILES_URL/docker-compose-$database.yml" -o "$CONFIG_DIR/docker-compose.yml"
    colorized_echo green "File saved in $CONFIG_DIR/docker-compose.yml"
	if [ "$nightly" = true ]; then
	    colorized_echo red "setting compose tag to nightly."
	 	sed -ri "s/(dawsh\/fishy:)latest/\1nightly/g" $CONFIG_DIR/docker-compose.yml
	fi
 
    colorized_echo blue "Fetching example .env file"
    curl -sL "$FILES_URL_PREFIX/.env.example" -o "$CONFIG_DIR/.env"
    colorized_echo green "File saved in $CONFIG_DIR/.env"

    colorized_echo green "Fishy Service files downloaded successfully"
}

install_marznode_xray_config() {
    mkdir -p "$NODE_DATA_DIR"
    curl -sL "https://raw.githubusercontent.com/fishy/marznode/master/xray_config.json" -o "$NODE_DATA_DIR/xray_config.json"
    colorized_echo green "Sample xray config downloaded for marznode"
}

uninstall_fishy_script() {
    if [ -f "/usr/local/bin/fishy" ]; then
        colorized_echo yellow "Removing fishy script"
        rm "/usr/local/bin/fishy"
    fi
}

uninstall_fishy() {
    if [ -d "$CONFIG_DIR" ]; then
        colorized_echo yellow "Removing directory: $CONFIG_DIR"
        rm -r "$CONFIG_DIR"
    fi
}

uninstall_fishy_docker_images() {
    images=$(docker images | grep fishy | awk '{print $3}')

    if [ -n "$images" ]; then
        colorized_echo yellow "Removing Docker images of Fishy Service"
        for image in $images; do
            if docker rmi "$image" >/dev/null 2>&1; then
                colorized_echo yellow "Image $image removed"
            fi
        done
    fi
}

uninstall_fishy_data_files() {
    if [ -d "$DATA_DIR" ]; then
        colorized_echo yellow "Removing directory: $DATA_DIR"
        rm -r "$DATA_DIR"
    fi
}

uninstall_marznode_data_files() {
    if [ -d "$NODE_DATA_DIR" ]; then
        colorized_echo yellow "Removing directory: $NODE_DATA_DIR"
        rm -r "$NODE_DATA_DIR"
    fi
}


up_fishy() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" up -d --remove-orphans
}

down_fishy() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" down
}

show_fishy_logs() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" logs
}

follow_fishy_logs() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" logs -f
}

fishy_cli() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" exec -e CLI_PROG_NAME="fishy cli" fishy /app/fishy-cli.py "$@"
}


update_fishy_script() {
    colorized_echo blue "Updating fishy script"
    curl -sSL $SCRIPT_URL | install -m 755 /dev/stdin /usr/local/bin/fishy
    colorized_echo green "fishy script updated successfully"
}

update_fishy() {
    $COMPOSE -f $COMPOSE_FILE -p "$APP_NAME" pull
}

is_fishy_installed() {
    if [ -d $CONFIG_DIR ]; then
        return 0
    else
        return 1
    fi
}

is_fishy_up() {
    if [ -z "$($COMPOSE -f $COMPOSE_FILE ps -q -a)" ]; then
        return 1
    else
        return 0
    fi
}

install_command() {
    check_running_as_root
    # Check if fishy is already installed
    if is_fishy_installed; then
        colorized_echo red "Fishy Service is already installed at $CONFIG_DIR"
        read -p "Do you want to override the previous installation? (y/n) "
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            colorized_echo red "Aborted installation"
            exit 1
        fi
    fi
    detect_os
    if ! command -v jq >/dev/null 2>&1; then
        install_package jq
    fi
    if ! command -v curl >/dev/null 2>&1; then
        install_package curl
    fi
    if ! command -v docker >/dev/null 2>&1; then
        install_docker
    fi
	
    database="sqlite"
	nightly=false
 
	while [[ "$#" -gt 0 ]]; do
	    case $1 in
	        -d|--database)
		 		database="$2"
				if [[ ! $database =~ ^(sqlite|mariadb|mysql)$ ]]; then
				    echo "database could only be sqlite, mysql and mariadb."
					exit 1
				fi
	            shift
	            ;;
			-n|--nightly)
	            nightly=true
	            ;;
	        *)
	            echo "Unknown option: $1"
	            exit 1
	            ;;
	    esac
	    shift
	done

    detect_compose
    install_fishy_script
    install_fishy $database $nightly
    install_marznode_xray_config
    up_fishy
    follow_fishy_logs
}

uninstall_command() {
    check_running_as_root
    # Check if fishy is installed
    if ! is_fishy_installed; then
        colorized_echo red "Fishy Service's not installed!"
        exit 1
    fi

    read -p "Do you really want to uninstall Fishy Service? (y/n) "
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        colorized_echo red "Aborted"
        exit 1
    fi

    detect_compose
    if is_fishy_up; then
        down_fishy
    fi
    uninstall_fishy_script
    uninstall_fishy
    uninstall_fishy_docker_images

    read -p "Do you want to remove fishy & marznode data files too ($NODE_DATA_DIR, $DATA_DIR)? (y/n) "
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        colorized_echo green "Fishy Service uninstalled successfully"
    else
        uninstall_fishy_data_files
	uninstall_marznode_data_files
        colorized_echo green "Fishy Service uninstalled successfully"
    fi
}

up_command() {
    help() {
        colorized_echo red "Usage: $0 up [options]"
        echo ""
        echo "OPTIONS:"
        echo "  -h, --help        display this help message"
        echo "  -n, --no-logs     do not follow logs after starting"
    }

    local no_logs=false
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            -n|--no-logs)
                no_logs=true
            ;;
            -h|--help)
                help
                exit 0
            ;;
            *)
                echo "Error: Invalid option: $1" >&2
                help
                exit 0
            ;;
        esac
        shift
    done

    # Check if fishy is installed
    if ! is_fishy_installed; then
        colorized_echo red "Fishy Service is not installed!"
        exit 1
    fi

    detect_compose

    if is_fishy_up; then
        colorized_echo red "Fishy Service is already up"
        exit 1
    fi

    up_fishy
    if [ "$no_logs" = false ]; then
        follow_fishy_logs
    fi
}

down_command() {

    # Check if fishy is installed
    if ! is_fishy_installed; then
        colorized_echo red "Fishy Service's not installed!"
        exit 1
    fi

    detect_compose

    if ! is_fishy_up; then
        colorized_echo red "Fishy Service's already down"
        exit 1
    fi

    down_fishy
}

restart_command() {
    help() {
        colorized_echo red "Usage: $0 restart [options]"
        echo
        echo "OPTIONS:"
        echo "  -h, --help        display this help message"
        echo "  -n, --no-logs     do not follow logs after starting"
    }

    local no_logs=false
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            -n|--no-logs)
                no_logs=true
            ;;
            -h|--help)
                help
                exit 0
            ;;
            *)
                echo "Error: Invalid option: $1" >&2
                help
                exit 0
            ;;
        esac
        shift
    done

    # Check if fishy is installed
    if ! is_fishy_installed; then
        colorized_echo red "Fishy Service's not installed!"
        exit 1
    fi

    detect_compose

    down_fishy
    up_fishy
    if [ "$no_logs" = false ]; then
        follow_fishy_logs
    fi
}

status_command() {

    # Check if fishy is installed
    if ! is_fishy_installed; then
        echo -n "Status: "
        colorized_echo red "Not Installed"
        exit 1
    fi

    detect_compose

    if ! is_fishy_up; then
        echo -n "Status: "
        colorized_echo blue "Down"
        exit 1
    fi

    echo -n "Status: "
    colorized_echo green "Up"

    json=$($COMPOSE -f $COMPOSE_FILE ps -a --format=json)
    services=$(echo "$json" | jq -r 'if type == "array" then .[] else . end | .Service')
    states=$(echo "$json" | jq -r 'if type == "array" then .[] else . end | .State')
    # Print out the service names and statuses
    for i in $(seq 0 $(expr $(echo $services | wc -w) - 1)); do
        service=$(echo $services | cut -d' ' -f $(expr $i + 1))
        state=$(echo $states | cut -d' ' -f $(expr $i + 1))
        echo -n "- $service: "
        if [ "$state" == "running" ]; then
            colorized_echo green $state
        else
            colorized_echo red $state
        fi
    done
}

logs_command() {
    help() {
        colorized_echo red "Usage: fishy logs [options]"
        echo ""
        echo "OPTIONS:"
        echo "  -h, --help        display this help message"
        echo "  -n, --no-follow   do not show follow logs"
    }

    local no_follow=false
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            -n|--no-follow)
                no_follow=true
            ;;
            -h|--help)
                help
                exit 0
            ;;
            *)
                echo "Error: Invalid option: $1" >&2
                help
                exit 0
            ;;
        esac
        shift
    done

    # Check if fishy is installed
    if ! is_fishy_installed; then
        colorized_echo red "Fishy Service is not installed!"
        exit 1
    fi

    detect_compose

    if ! is_fishy_up; then
        colorized_echo red "Fishy Service is not up."
        exit 1
    fi

    if [ "$no_follow" = true ]; then
        show_fishy_logs
    else
        follow_fishy_logs
    fi
}

cli_command() {
    # Check if fishy is installed
    if ! is_fishy_installed; then
        colorized_echo red "Fishy Service is not installed!"
        exit 1
    fi

    detect_compose

    if ! is_fishy_up; then
        colorized_echo red "Fishy Service is not up."
        exit 1
    fi

    fishy_cli "$@"
}

update_command() {
    check_running_as_root
    # Check if fishy is installed
    if ! is_fishy_installed; then
        colorized_echo red "Fishy Service is not installed!"
        exit 1
    fi

    detect_compose

    update_fishy_script
    colorized_echo blue "Pulling latest version"
    update_fishy

    colorized_echo blue "Restarting Fishy Service's services"
    down_fishy
    up_fishy

    colorized_echo blue "Fishy Service updated successfully"
}


usage() {
    colorized_echo red "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  up              Start services"
    echo "  down            Stop services"
    echo "  restart         Restart services"
    echo "  status          Show status"
    echo "  logs            Show logs"
    echo "  cli             Fishy Service command-line interface"
    echo "  install         Install Fishy Service"
    echo "  update          Update latest version"
    echo "  uninstall       Uninstall Fishy Service"
    echo "  install-script  Install Fishy Service script"
    echo
}

case "$1" in
    up)
    shift; up_command "$@";;
    down)
    shift; down_command "$@";;
    restart)
    shift; restart_command "$@";;
    status)
    shift; status_command "$@";;
    logs)
    shift; logs_command "$@";;
    cli)
    shift; cli_command "$@";;
    install)
    shift; install_command "$@";;
    update)
    shift; update_command "$@";;
    uninstall)
    shift; uninstall_command "$@";;
    install-script)
    shift; install_fishy_script "$@";;
    *)
    usage;;
esac
