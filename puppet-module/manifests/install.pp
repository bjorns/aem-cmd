class acmd::install inherits acmd {

  $packages = ["libxml2-dev", "libxslt-dev", "zlib1g-dev"]
  package {
    $packages: ensure => installed,
  }

  python::pip { 'aem-cmd' :
    pkgname      => 'aem-cmd',
    ensure       => $acmd::version,
    timeout      => 3600,
  }
}
