#!/bin/bash
set -e

acmd help >> /tmp/output


diff -s ./expected_output /tmp/output
