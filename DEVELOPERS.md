# Developer Manual

This is the developer manual for aem-cmd. It should cover what you need
to get started developing the core packages.

## Requirements

### Install OS level packages

Most development of this package has been performed on macOS. As such, any
required packages have been installed via the [Homebrew](https://brew.sh)
package manager.

The recommended command to install homebrew is the following:

    $ /usr/bin/ruby -e \
        "$(curl -fsSL \
        https://raw.githubusercontent.com/Homebrew/install/master/install)"

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

## Building

### Developer install

To connect the default acmd command to your local project code

    $ cd ~/projects/aem-cmd
    $ pip install -e .
    $ acmd --version
    0.13.1b

Now, wherever you run acmd from it will use the code within your project. Note
that this may cause issues if you are simultaneously working and something
breaks. A different approach is to only install released versions from pypi
and use the local binary for testing development code

    $ pip uninstall aem-cmd
    $ pip install aem-cmd
    $ cd ~/projects/aem-cmd
    $ ./bin/acmd --version
    0.13.1b
    $ acmd --version
    0.13.0





### GNU Make

The project uses GNU Make to collect common actions during development. Make
is installed by default on macOS but may need to be installed on e.g. a linux
system.

See Makefile for details.

## Releasing

### Set a version

Before releasing, take care to set a correct version. The version is set in the
file acmd/\_\_init\_\_.py. e.g.

    __version__ = '0.13.0b'

The system uses the [LooseVersion](http://www.programcreek.com/python/example/6084/distutils.version.LooseVersion)
interface to parse the version string.

### Build and release

To build a release package use make.

    $ make clean dist

The release task pushes the release to the python package index (pypi).

    $ make release

## Architecture

### Guidelines

* aem-cmd is built to last
* aem-cmd is built using modern idiomatic python
* aem-cmd may be used on system without sudo access, it must still work.
* The code was fun to write, it should be fun to read

### System Initialization

The system is build around a general purpose command line parsing together with
a set of loosely coupled tools. The main initialization flow goes something
like this:

* Find and read the main config file .acmd.rc in the users home dir.
* Load all the default tools from the main tool repository
* Load any plugin tool repositories from teh config file.
* Parse the main command line, find out what server is being read.
* Load the tool requested by the user.
* Call the tool with the selected server as well as any excess command line
    arguments.


### Tool loading

The system uses the decorator class `acmd.repo.tool` to mark classes as tool.
The decorator, when the class or module is loaded, takes the class object, instantiates it and stores in a dict in the `acmd.repo.ToolRepo` object
with the tool name as a key.

Because of this loading the built in tools is simply a matter of loading
all modules in the acmd/tools directory using the standard library
importlib utility.

The plugin tools likewise can be loaded using the directory path given in the
project specification in the _.acmd.rc_ file.

## Thanks

Thanks to everyone who has supported this project, including developers
of dependencies and python itself.
