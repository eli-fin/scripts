import struct, time, sys


def write_safe(stream, buf):
    assert stream.write(buf) == len(buf), "Error writing to stream"


def mac_str_to_bytes(mac_str):
    mac_str_bytes = mac_str.encode()
    parts = mac_str_bytes.split(b":")
    assert len(parts) == 6
    parts_bytes = parts = [int(i, 16) for i in parts]
    return bytes(parts)


def ip_str_to_bytes(ip_str):
    ip_str_bytes = ip_str.encode()
    parts = ip_str_bytes.split(b".")
    assert len(parts) == 4
    parts_bytes = parts = [int(i) for i in parts]
    return bytes(parts)


def write_pcap_header(stream):
    """
    typedef struct pcap_hdr_s {
        guint32 magic_number;   /* magic number */
        guint16 version_major;  /* major version number */
        guint16 version_minor;  /* minor version number */
        gint32  thiszone;       /* GMT to local correction */
        guint32 sigfigs;        /* accuracy of timestamps */
        guint32 snaplen;        /* max length of captured packets, in octets */
        guint32 network;        /* data link type */
    } pcap_hdr_t;
    """
    write_safe(
        stream,
        struct.pack(
            "IHHiIII",
            0xA1B2C3D4,
            2,
            4,
            0,
            0,
            65535,
            1,  # LINKTYPE_ETHERNET/DLT_EN10MB
        ),
    )


def write_packet_header(stream, pkt_len, time_ms):
    """
    typedef struct pcaprec_hdr_s {
        guint32 ts_sec;         /* timestamp seconds */
        guint32 ts_usec;        /* timestamp microseconds */
        guint32 incl_len;       /* number of octets of packet saved in file */
        guint32 orig_len;       /* actual length of packet */
    } pcaprec_hdr_t;
    """
    write_safe(
        stream,
        struct.pack(
            "IIII",
            int(time_ms // 1000 // 1000),
            int(time_ms % (1000 * 1000)),
            pkt_len,
            pkt_len,
        ),
    )


def write_udp_packet(
    stream, time_ms, src_mac, dst_mac, src_ip, dst_ip, src_port, dst_port, payload
):
    packet = bytearray()
    # ethernet
    packet += mac_str_to_bytes(dst_mac)  # dst mac
    packet += mac_str_to_bytes(src_mac)  # src mac
    packet += b"\x08\x00"  # ether type ipv4
    ETHER_LEN = len(packet)

    # ipv4
    packet += bytes([0b0100_0101])  # v4, hdr len=5 words=20 bytes
    packet += b"\x00"  # differentiated services
    IP_LEN_OFFSET = len(packet)
    packet += b"\x00\x00"  # total length
    packet += b"\x00\x00"  # id
    packet += b"\x00"  # flags
    packet += b"\x00"  # fragment offset
    packet += (64).to_bytes(1, "big")  # ttl
    packet += b"\x11"  # protocol=udp
    packet += b"\x00\x00"  # checksum
    packet += ip_str_to_bytes(src_ip)  # src ip
    packet += ip_str_to_bytes(dst_ip)  # dst ip
    IP_LEN = len(packet) - ETHER_LEN

    # udp
    packet += (src_port).to_bytes(2, "big")  # src port
    packet += (dst_port).to_bytes(2, "big")  # dst port
    UDP_LEN_OFFSET = len(packet)
    packet += b"\x00\x00"  # length
    packet += b"\x00\x00"  # checksum
    packet += payload  # payload

    packet[IP_LEN_OFFSET : IP_LEN_OFFSET + 2] = (len(packet) - ETHER_LEN).to_bytes(
        2, "big"
    )
    packet[UDP_LEN_OFFSET : UDP_LEN_OFFSET + 2] = (
        len(packet) - ETHER_LEN - IP_LEN
    ).to_bytes(2, "big")

    write_packet_header(f, len(packet), time.time_ns() / 1000)
    write_safe(f, packet)


if __name__ == "__main__":
    path = sys.argv[1]
    print("Writing to", path, file=sys.stderr)
    with open(path, "wb") as f:
        write_pcap_header(f)
        write_udp_packet(
            f,
            time.time_ns() / 1000,
            "12:34:56:78:90:ab",
            "12:34:56:78:90:cd",
            "192.168.1.2",
            "192.168.3.4",
            9123,
            9456,
            b"Hi, it's me, Eli!",
        )
        time.sleep(1.5)
        write_udp_packet(
            f,
            time.time_ns() / 1000,
            "12:34:56:78:90:ab",
            "12:34:56:78:90:cd",
            "192.168.1.2",
            "192.168.3.4",
            9123,
            9456,
            b"Hi, it's me, Eli!",
        )
