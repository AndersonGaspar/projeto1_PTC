# -*- coding: utf-8 -*-
import socket
import sys


def padhexa(s, length):
    return '0x' + s[2:].zfill(length)


def int2bit(num, length):
    bit = padhexa(hex(num), length)
    bit = bit[2:]
    bit = bytes.fromhex(bit)
    return bit


def atributes(permision, path):
    packet = '\x00\x00\x00\x00\x00'
    int.from_bytes

    return packet


def data(n_seq, end_flag, data):
    type_code = int2bit(0x10 + end_flag, 2)
    n_sec_padded = int2bit(n_seq, 8)
    packet = type_code + n_sec_padded + data

    return packet


def ack(n_seq, end_flag):
    type_code = int2bit(0x20 + end_flag, 2)
    n_sec_padded = int2bit(n_seq, 8)
    packet = type_code + n_sec_padded
    return packet


def error(code):
    error_code = int2bit(code, 2)
    packet = '\x30\x00\x00\x00\x00' + error_code

    return packet


def send(send_file, path, address, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    exit_code = 0
    packet = ''
    n_seq = 0
    filep = open(send_file, 'rb')
    data_p = filep.read(512)

    sock.sendto(packet.atributes, ("127.0.0.1", 5506))

    while(True):
        packet = data(n_seq, 0, data_p)
        sock.sendto(packet, ("127.0.0.1", 5506))
        data_p = filep.read(512)
        n_seq += 1
        print (n_seq)
        if(len(data_p) < 512):
            packet = data(n_seq, 1, data_p)
            sock.sendto(packet, ("127.0.0.1", 5506))
            print ('FIN \n')
            break
    return exit_code


def receive(address, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 5506))
    exit_code = 0
    end_flag = 0
    filep = open('receive_file.jpg', 'wb')
    while(end_flag == 0):
        data, addr = sock.recvfrom(517)
        overhead = data[0:4]
        #print(overhead)
        filep.write(data[5:])
        end_flag = overhead[0] & 0x01
        #print (end_flag)
    return exit_code