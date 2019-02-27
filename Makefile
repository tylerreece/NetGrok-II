SSLSPLITNETGROK=https://github.com/Ghost-in-the-Bash/sslsplit-netgrok.git
NETGROKII=https://github.com/tylerreece/NetGrok-II.git

ubuntu: certs ubunturouter
	git clone $(SSLSPLITNETGROK)
	cd sslsplit; make clean
	cd sslpslit; make
	cd sslsplit; ./sslsplit -k ../certificates/netgrok.key -c ../certificates/netgrok.crt ssl 0.0.0.0 8443 tcp 0.0.0.0 8080

certs:
	sudo apt-get install libssl-dev libevent-dev
	printf "US\nNew York\nWest Point\nNetGrok CA\nNetGrok II\nNetGrok\n\n" | openssl genrsa -out certificates/netgrok.key 4096 openssl req -new -x509 -days 1826 -key certificates/netgrok.key -out certificates/netgrok.crt

ubunturouter:
	sudo sysctl -w net.ipv4.ip_forward=1
	sudo iptables -t nat -F
	sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 8080
	sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-ports 8443
	sudo iptables -t nat -A PREROUTING -p tcp --dport 465 -j REDIRECT --to-ports 8443
	sudo iptables -t nat -A PREROUTING -p tcp --dport 587 -j REDIRECT --to-ports 8443
	sudo iptables -t nat -A PREROUTING -p tcp --dport 993 -j REDIRECT --to-ports 8443
	sudo iptables -t nat -A PREROUTING -p tcp --dport 5222 -j REDIRECT --to-ports 8080

openwrt:
	git clone $(SSLSPLITNETGROK)
