#!/bin/bash

OUTPUT=geoip.txt

echo "# This file is for use with haproxy" > $OUTPUT

for COUNTRY in *.cidr ; do
	 CC=$(basename $COUNTRY .cidr)
	 awk -v CC=$CC '{print $0, CC}' $COUNTRY >>$OUTPUT
done

for COUNTRY in *.ipv6 ; do
	         CC=$(basename $COUNTRY .ipv6)
		          awk -v CC=$CC '{print $0, CC}' $COUNTRY >>$OUTPUT
done


