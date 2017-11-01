#!/bin/bash

#echo "Positional Parameters"
#echo '$0 = ' $0
#echo '$1 = ' $1
#echo '$2 = ' $2
#echo '$3 = ' $3
# Program:
#	Program shows the script name, parameters...
# History:
# 2015/07/16	VBird	First release
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

echo "The script name is        ==> ${0}"
echo "Total parameter number is ==> $#"
[ "$#" -lt 1 ] && echo "The number of parameter is less than 1.  Stop here." && exit 0
echo "Your whole parameter is   ==> '$@'"
echo "The 1st parameter         ==> ${1}"
echo "The 2nd parameter         ==> ${2}"

# Argument = -t test -r server -p password -v

usage()
{
cat << EOF
usage: $0 options

This script run the test1 or test2 over a machine.

OPTIONS:
   -h      Show this message
   -t      Sleep time
   -g      Get variable
   -s      Set variable
EOF
}

SLEEP=0
GET=''
SET=''

while getopts “hg:t:s:” OPTION
do
     case $OPTION in
         h)
             usage
             exit 1
             ;;
         t)
             SLEEP=$OPTARG
             ;;
         g)
             GET=$OPTARG
             ;;
         s)
             SET=$OPTARG
             ;;
         ?)
             usage
             exit
             ;;
     esac
done
[ "$#" -eq 1 ] && GET=$1

echo "SLEEP: " $SLEEP
echo "GET:   " $GET
echo "SET:   " $SET
