#!/bin/bash

while true
do
./prot2_control2 >> res.dat

tail -n 1 res.dat | while read -a line;
do
        if [[ ${line[1]} > 53.00 ]]
        then
                echo -e "${line[1]}";
                echo 'Caution - danger! Temperature exceeded ('${line[1]}')' | mutt -s "Temperature ASHIPH-SiPM tests" "i.v.ovtin@inp.nsk.su;i.a.kuyanov@inp.nsk.su"
        fi
done

tail -n 1 res.dat
sleep 20
done
