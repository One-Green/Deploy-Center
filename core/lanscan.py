import scapy.all as scapy


def arp(ip: str = '192.168.0.1/24') -> list:
    """
    Scan local network
    :param ip:
    :return:
    """
    arp_r = scapy.ARP(pdst=ip)
    br = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    request = br / arp_r
    answered, unanswered = scapy.srp(request, timeout=1)
    ip_list = []
    for i in answered:
        ip, mac = i[1].psrc, i[1].hwsrc
        ip_list.append(
            {'ip': ip, 'mac': mac}
        )
    return ip_list
