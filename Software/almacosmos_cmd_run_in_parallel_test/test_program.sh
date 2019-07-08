#!/bin/bash
# 


# print all input arguments
echo "This is a test program."
echo "User has input these arguments:"
for (( i=1; i<=$#; i++ )); do
    echo "${!i}"
    sleep 1
done

echo "Now sleeping for 7 seconds."
sleep 7

echo "Done!"


