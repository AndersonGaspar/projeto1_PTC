# -*- coding: utf-8 -*-
import socket
import os
import codecs

#ERROS
#arq inexistente
ERROR_ARQ_INEX = 0x11
#permissao negada
ERROR_PER_NEG = 0x12
#sem espaco em disk
ERROR_DISK_SPACE = 0x13
#tentativas maxx
ERROR_TENT_MAX = 0x21
#queda de conexao
ERROR_LOST_CON = 0x22

def padhexa(s, length):
    return '0x' + s[2:].zfill(length)


def int2bit(num, length):
    bit = padhexa(hex(num), length)
    bit = bit[2:]
    bit = bytes.fromhex(bit)
    return bit


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def atributes(permision, path):
    packet = b'\x00\x00\x00\x00\x00'
    packet += int2bit(permision, 4)
    packet += codecs.getencoder('ascii')(path)[0]
    return packet


def data(n_seq, end_flag, data):
    packet = int2bit(0x10 + end_flag, 2)
    packet += int2bit(n_seq, 8)
    packet += data
    return packet


def ack(n_seq, end_flag):
    packet = int2bit(0x20 + end_flag, 2)
    packet += int2bit(n_seq, 8)
    return packet


def error(code):
    packet = b'\x30\x00\x00\x00\x00'
    packet += int2bit(code, 2)
    return packet


def send_packet(sock, address, packet, timeout, tries):
    tryout = 0
    sock.settimeout(timeout)
    while(tryout <= 10):
        try:
            sock.sendto(packet, address)
            tryout += 1
            packet_recv, addr = sock.recvfrom(517)
            type_code = packet_recv[0] & 0xF0
            if((type_code == 0x20) and (packet_recv[1:5] == packet[1:5])):
                return ((0, packet_recv))
            if(type_code == 0x30):
                return ((-1, int.from_bytes(packet_recv[5:], byteorder='big')))
        except socket.timeout:
            if(tryout == tries):
                return ((-1, ERROR_TENT_MAX))
        except :
            return ((-1, ERROR_LOST_CON))
    return ((-1, ERROR_TENT_MAX))


def receive_packet(sock, n_seq, filep, timeout, tries):
    tryout = 0
    sock.settimeout(timeout)
    n_seq_recv = 0
    while(tryout <= 10):
        try:
            packet_recv, addr = sock.recvfrom(517)
            n_seq_recv = (int.from_bytes(packet_recv[1:5], byteorder='big'))
            type_code = packet_recv[0] & 0xF0
            if((type_code == 0x00)):
                    #permission = data[5:7]
                    filename = packet_recv[7:]
                    try:
                        filep = open(filename.decode('ascii'), 'wb')
                        #os.chmod(filename.decode('ascii'), permission)
                        sock.sendto(ack(n_seq, (packet_recv[0] & 0x01)), addr)
                        return (0, filep)
                    except OSError:
                        packet = error(ERROR_PER_NEG)
                        sock.sendto(packet, addr)
                        return ((-1, ERROR_PER_NEG))
            if((type_code == 0x10) and (n_seq == n_seq_recv)):
                try:
                    filep.write(packet_recv[5:])
                    sock.sendto(ack(n_seq, (packet_recv[0] & 0x01)), addr)
                    return ((0, packet_recv))
                except Exception:
                    sock.sendto(error(ERROR_DISK_SPACE), addr)
                    return ((-1, ERROR_DISK_SPACE))
            if((type_code == 0x10) and (n_seq > n_seq_recv)):
                sock.sendto(ack(n_seq_recv, (packet_recv[0] & 0x01)), addr)
            tryout += 1
        except socket.timeout:
            if(tryout == tries):
                return ((-1, ERROR_TENT_MAX))
        except:
            return ((-1, ERROR_LOST_CON))
    return ((-1, ERROR_TENT_MAX))


def send(address, port, send_file, path, permission=0xFFFF, timeout=5, tries=10):
    exit_code = 0
    packet = ''
    n_seq = 0

# Create a scoket udp and bind using a interface conneted to internet using
# a random port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((get_ip_address(), 0))

# Open file and get permissions of file in case the user haven't set then.
    if (not(os.path.exists(send_file))):
        return ERROR_ARQ_INEX

    filep = open(send_file, 'rb')
    
    if(permission == 0xFFFF):
        permission = int(oct(os.stat(send_file)[0])[-1:-4:-1])

# Create a packet with atributes and send to the server.
    packet = atributes(permission, path)
    received = send_packet(sock, (address, port), packet, timeout, tries)
    if(received[0] < 0):
        return received[1]

# Read the file in packet of 512 Bytes and send to the server.
    while(True):
        data_p = filep.read(512)
        packet = data(n_seq, ((len(data_p) < 512) * 1), data_p)
        received = send_packet(sock, (address, port), packet, timeout, tries)
        if(received[0] < 0):
            return received[1]
        n_seq += 1
        if(len(data_p) < 512):
            break
    sock.close()
    return exit_code


def receive(address, port, timeout=5, tries=10):
    exit_code = 0
    end_flag = 0
    n_seq = 0

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((address, port))

    filep = receive_packet(sock, n_seq, None, None, tries)[1]

    while(end_flag == 0):
        received = receive_packet(sock, n_seq, filep, timeout, tries)
        if(received[0] == -1):
            return received[1]
        packet_recv = received[1]
        end_flag = packet_recv[0] & 0x01
        n_seq += 1
    filep.close()
    sock.close()
    return exit_code