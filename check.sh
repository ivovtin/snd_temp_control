#!/bin/bash

tail -n 1 res.dat | while read -a line;
do
        if [[ ${line[1]} > 40.00 ]]
	then
		echo -e "${line[1]}";
  		echo 'Caution - danger! Temperature exceeded.' | mutt -s "Temperature ASHIPH-SiPM tests" "i.v.ovtin@inp.nsk.su"
 	fi
done
