# AEM Command Line Tools

This is a toolset package for working with AEM and especially
CRX repositories via command line tools. It tries to utilize
the unix philosophy by reading and writing plaintext in order
to interoperate with common tools such as grep, cut, sed and awk.


## Installation

acmd is available in PyPI.

    $ pip instal aem-cmd
    ...
    $ acmd
    Usage: acmd [options] <tool> <args>
    Run 'acmd help' for list of available tools

    Options:
      -h, --help            show this help message and exit
      -s str, --server=str  server name


## Tools

To begin with the commons rest webservices for interacting with
system resources is available

### Help

The help tool lists all installed tools

    $ acmd help
    Available tools:
      inspect
      bundles
      help
      packages

### JCR tools

The JCR tools are considered so common they are not grouped together but come
as separate commands.

List subpaths:

    $ amcd ls /
    index.servlet
    bundles
    rep:policy
    services
    home
    ....

Show node properties:

    $ acmd cat /content
    jcr:primaryType:	sling:OrderedFolder
    jcr:createdBy:	admin
    jcr:mixinTypes:	[u'sling:Redirect', u'mix:lockable', u'rep:AccessControllable']
    sling:target:	/geohome
    sling:resourceType:	sling:redirect
    jcr:created:	Fri Jun 13 2014 14:17:56 GMT-0400

Search for properties

    $ acmd search serial_nbr=1234
    /content/catalog/product4711


### Bundles

The bundles tool can list, start and stop jackrabbit OSGi bundles.

#### List bundles

List all bundles in the system.

    $ acmd bundles list
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

    $ acmd bundles list | grep bndlib | cut -f 2
    1.43.0

#### Stop Bundle

    $ acmd bundles stop biz.aQute.bndlib
    $

#### Start bundle

All bundles commands support the --raw flag which prints raw json output.

    $ acmd bundles start biz.aQute.bndlib --raw
    {
        "fragment": false,
        "stateRaw": 32
    }
    $


### Packages

The packages tool support up- and downloading, installing and uninstalling packages.

#### List packages

By default the packages tool lists all installed packages.

    $ acmd packages list
    ...
    day/cq540/product   cq-portlet-director 5.4.38
    day/cq550/product   cq-upgrade-acl  5.5.2
    day/cq560/collab/blog   cq-collab-blog-pkg  5.6.17
    day/cq560/collab/calendar   cq-collab-calendar-pkg  5.6.12
    day/cq560/social/calendar   cq-social-calendar-pkg  1.0.28
    ....

### Storage

The backend storage tool can trigger optimization jobs.

#### Tar Optimize

    $ acmd storage optimize

Asynchronously triggers a tar optimization job for the filesystem backend.

#### Garbage collection

    $ acmd storage gc

Asynchronously triggers a garbage collection job.



## Configuration

Acmd config is specified in ```~/.acmd.rc.``` If this file does not exist at first
execution it will be created from a template. Here is what the template file
looks like:

    # This is a template configuration file for the AEM Command line tools.
    # acmd expects this file to exist as ~/.acmd.rc

    # Each server is defined by a section named [server <name>].
    # This server can then be accessed via the --server option.
    [server localhost]
    host=localhost
    port=4502
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

    $ acmd -s prod-author bundles
    ....

### Projects

The projects section enables you to add project specific tools you your
arsenal. Let's say you have created a custom tool for handling a product
catalog under _~/my_project/acmd-tools/catalog.py_. Now what you do is
add the following to your ```.acmd.rc```

    [pojects]
    custom=~/my_project/acmd-tools

All python files in _aem-tools_ will be imported and your tool should show up
in with the help command as custom:catalog

    $ acmd help
     ...
    custom:catalog

## Custom Tools

Writing a custom tool is relatively easy. All of acmd is written in Python and
relies on the [requests](http://www.python-requests.org) http client library
for communication with AEM. The best way to learn how to extend is to read the
tools code under acmd/tools.

Nevertheless here is boilerplate for creating a new tool.

```python
# coding: utf-8
from acmd.tool import tool

@tool('template')
class TemplateTool(object):
    def execute(self, server, argv):
        sys.stdout.write("Hello, world.\n")
```

There are two essential parts here. The ```@tool``` decorator takes care of declaring
the tool so it can be found but acmd. The argument is the label used for the
tool on the command line. Note that for custom tools declared under
```[projects]``` a prefix will be added to the tool name.

The ```execute()``` method takes a server argument
containing all info on the currently selected server and argv is a list of
tool arguments starting with the tool name. See for example the bundles tool
for info on how to use the optparse package to add tool specific options.

And that is pretty much it. The tool does not have to have any specific name
(though a -Tool suffix is idiomatic), and it does not have to inherit any
specific class.
