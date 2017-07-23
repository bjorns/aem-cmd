# Developer Manual

This is the developer manual for aem-cmd. It should cover what you need
to get started developing the core packages.

## Requirements

### Install OS level packages

Most development of this package has been performed on macOS. As such, any
required packages have been installed via the [Homebrew](https://brew.sh)
package manager.

The recommended command to install homebrew is the following:

    $ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

After installing homebrew, install the latest python packages

    $ brew install python2 python3

Homebrew will install binaries under /usr/local/bin. Make sure this path
is added to your PATH environment variable.

Next, macOS for licensing reasons does not install a fresh version of bash.
Correct this with bash4.

    $ brew install bash

### Install Python Requirements

aem-cmd runs on both python2 and python3. Because of this you will need to
install dependencies with both

    $ pip install -r requirements.txt
    $ pip3 install -r requirements.txt

If you develop multiple python projects, consider using virtualenv before
installing these packages.

## GNU Make

The project uses GNU Make to collect common actions during development. Make
is installed by default on macOS but may need to be installed on e.g. a linux
system.

See Makefile for details.

## Releasing

### Set a version

Before releasing, take care to set a correct version. The version is set in the
file acmd/__init__.py. e.g.

    __version__ = '0.13.0b'

The system uses the [LooseVersion](http://www.programcreek.com/python/example/6084/distutils.version.LooseVersion)
interface to parse the version string.

### Build and release

To build a release package use make.

    $ make clean dist

The release task pushes the release to the python package index (pypi).

    $ make release
