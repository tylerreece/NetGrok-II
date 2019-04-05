
SSLSPLITNETGROK=https://github.com/Ghost-in-the-Bash/sslsplit-netgrok.git
NETGROKII=https://github.com/tylerreece/NetGrok-II.git

all: ubuntu

ubuntu: certs ubunturouter

certs:
        sudo apt-get install libssl-dev libevent-dev
        printf "US\nNew York\nWest Point\nNetGrok CA\nNetGrok II\nNetGrok\n\n" | openssl gen$

ubunturouter:
        sudo sysctl -w net.ipv4.ip_forward=1
        sudo iptables -t nat -F
        sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 8080
        sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-ports 8443
        sudo iptables -t nat -A PREROUTING -p tcp --dport 465 -j REDIRECT --to-ports 8443
        sudo iptables -t nat -A PREROUTING -p tcp --dport 587 -j REDIRECT --to-ports 8443
        sudo iptables -t nat -A PREROUTING -p tcp --dport 993 -j REDIRECT --to-ports 8443
        sudo iptables -t nat -A PREROUTING -p tcp --dport 5222 -j REDIRECT --to-ports 8080

