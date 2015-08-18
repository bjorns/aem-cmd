# AEM Command Line Tools

This is a toolset package for working with AEM and especially
CRX repositories via command line tools. It tries to utilize
the unix philosophy by reading and writing plaintext in order
to interoperate with common tools such as grep, cut, sed and awk.

## Tools

To begin with the commons rest webservices for interacting with
system resources is available

### Help

The help command lists all installed tools

    $ acmd help
    Available commands:
      inspect
      bundles
      help
      packages


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

All bundles commands support the --verbose flag which prints raw json output.

    $ acmd bundles start biz.aQute.bndlib
    {
        "fragment": false,
        "stateRaw": 32
    }
    $


### Packages

The packages command support up- and downloading, installing and uninstalling packages.

#### List packages

By default the packages command lists all installed packages.

    $ acmd packages list
    ...
    day/cq540/product   cq-portlet-director 5.4.38
    day/cq550/product   cq-upgrade-acl  5.5.2
    day/cq560/collab/blog   cq-collab-blog-pkg  5.6.17
    day/cq560/collab/calendar   cq-collab-calendar-pkg  5.6.12
    day/cq560/social/calendar   cq-social-calendar-pkg  1.0.28
    ....
