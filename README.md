NetGrok-II
================================================================================
NetGrok is a tool for understanding network traffic from the point-of-view of
the local network. It uses [SSLsplit] to monitor connections made to and from
local hosts, and then outputs information about the connections, such as
addresses, time, and size. 

[SSLsplit]: https://www.roe.ch/SSLsplit
[OpenWRT]: https://openwrt.org/
[Original NetGrok project]: https://github.com/codydunne/netgrok

Repository Overview
--------------------------------------------------------------------------------
### Documentation
This directory is currently empty, but will eventually contain
a basic description of how to use and implement the NetGrok app on a 
compatible OpenWRT router.

### SSLSplit
These are the actual data gathering files that do the background work of Netgrok.
This is simply a slight modification of SSLSplit that parses data from that
software and instead publishes is it to port 7188 allowing our visualization 
software to paint a picture of the network.

### Testing
These are our personal testing files (testing plans) that are currently under development.

SSLsplit-NetGrok on an Ubuntu machine acting as the default gateway (router)
--------------------------------------------------------------------------------
Reference: https://blog.heckel.xyz/2013/08/04/use-sslsplit-to-transparently-sniff-tls-ssl-connections/

This is the simplist way to use SSLsplit-NetGrok. The machine running
SSLsplit-NetGrok acts as a router (and man-in-the-middle) for the client. For
this example, both the client and router were 64-bit Ubuntu Linux machines.

### 0. Download SSLsplit-NetGrok onto the Ubuntu machine acting as the router:

 #### a. Clone the GitHub repository:

  git clone https://github.com/tylerreece/NetGrok-II

 #### b. Next, install libevent and libssl so sslsplit can handle large numbers of
  ssl connections simultaneously:

  sudo apt-get install libssl-dev libevent-dev


### 1. Generate a Certificate Authority key and certificate. Eventually, this step
might be automated on the OpenWRT router to generate a NetGrok CA key and
certificate if they are not present. Generate a key and certificate in the
certificates directory:

openssl genrsa -out netgrok.key 4096
openssl req -new -x509 -days 1826 -key netgrok.key -out netgrok.crt

  Country:             US \
  State:               New York \
  City:                West Point \
  Organization:        NetGrok CA \
  Organizational Unit: NetGrok II \
  Common Name:         NetGrok \
  Email Address: \


### 2. Configure the Ubuntu machine acting as the router:

####  a. Enable IP forwarding:

  sudo sysctl -w net.ipv4.ip_forward=1

####  b. Delete all current NAT rules, just in case:

  sudo iptables -t nat -F

 #### c. Configure NAT to redirect packets to ports that SSLsplit listens to:

  sudo iptables -t nat -A PREROUTING -p tcp --dport   80 -j REDIRECT --to-ports 8080 \
  sudo iptables -t nat -A PREROUTING -p tcp --dport  443 -j REDIRECT --to-ports 8443 \
  sudo iptables -t nat -A PREROUTING -p tcp --dport  465 -j REDIRECT --to-ports 8443 \
  sudo iptables -t nat -A PREROUTING -p tcp --dport  587 -j REDIRECT --to-ports 8443 \
  sudo iptables -t nat -A PREROUTING -p tcp --dport  993 -j REDIRECT --to-ports 8443 \
  sudo iptables -t nat -A PREROUTING -p tcp --dport 5222 -j REDIRECT --to-ports 8080 \

  These rules redirect HTTP, HTTPS, SMTP, IMAP, and WhatsApp packets.


### 3. Run SSLsplit-NetGrok from the sslsplit/ directory on the Ubuntu
machine acting as the router:

 ####  a. To see the JSON dumps, uncomment the print statement in netgrok().
 ####  b.

    make clean
    make
    ./sslsplit -k ../netgrok.key -c ../netgrok.crt ssl 0.0.0.0 8443 tcp 0.0.0.0 8080


### 4. Configure the client's web browser (if the CA cert is not already installed):

 #### a. Copy the netgrok.crt onto the client machine

  #### b. Open up Firefox and go to Preferences > Privacy & Security >
  View Certificates > Authorities > Import, and then select the netgrok.crt


### 5. Configure the client's default gateway:

####  a. Add a new default gateway. 
  It is critical that you do this before deleting the original default 
  gateway if you are using the client through SSH, or else you will disconnect. 
  Use the IP address of the Ubuntu machine acting as the router:

  sudo route add default gw <router_ip_address>

####  b. Delete the client's original default gateway:

  sudo route del default gw <original_gw_ip_address>

Now you should be able to open up Firefox and go to any website. Click on the
secure HTTPS lock icon in the URL bar to display the certificate. It should be
verified by the NetGrok CA.

### 6. Run the server.

   In the main directory:  
   
   python3 server.py
   
   This will run the server hosted on netgrok.eecs.net on port 5000.
   
### 7. Navigate to visualization page.

   While connected to EECSNet, visit netgrok.eecs.net:5000 to see the main network visualization page.

## Authors

- **Son Tran** - *SSLSplit back-end*
- **Tyler Reece** - *Current Author* 
- **Dan Young** - *Current Author*
- **Josh Balba** - *Current Author*
- **Matt Kim** - *Current Author*

## License

TODO
