#!/bin/bash
set -e

acmd help &> /tmp/output
diff -s ./expected/help_command.txt /tmp/output


acmd config set-master &> /tmp/output | true
diff -s ./expected/failed_set_master_pass.txt /tmp/output
