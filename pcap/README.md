A script to create a pcap file and instructions to play it.

1. Create a veth pair, to simulate a network with incoming traffic
  ```bash
  ip link add name veth1 type veth peer name veth2
  # mac addresses must match
  ip link set veth1 address 12:34:56:78:90:ab
  ip link set veth2 address 12:34:56:78:90:cd
  # dst ip of of packet must match
  ip address add 192.168.3.4 dev veth2
  ip link set veth1 up
  ip link set veth2 up
  # set this to 2, otherwise packets are will be dropped (0 should disable it, but it doesn't seem to work for some reason)
  echo 2 > /proc/sys/net/ipv4/conf/veth2/rp_filter
  
  # to delete everything, just run:
  ip link delete veth1
  ```

2. Validate that you can send/receive packets
    ```bash
    # in 1 shell, run this to listen for incoming packets
    nc -kul 192.168.3.4 9456
    # in another shell, start python and send a packet
    from scapy.all import *
    sendp(
        Ether(src='12:34:56:78:90:ab', dst='12:34:56:78:90:cd')\
        /IP(src='192.168.1.2', dst='192.168.3.4')\
        /UDP(sport=999, dport=9456)\
        /'abc', iface='veth1')
    ```

3. Create the pcap file
    ```bash
    python create_pcap.py f.pcap
    
    # fix ip checksums
    tcprewrite --fixcsum --infile=f.pcap --outfile=f_fixed.pcap
    
    # (you can see the diff with the following command)
    xxd f.pcap > a && xxd f_fixed.pcap > b && git diff --no-index --word-diff --unified=1000 a b; rm a b
    ```

4. Play pcap file:
    ```bash
    tcpreplay --intf1=veth1 f_fixed.pcap
    ```

5. You should be able to see it in `nc` now
