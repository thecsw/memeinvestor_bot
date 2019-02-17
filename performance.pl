#!/bin/perl

# MemeInvestor script for checking containers'
# performance base on processing time
# Created by @thecsw

use strict;
use warnings;

print "MemeInvestor script for checking containers' performance\n";
print "The log analysis will take some time depending on the log size...\n\n";

my $bot_processing = `docker-compose logs bot | grep processed | sed "s/s//g" | awk '{sum += \$7} END {print sum / NR}'`;
print "Average time to process commands - \033[0;32m$bot_processing\033[0m"
