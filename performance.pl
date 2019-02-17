#!/bin/perl

# MemeInvestor script for checking containers'
# performance base on processing time
# Created by @thecsw

use strict;
use warnings;

print "MemeInvestor script for checking containers' performance\n";
print "The log analysis will take some time depending on the log size...\n\n";

my $color = "\033[1;32m";

print "BOT STATS:";
my $bot_commands = `docker-compose logs bot | grep processed | wc -l | tr -d '\n'`;
print "\tNumber of commands received since last deployment - $color$bot_commands\033[0m\n";

my $bot_processing = `docker-compose logs bot | grep processed | sed "s/s//g" | awk '{sum += \$7} END {print sum / NR}' | tr -d '\n'`;
print "\tAverage time to process commands - $color$bot_processing seconds\033[0m\n";

my $bot_waiting = `docker-compose logs bot | grep retrieved | sed "s/s//g" | awk '{sum += \$7} END {print sum / NR}' | tr -d '\n'`;
print "\tAverage waiting time for commands - $color$bot_waiting seconds\033[0m\n";

print "\nCALCULATOR STATS:";

my $calculator_commands = `docker-compose logs calculator | grep processed | wc -l | tr -d '\n'`;
print "\tNumber of investments evaluated since last deployment - $color$calculator_commands\033[0m\n";

my $calculator_processing = `docker-compose logs calculator | grep processed | sed "s/s//g" | awk '{sum += \$7} END {print sum / NR}' | tr -d '\n'`;
print "\tAverage time to process investments - $color$calculator_processing seconds\033[0m\n";
