#!/bin/bash
# This is an unmaintainable hack. I'll come up with something better or borrow
# it from dominionstats.

cd ~/webapps/scorepile/data
for day in $*
do
    wget -x http://innovation.isotropic.org/gamelog/201304/$day/all.tar.bz2
    (cd innovation.isotropic.org/gamelog/201304/$day; tar xvf all.tar.bz2)
done

