#!/bin/perl

# MemeInvestor script for checking containers'
# performance base on processing time
# Created by @thecsw

use strict;
use warnings;

print "MemeInvestor script for checking containers' performance\n";
print "The log analysis will take some time depending on the log size...\n\n";

my $bot_processing = `docker-compose logs bot | grep processed | sed "s/s//g" | awk '{sum += \$7} END {print sum / NR}'`;
$bot_processing =~ s/\n//;
print "Average time to process commands - \033[0;32m$bot_processing seconds\033[0m";

my $calculator_processing = `docker-compose logs calculator | grep processed | sed "s/s//g" | awk '{sum += \$7} END {print sum / NR}'`;
$calculator_processing =~ s/\n//;
print "Average time to process investments - \033[0;32m$calculator_processing seconds\033[0m";
