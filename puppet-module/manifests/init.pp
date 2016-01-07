# == Class: acmd
#
# Installs AEM Command Line Interface
#
# === Parameters
#
# [*version*]
#   Specify version to install
#
# === Examples
#
#  class { 'acmd':
#    version => "0.6.1",
#  }
#
# === Copyright
#
# Copyright 2016 Björn Skoglund
#
class acmd (
  $version = $acmd::params::version,
  ) {
    include python
    include apt

    anchor { 'acmd::begin': } ->
    class { '::acmd::install': } ->
    anchor { 'acmd::end': }
}
