#!/bin/bash
set -e

ENCRYPTION_ENABLED=false

while getopts ":c" opt; do
  case $opt in
    c)
      ENCRYPTION_ENABLED=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

# Check that help command finds tools and prints results
acmd help &> /tmp/output | true
diff -s ./expected/help_command.txt /tmp/output

# Check that correct error message is printed on missing pycrypto
if [ "$ENCRYPTION_ENABLED" == "false" ]; then
    acmd config set-master &> /tmp/output | true
    diff -s ./expected/failed_set_master_pass.txt /tmp/output
fi
