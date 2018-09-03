# AEM Command Line Tools

[![Circle CI](https://circleci.com/gh/bjorns/aem-cmd.svg?style=svg)](https://circleci.com/gh/bjorns/aem-cmd)

AEM command line tools is a toolset package for working with AEM and
the Java Content Repository (JCR) from a shell. Aem-cmd presents a few novel
ideas compared to other aem command line tools:

* *Unix friendly* - By reading and writing plaintext aem-cmd interoperates easily
with common tools such as grep, cut, sed and awk.
* *Concise* - Hostnames and usernames are stored in
config files and mere server aliases are used from the perspective of the user.
* *Battle tested* - Aem-cmd takes care to support standard python deployments and
does not assume the user has super user access to the deployment environment.
* *By developers for developers* - Write your own tools in powerful python and
re-use the configuration framework and api-libs of the aem-cmd system.

## Getting Started

### Installation

#### Quick install

A quick install script is provided for convenience:

    $ curl https://raw.githubusercontent.com/bjorns/aem-cmd/master/get-acmd.sh | bash

Note: The install script requires sudo access.

#### Manual install

For manual install, acmd is available in PyPI.

    $ pip install aem-cmd
    ...
    $ acmd
    Usage: acmd [options] <tool> <args>
    Run 'acmd help' for list of available tools

    Options:
      -h, --help            show this help message and exit
      -s str, --server=str  server name

#### User local install

If you do not have sudo access and your user does not have write access to the
default python paths you can make a user local installation with:

    $ pip install --user aem-cmd

When running this installation directory becomes $(HOME)/.local/bin. Usually
this path is then covered in PATH but it may be necessary to add it to your
.bashrc. A quick install script is available for user installs at

    $ curl https://raw.githubusercontent.com/bjorns/aem-cmd/master/get-acmd-user.sh | bash

#### Bash Completion

aem-cmd comes with a bash completion script but for technical reasons it cannot
be installed by pip so to install it use the install_bash_completion command.

    $ sudo acmd install_bash_completion
    Password:
    Installed bash completion script in /etc/bash_completion.d

Note 1: The bash completion works best in bash 4. Due to licensing issues macOS
still comes with bash 3 by default but it is possible to upgrade. See
[here](http://apple.stackexchange.com/questions/24632/is-it-safe-to-upgrade-bash-via-homebrew).

Note 2: The main quick install script automatically invokes the bash completion
tool.


## Tools

aem-cmd is built around tools. Each tool represents a resource in the system.
Packages, bundles and users each have separate tools for operating on them.
Think of it in terms of REST services. Primarily you interact with a resource,
not an action.

### Help

The help tool lists all installed tools

    $ acmd help
    Available tools:
      inspect
      bundle
      help
      package

To get more information on available actions call help on that tool:

    $ acmd help package
    Usage: acmd package [options] [list|build|install|upload|download] [<zip>|<package>]

    Options:
      -h, --help            show this help message and exit
      -v VERSION, --version=VERSION
                            specify explicit version
      -g GROUP, --group=GROUP
                            specify explicit group
      -r, --raw             output raw response data
      -c, --compact         output only package name
      -i, --install         install package after upload


### JCR tools

The JCR tools are considered so common they are not grouped together but come
as separate commands.

#### List subpaths:

    $ acmd ls /
    index.servlet
    bundle
    rep:policy
    services
    home
    ....

#### List entire subtree:

    $ acmd find /content/catalog
    ...


#### Show node properties:

    $ acmd cat /content
    jcr:primaryType:	sling:OrderedFolder
    jcr:createdBy:	admin
    jcr:mixinTypes:	[u'sling:Redirect', u'mix:lockable', u'rep:AccessControllable']
    sling:target:	/geohome
    sling:resourceType:	sling:redirect
    jcr:created:	Fri Jun 13 2014 14:17:56 GMT-0400

#### Set property

    $ acmd setprop prop=cheese /content/catalog/product4711
    /content/catalog/product4711
    $ acmd cat /content/catalog/product4711
    serial_nbr: 1234
    ...
    prop:   cheese


Multiple properties can be set comma separated. Just quote the values if there
are commas or spaces in the values. Quoting will also force the type to string, otherwise
rudimentary type inference is performed recognizing numbers and booleans.

    $ acmd setprop prop1="I like cheese",prop2="I also like wine" /content/catalog/product4711

The setprop tool also takes paths on stdin. The following line sets the property
on all nodes under /content/catalog

    $ acmd find /content/catalog | acmd setprop prop="I like cheese"

#### Create node

Note that the setprop command will create the path if it does not exist. The
following will create a new folder:

    $ acmd setprop jcr:primaryType=sling:Folder /content/new_folder

#### Delete property

    $ acmd rmprop prop /content/catalog/product4711
    /content/catalog/product4711

Works very similar to setprop, takes multiple paths on stdin and can take
multiple comma separated property names as prop0,prop1,prop2.

#### Search for properties

The search tool uses the AEM query API to find nodes which contain a given property
value.

    $ acmd search serial_nbr=1234
    /content/catalog/product4711

#### Delete node

    $ acmd rm /content/catalog/product4711
    /content/catalog/product4711

The rm tool if given no argument will read node paths from standard input.

    $ acmd find /content/catalog | grep product | acmd rm
    ....



### Packages

The package-tool supports up- and downloading, installing and uninstalling
packages. If you install the bash completion script, package names will be
autocompleted. In addition to autocomplete the tool also automatically finds
group and version of the latest package so only the simple package name needs
to be supplied as argument.

#### List packages

By default the package tool lists all installed packages.

    $ acmd package list
    ...
    day/cq540/product   cq-portlet-director 5.4.38
    day/cq550/product   cq-upgrade-acl  5.5.2
    day/cq560/collab/blog   cq-collab-blog-pkg  5.6.17
    day/cq560/collab/calendar   cq-collab-calendar-pkg  5.6.12
    day/cq560/social/calendar   cq-social-calendar-pkg  1.0.28
    ....

#### Rebuild package

The packages commands require only that you provide the name of the package.
The group and the latest version will be located automatically. If there are
overlaying grops or you want a specific version you may specify them using the
-g and -v flags.

    $ acmd package build --raw cq-upgrade-acl
    {"success":true,"msg":"Package built"}

#### Install package

    $ acmd package install --raw cq-upgrade-acl
    {"success":true,"msg":"Package installed"}

#### Upload package

You may install a properly generated package zip e.g. downloaded from another instance.

    $ acmd package upload new-catalog-1.0.zip


### User tool

#### List Users

    $ acmd user list
    ...

#### Create Users

    $ acmd user create --password=foobar jdoe
    /home/users/j/jdoe

#### Set profile properties

    $ acmd user setprop age=29,name="John Doe" jdoe
    /home/users/j/jdoe


### Group tool

#### List groups

    $ acmd group list
    ....

The list action is the default action of the groups tool so ```acmd groups```
will suffice.

#### Create group

    $ acmd group create editors
    /home/groups/e/editors

#### Add user to group

    $ acmd group adduser editors jdoe
    /home/groups/e/editors


### Bundles

The bundle tool can list, start and stop jackrabbit OSGi bundles. If you
install the bash completion script bundle names will be autocompleted. Like
the packages tool, the group and version of the bundle will be inferred
for all commands.

#### List bundles

List all bundles in the system.

    $ acmd bundle list
    ...
    org.apache.sling.extensions.webconsolesecurityprovider  1.0.0   Active
    org.apache.sling.jcr.jcr-wrapper    2.0.0   Active
    org.apache.tika.core    1.3.0.r1436209  Active
    org.apache.tika.parsers 1.3.0.r1436209  Active
    biz.aQute.bndlib    1.43.0  Active
    com.day.cq.collab.cq-collab-blog    5.6.10  Active
    com.day.cq.collab.cq-collab-calendar    5.6.9   Active
    ...

The output is tab-separated to make it easy to read specific data.
E.g. to get the version of the bndlib bundle:

    $ acmd bundle list | grep bndlib | cut -f 2
    1.43.0

#### Stop Bundle

    $ acmd bundle stop biz.aQute.bndlib
    $

#### Start bundle

All bundle-commands support the --raw flag which prints raw json output.

    $ acmd bundle start biz.aQute.bndlib --raw
    {
        "fragment": false,
        "stateRaw": 32
    }
    $

### Groovy

Note: the groovy tool requires the
[cq-groovy-console](https://github.com/Citytechinc/cq-groovy-console) bundle
from Citytech.

The groovy tool allows execution of arbitrary code server side. Put your code
in a file and execute with:

    $ acmd groovy list-entire-catalog.groovy
    ....

For more documentation on how to write groovy scripts install the
cq-groovy-console bundle and go to
[http://localhost:4502/etc/groovyconsole.html](http://localhost:4502/etc/groovyconsole.html)


### Assets

The assets tool controls interactions with the AEM dam.

#### List assets

    $ acmd asset ls /selfies

lists assets and folders in /content/dam/selfies

#### Find

List all assets in the system

    $ acmd asset find /

#### Import assets

The import command allows for importing single files and entire directories
into the DAM.

To import a single file into /content/dam/selfie.jpg

    $ acmd asset import ~/Pictures/selfie.jpg

If a directory is given it will be recreated at /content/dam

    $ acmd asset import ~/Pictures/selfies

will create /content/dam/selfies and import all the contents

The -d flag allows for importing into a specific directory.

    $ acmd asset import -d /content/dam/another_directory ~/Pictures/selfies

#### Touch

To trigger the Update Asset workflow for an asset

    $ acmd asset touch /selfie.jpg


### Storage

The backend storage tool can trigger optimization jobs.

#### Tar Optimize

    $ acmd storage optimize

Asynchronously triggers a tar optimization job for the filesystem backend.

#### Garbage collection

    $ acmd storage gc

Asynchronously triggers a garbage collection job.

## Configuration

Acmd config is specified in ```~/.acmd.rc``` If this file does not exist at first
execution it will be created from a template. Here is what the template file
looks like:

    # This is a template configuration file for the AEM Command line tools.
    # acmd expects this file to exist as ~/.acmd.rc

    # Each server is defined by a section named [server <name>].
    # This server can then be accessed via the --server option.
    [server localhost]
    host=http://localhost:4502
    username=admin
    password=admin

    # The default server option specifies which server to use if
    # the --server option is not specified.
    [settings]
    default_server=localhost

    # Add custom tools directories here as
    # prefix=<custom_tool_dir>
    [projects]


### Servers

The most common use of the config file is to add additional servers. You will
want to add a server entry for each instance in your setup. So one for your
local, one for integration testing, one staging server and one each for
author and publish instances in production.

Once this is done you can easily run any command on any server via the ```-s```
flag. Like for example

    $ acmd -s prod-author bundle
    ....

### Projects

The projects section enables you to add project specific tools you your
arsenal. Let's say you have created a custom tool for handling a product
catalog under _~/my_project/acmd-tools/catalog.py_. Now what you do is
add the following to your ```.acmd.rc```

    [projects]
    custom=~/my_project/acmd-tools

All python files in _aem-tools_ will be imported and your tool should show up
in with the help command as custom:catalog

    $ acmd help
     ...
    custom:catalog

### Encrypted passwords

For many use cases it is not desireable to keep passwords in plaintext. For
this purpose it is possible to encrypt the configuration file and use a separate
passphrase on invocation.

### Installation
Crypto support requries the pycryptodome package which in turn requires some
native packages. Because of this it is not installed by default. Install with

    $ pip install pycryptodome

or if you are using Python 3

    $ pip3 install pycryptodome

#### Set master passphrase
To start set a master password. The master will be stored in the system
keychain using the python [keyring](https://pypi.python.org/pypi/keyring#using-keyring-on-headless-linux-systems) library.

    $ acmd config set-master
    Set master passphrase:

#### Invocation
The following command will ask for a passphrase which can then be used on acmd
invocation.

    $ acmd config encrypt qa-server

By default the tool encrypts the local ~/.acmd.rc file. A parameter is
available to encrypt the password for a specific file.

    $ acmd config encrypt --file=/home/jennie/.acmd.rc qa-server

If you look in your rcfile after this you will notice the password section has
changed.

    [server qa-server]
    ...
    username = admin
    password = {OLVoV9rxctNlCYtZuyunciQK0yXS59oyI8mnY4TuYxHg++0lB+QJ}

Now as long as the master passphrase is set in the keychain you can continue to
use aem-cmd as normal.

    $ acmd ls /content/dam
    project
    stuff
    other


#### Notes on encrypted passwords

- If you are on a linux system you may have to install a secure backend
to avoid storing the master password in plaintext. Refer to the [keyring
documentation](https://pypi.python.org/pypi/keyring#using-keyring-on-headless-linux-systems) for more details.

- The brackes '{' and '}' are the signals to acmd that the password is encrypted and so do
not use passwords with brackets at both beginning and end.

- In the process of encrypting the password acmd
will parse and rewrite the entire config file and will discard any comments
left in the file. This is a known bug or if you will, expected behavior.

## Custom Tools

Writing a custom tool is relatively easy. All of acmd is written in Python and
relies on the [requests](http://www.python-requests.org) http client library
for communication with AEM. The best way to learn how to extend is to read the
tools code under acmd/tools.

Nevertheless here is boilerplate for creating a new tool.

```python
# coding: utf-8
from acmd.tool import tool

@tool('catalog', ['inspect', 'upload'])
class CatalogTool(object):
    def execute(self, server, argv):
        sys.stdout.write("Hello, world.\n")
```

There are two essential parts here. The ```@tool``` decorator takes care of
declaring the tool so it can be found by acmd. The first argument is the label used
for the tool on the command line. Note that for custom tools declared
under ```[projects]``` a prefix will be added to the tool name. The second
argument is a list of commands available under the tool. Remember that under
normal circumstances the tool represents a resource and the first argument is
a command to perform on that resource. This list is used for autocompletion and
can be omitted for simpler tools.

The ```execute()``` method takes a server argument
containing all info on the currently selected server and argv is a list of
tool arguments starting with the tool name. See for example the bundle-tool
for info on how to use the optparse package to add tool specific options.

And that is pretty much it. The tool does not have to have any specific name
(though a -Tool suffix is idiomatic), and it does not have to inherit any
specific class.



## Other tools, recommendations and shoutouts

* The inspiration for acmd comes from the Polopoly CMS command line tools - https://github.com/polopolyps/pcmd
* The CQ Unix Toolkit is a similar toolset written in bash - https://github.com/Cognifide/CQ-Unix-Toolkit
* The AEM Curl command reference was incredibly helpful during the development of acmd - https://gist.github.com/sergeimuller/2916697
* oak-run is a another great command line tool for maintaining AEM instances - https://github.com/apache/jackrabbit-oak/tree/trunk/oak-run
