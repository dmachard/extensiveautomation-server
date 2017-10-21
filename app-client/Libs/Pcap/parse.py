# to support new print style on python 2.x
from __future__ import print_function 

import struct
import socket

class FileFormat(object):
    PCAP = 0xA1B2C3D4
    PCAP_NG = 0x0A0D0D0A
    UNKNOWN = -1
    
class LinkLayerType(object):
    ETHERNET = 1
    LINUX_SLL = 113
    
class NetworkProtocol(object):
    IP = 2048
    IPV6 = 34525
    P802_1Q = 33024
    PPP_IP = 33
    PPPOE_SESSION = 34916
    
class TransportProtocol(object):
    TCP = 6
    UDP = 17

def extractFormat(infile):
    """
    get cap file format by magic num.
    return file format and the first byte of string
    :type infile:file
    """
    buf = infile.read(4)
    if len(buf) == 0:
        # EOF
        print("empty file", file=sys.stderr)
        sys.exit(-1)
    if len(buf) < 4:
        print("file too small", file=sys.stderr)
        sys.exit(-1)
    magic_num, = struct.unpack(b'<I', buf)
    if magic_num == 0xA1B2C3D4 or magic_num == 0x4D3C2B1A:
        return FileFormat.PCAP, buf
    elif magic_num == 0x0A0D0D0A:
        return FileFormat.PCAP_NG, buf
    else:
        return FileFormat.UNKNOWN, buf
        
def decodeTcp(tcp_packet):
    """
    read tcp data.http only build on tcp, so we do not need to support other protocols.
    """
    tcp_base_header_len = 20
    # tcp header
    tcp_header = tcp_packet[0:tcp_base_header_len]
    source_port, dest_port, seq, ack_seq, t_f, flags = struct.unpack(b'!HHIIBB6x', tcp_header)
    # real tcp header len
    tcp_header_len = ((t_f >> 4) & 0xF) * 4
    
    # skip extension headers
    if tcp_header_len > tcp_base_header_len:
        pass

    # tcp data
    data = tcp_packet[tcp_header_len:]

    return source_port, dest_port, flags, seq, ack_seq, data

def decodeUdp(udp_packet):
    """
    read udp only build on tcp, so we do not need to support other protocols.
    """
    udp_base_header_len =8
    # udp header
    udp_header = udp_packet[0:udp_base_header_len]
    source_port, dest_port, lgth, udp_sum = struct.unpack(b'!4H', udp_header)
    # data
    data = udp_packet[udp_base_header_len:]

    return source_port, dest_port, lgth, udp_sum, data
    
def decodeIpV4(network_protocol, ip_packet):
    """
    """
    # ip header
    ip_base_header_len = 20
    ip_header = ip_packet[0:ip_base_header_len]
    (ip_info, ip_length, transport_protocol) = struct.unpack(b'!BxH5xB10x', ip_header)
    # real ip header len.
    ip_header_len = (ip_info & 0xF) * 4
    ip_version = (ip_info >> 4) & 0xF

    # skip all extra header fields.
    if ip_header_len > ip_base_header_len:
        pass

    source = socket.inet_ntoa(ip_header[12:16])
    dest = socket.inet_ntoa(ip_header[16:])

    return transport_protocol, source, dest, ip_packet[ip_header_len:ip_length]
        
def decodeEthernet(packet):
    """ 
    parse Ethernet packet
    """

    eth_header_len = 14
    # ethernet header
    ethernet_header = packet[0:eth_header_len]

    (network_protocol, ) = struct.unpack(b'!12xH', ethernet_header)
    if network_protocol == NetworkProtocol.P802_1Q:
        # 802.1q, we need to skip two bytes and read another two bytes to get protocol/len
        type_or_len = packet[eth_header_len:eth_header_len + 4]
        eth_header_len += 4
        network_protocol, = struct.unpack(b'!2xH', type_or_len)
    if network_protocol == NetworkProtocol.PPPOE_SESSION:
        # skip PPPOE SESSION Header
        eth_header_len += 8
        type_or_len = packet[eth_header_len - 2:eth_header_len]
        network_protocol, = struct.unpack(b'!H', type_or_len)
    if network_protocol < 1536:
        # TODO n_protocol means package len
        pass
    return network_protocol, packet[eth_header_len:]
    
def decodeLinuxSSL(packet):
    """
    Parse linux sll packet
    """

    sll_header_len = 16

    # Linux cooked header
    linux_cooked = packet[0:sll_header_len]

    packet_type, link_type_address_type, link_type_address_len, link_type_address, n_protocol \
        = struct.unpack(b'!HHHQH', linux_cooked)
    return n_protocol, packet[sll_header_len:]
    
def decodePacket(packet, getTcp=False, getUdp=False):
    """
    """
    link_type, micro_second, link_packet = packet

    # decode network layer
    if link_type == LinkLayerType.ETHERNET:
        network_protocol, link_layer_body = decodeEthernet(link_packet)
    elif link_type == LinkLayerType.LINUX_SLL:
        network_protocol, link_layer_body = decodeLinuxSSL(link_packet)
    else:
        return None

    # decode ip layer
    if network_protocol == NetworkProtocol.IP or network_protocol == NetworkProtocol.PPP_IP:
        transport_protocol, source, dest, ip_body = decodeIpV4(network_protocol, link_layer_body)
    else:
        return None

    # decode transport
    if getTcp:
        if transport_protocol == TransportProtocol.TCP:
            source_port, dest_port, flags, seq, ack_seq, data = decodeTcp(ip_body)
            return (source, dest, source_port, dest_port, data)
            
    if getUdp:
        if transport_protocol == TransportProtocol.UDP:
            source_port, dest_port, lgth, udp_sum, data = decodeUdp(ip_body)
            return (source, dest, source_port, dest_port, data)
        
    return None