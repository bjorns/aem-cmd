#!/bin/bash
set -e

# Check that help command finds tools and prints results
acmd help &> /tmp/output | true
diff -s ./expected/help_command.txt /tmp/output

# Check that correct error message is printed on missing pycrypto
acmd config set-master &> /tmp/output | true
diff -s ./expected/failed_set_master_pass.txt /tmp/output
