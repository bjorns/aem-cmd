#!/usr/bin/env bash
set -e

function install_pip() {
    local pip_url="https://bootstrap.pypa.io/get-pip.py"

    if [ "$(which pip)" == "" ]; then
        (>&2 echo "Installing pip from $pip_url")

        curl --silent --show-error "$pip_url" | sudo python2.7
    fi
}

function install_pkg() {
    local pkg="$1"

    (>&2 echo "Installing $pkg from pypi")
    sudo pip install --upgrade $pkg
}

function install_acmd() {
    install_pip
    install_pkg requests
    install_pkg requests_toolbelt
    install_pkg aem-cmd

    # Install bash completions
    sudo acmd install_bash_completion
}

install_acmd
