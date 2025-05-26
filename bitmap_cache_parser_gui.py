#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import os.path
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from struct import pack, unpack
import threading
from queue import Queue
import time

class BMCContainer():
    BIN_FILE_HEADER = b"RDP8bmp\x00"
    BIN_CONTAINER = b".BIN"
    BMC_CONTAINER = b".BMC"
    TILE_HEADER_SIZE = {BMC_CONTAINER: 0x14, BIN_CONTAINER: 0xC}
    STRIPE_WIDTH = 64
    LOG_TYPES = ["[===]", "[+++]", "[---]", "[!!!]"]
    
    # Complete PALETTE definition from original code
    PALETTE = bytes(bytearray((0, 0, 0, 0, 0, 0, 128, 0, 0, 128, 0, 0, 0, 128, 128, 0, 128, 0, 0, 0, 128, 0, 128, 0, 128, 128, 0, 0, 192, 192, 192, 0, 192, 220, 192, 0, 240, 202, 166, 0, 0, 32, 64, 0, 0, 32, 96, 0, 0, 32, 128, 0, 0, 32, 160, 0, 0, 32, 192, 0, 0, 32, 224, 0, 0, 64, 0, 0, 0, 64, 32, 0, 0, 64, 64, 0, 0, 64, 96, 0, 0, 64, 128, 0, 0, 64, 160, 0, 0, 64, 192, 0, 0, 64, 224, 0, 0, 96, 0, 0, 0, 96, 32, 0, 0, 96, 64, 0, 0, 96, 96, 0, 0, 96, 128, 0, 0, 96, 160, 0, 0, 96, 192, 0, 0, 96, 224, 0, 0, 128, 0, 0, 0, 128, 32, 0, 0, 128, 64, 0, 0, 128, 96, 0, 0, 128, 128, 0, 0, 128, 160, 0, 0, 128, 192, 0, 0, 128, 224, 0, 0, 160, 0, 0, 0, 160, 32, 0, 0, 160, 64, 0, 0, 160, 96, 0, 0, 160, 128, 0, 0, 160, 160, 0, 0, 160, 192, 0, 0, 160, 224, 0, 0, 192, 0, 0, 0, 192, 32, 0, 0, 192, 64, 0, 0, 192, 96, 0, 0, 192, 128, 0, 0, 192, 160, 0, 0, 192, 192, 0, 0, 192, 224, 0, 0, 224, 0, 0, 0, 224, 32, 0, 0, 224, 64, 0, 0, 224, 96, 0, 0, 224, 128, 0, 0, 224, 160, 0, 0, 224, 192, 0, 0, 224, 224, 0, 64, 0, 0, 0, 64, 0, 32, 0, 64, 0, 64, 0, 64, 0, 96, 0, 64, 0, 128, 0, 64, 0, 160, 0, 64, 0, 192, 0, 64, 0, 224, 0, 64, 32, 0, 0, 64, 32, 32, 0, 64, 32, 64, 0, 64, 32, 96, 0, 64, 32, 128, 0, 64, 32, 160, 0, 64, 32, 192, 0, 64, 32, 224, 0, 64, 64, 0, 0, 64, 64, 32, 0, 64, 64, 64, 0, 64, 64, 96, 0, 64, 64, 128, 0, 64, 64, 160, 0, 64, 64, 192, 0, 64, 64, 224, 0, 64, 96, 0, 0, 64, 96, 32, 0, 64, 96, 64, 0, 64, 96, 96, 0, 64, 96, 128, 0, 64, 96, 160, 0, 64, 96, 192, 0, 64, 96, 224, 0, 64, 128, 0, 0, 64, 128, 32, 0, 64, 128, 64, 0, 64, 128, 96, 0, 64, 128, 128, 0, 64, 128, 160, 0, 64, 128, 192, 0, 64, 128, 224, 0, 64, 160, 0, 0, 64, 160, 32, 0, 64, 160, 64, 0, 64, 160, 96, 0, 64, 160, 128, 0, 64, 160, 160, 0, 64, 160, 192, 0, 64, 160, 224, 0, 64, 192, 0, 0, 64, 192, 32, 0, 64, 192, 64, 0, 64, 192, 96, 0, 64, 192, 128, 0, 64, 192, 160, 0, 64, 192, 192, 0, 64, 192, 224, 0, 64, 224, 0, 0, 64, 224, 32, 0, 64, 224, 64, 0, 64, 224, 96, 0, 64, 224, 128, 0, 64, 224, 160, 0, 64, 224, 192, 0, 64, 224, 224, 0, 128, 0, 0, 0, 128, 0, 32, 0, 128, 0, 64, 0, 128, 0, 96, 0, 128, 0, 128, 0, 128, 0, 160, 0, 128, 0, 192, 0, 128, 0, 224, 0, 128, 32, 0, 0, 128, 32, 32, 0, 128, 32, 64, 0, 128, 32, 96, 0, 128, 32, 128, 0, 128, 32, 160, 0, 128, 32, 192, 0, 128, 32, 224, 0, 128, 64, 0, 0, 128, 64, 32, 0, 128, 64, 64, 0, 128, 64, 96, 0, 128, 64, 128, 0, 128, 64, 160, 0, 128, 64, 192, 0, 128, 64, 224, 0, 128, 96, 0, 0, 128, 96, 32, 0, 128, 96, 64, 0, 128, 96, 96, 0, 128, 96, 128, 0, 128, 96, 160, 0, 128, 96, 192, 0, 128, 96, 224, 0, 128, 128, 0, 0, 128, 128, 32, 0, 128, 128, 64, 0, 128, 128, 96, 0, 128, 128, 128, 0, 128, 128, 160, 0, 128, 128, 192, 0, 128, 128, 224, 0, 128, 160, 0, 0, 128, 160, 32, 0, 128, 160, 64, 0, 128, 160, 96, 0, 128, 160, 128, 0, 128, 160, 160, 0, 128, 160, 192, 0, 128, 160, 224, 0, 128, 192, 0, 0, 128, 192, 32, 0, 128, 192, 64, 0, 128, 192, 96, 0, 128, 192, 128, 0, 128, 192, 160, 0, 128, 192, 192, 0, 128, 192, 224, 0, 128, 224, 0, 0, 128, 224, 32, 0, 128, 224, 64, 0, 128, 224, 96, 0, 128, 224, 128, 0, 128, 224, 160, 0, 128, 224, 192, 0, 128, 224, 224, 0, 192, 0, 0, 0, 192, 0, 32, 0, 192, 0, 64, 0, 192, 0, 96, 0, 192, 0, 128, 0, 192, 0, 160, 0, 192, 0, 192, 0, 192, 0, 224, 0, 192, 32, 0, 0, 192, 32, 32, 0, 192, 32, 64, 0, 192, 32, 96, 0, 192, 32, 128, 0, 192, 32, 160, 0, 192, 32, 192, 0, 192, 32, 224, 0, 192, 64, 0, 0, 192, 64, 32, 0, 192, 64, 64, 0, 192, 64, 96, 0, 192, 64, 128, 0, 192, 64, 160, 0, 192, 64, 192, 0, 192, 64, 224, 0, 192, 96, 0, 0, 192, 96, 32, 0, 192, 96, 64, 0, 192, 96, 96, 0, 192, 96, 128, 0, 192, 96, 160, 0, 192, 96, 192, 0, 192, 96, 224, 0, 192, 128, 0, 0, 192, 128, 32, 0, 192, 128, 64, 0, 192, 128, 96, 0, 192, 128, 128, 0, 192, 128, 160, 0, 192, 128, 192, 0, 192, 128, 224, 0, 192, 160, 0, 0, 192, 160, 32, 0, 192, 160, 64, 0, 192, 160, 96, 0, 192, 160, 128, 0, 192, 160, 160, 0, 192, 160, 192, 0, 192, 160, 224, 0, 192, 192, 0, 0, 192, 192, 32, 0, 192, 192, 64, 0, 192, 192, 96, 0, 192, 192, 128, 0, 192, 192, 160, 0, 240, 251, 255, 0, 164, 160, 160, 0, 128, 128, 128, 0, 0, 0, 255, 0, 0, 255, 0, 0, 0, 255, 255, 0, 255, 0, 0, 0, 255, 0, 255, 0, 255, 255, 0, 0, 255, 255, 255, 0)))
    
    COLOR_BLACK = b"\x00"
    COLOR_WHITE = b"\xFF"
    
    def __init__(self, verbose=False, count=0, old=False, big=False, width=64, log_callback=None):
        self.bdat = ""
        self.o_bmps = []
        self.bmps = []
        self.btype = None
        self.cnt = count
        self.fname = None
        self.oldsave = old
        self.pal = False
        self.verb = verbose
        self.big = big
        self.STRIPE_WIDTH = width
        self.log_callback = log_callback
        
        if count > 0:
            self.b_log(True, 2, f"At most {count} tiles will be processed.")
        if old:
            self.b_log(True, 2, "Old data will also be saved in separate files.")
    
    def b_log(self, verbose, ltype, lmsg):
        if not verbose or self.verb:
            log_message = f"{self.LOG_TYPES[ltype]} {lmsg}"
            if self.log_callback:
                self.log_callback(log_message)
            else:
                print(log_message)
        return True

    def b_import(self, fname):
        """Import BMCache file - exact copy from original"""
        if len(self.bdat) > 0:
            self.b_log(False, 3, "Data is already waiting to be processed; aborting.")
            return False
        
        try:
            with open(fname, "rb") as f:
                self.bdat = memoryview(f.read())
        except Exception as e:
            self.b_log(False, 3, f"Unable to retrieve file contents; aborting. Error: {str(e)}")
            return False
        
        if len(self.bdat) == 0:
            self.b_log(False, 3, "Unable to retrieve file contents; aborting.")
            return False
        
        self.fname = fname
        self.btype = self.BMC_CONTAINER
        
        if self.bdat[:len(self.BIN_FILE_HEADER)] == self.BIN_FILE_HEADER:
            self.b_log(True, 2, f"Subsequent header version: {unpack('<L', self.bdat[len(self.BIN_FILE_HEADER):len(self.BIN_FILE_HEADER)+4])[0]}.")
            self.bdat = self.bdat[len(self.BIN_FILE_HEADER)+4:]
            self.btype = self.BIN_CONTAINER
        
        self.b_log(True, 0, f"Successfully loaded '{self.fname}' as a {self.btype.decode()} container.")
        return True

    def b_process(self):
        """Process the imported BMCache data - exact copy from original"""
        if len(self.bdat) == 0:
            self.b_log(False, 3, "Nothing to process.")
            return False
        
        bl = 0
        while len(self.bdat) > 0:
            old = False
            o_bmp = ""
            t_hdr = self.bdat[:self.TILE_HEADER_SIZE[self.btype]]
            key1, key2, t_width, t_height = unpack("<LLHH", t_hdr[:0xC])
            
            if self.btype == self.BIN_CONTAINER:
                bl = 4*t_width*t_height
                t_bmp = self.b_parse_rgb32b(self.bdat[len(t_hdr):len(t_hdr)+bl].tobytes())
            elif self.btype == self.BMC_CONTAINER:
                t_bmp = ""
                t_len, t_params = unpack("<LL", t_hdr[-0x8:])
                if t_params & 0x08:  # Compression bit flag
                    if bl == 0:
                        if "22.bmc" in self.fname:
                            bl = 64*64*2
                        elif "24.bmc" in self.fname:
                            bl = 64*64*4
                        elif "2.bmc" in self.fname:
                            bl = 64*64
                        else:
                            for b in [1, 2, 4]:
                                if len(self.bdat) < len(t_hdr)+64*64*b+8:
                                    break
                                elif unpack("<H", self.bdat[len(t_hdr)+64*64*b+8:][:2])[0] == 64:
                                    bl = 64*64*b
                                    break
                            if bl == 0:
                                self.b_log(False, 3, "Unable to determine data pattern size; exiting before throwing any error!")
                                return False
                    o_bmp = b""
                    t_bmp = self.b_uncompress(self.bdat[len(t_hdr):len(t_hdr)+t_len].tobytes(), bl//(64*64))
                    if len(t_bmp) > 0:
                        if len(t_bmp) != t_width*t_height*bl//(64*64):
                            self.b_log(False, 3, f"Uncompressed tile data seems bogus (uncompressed {len(t_bmp)} bytes while expecting {t_width*t_height*bl//(64*64)}). Discarding tile.")
                            t_bmp = b""
                        else:
                            t_bmp = self.b_parse_rgb565(t_bmp)
                else:
                    cf = t_len//(t_width*t_height)
                    if cf == 4:
                        t_bmp = self.b_parse_rgb32b(self.bdat[len(t_hdr):len(t_hdr)+cf*t_width*t_height].tobytes())
                        if t_height != 64:
                            old = True
                            o_bmp = self.b_parse_rgb32b(self.bdat[len(t_hdr)+cf*t_width*t_height:len(t_hdr)+cf*64*64].tobytes())
                    elif cf == 3:
                        t_bmp = self.b_parse_rgb24b(self.bdat[len(t_hdr):len(t_hdr)+cf*t_width*t_height].tobytes())
                        if t_height != 64:
                            old = True
                            o_bmp = self.b_parse_rgb24b(self.bdat[len(t_hdr)+cf*t_width*t_height:len(t_hdr)+cf*64*64].tobytes())
                    elif cf == 2:
                        t_bmp = self.b_parse_rgb565(self.bdat[len(t_hdr):len(t_hdr)+cf*t_width*t_height].tobytes())
                        if t_height != 64:
                            old = True
                            o_bmp = self.b_parse_rgb565(self.bdat[len(t_hdr)+cf*t_width*t_height:len(t_hdr)+cf*64*64].tobytes())
                    elif cf == 1:
                        self.pal = True
                        t_bmp = self.PALETTE+self.bdat[len(t_hdr):len(t_hdr)+cf*t_width*t_height].tobytes()
                        if t_height != 64:
                            old = True
                            o_bmp = self.PALETTE+self.bdat[len(t_hdr)+cf*t_width*t_height:len(t_hdr)+cf*64*64].tobytes()
                    else:
                        self.b_log(False, 3, f"Unexpected bpp ({8*cf}) found during processing; aborting.")
                        return False
                    bl = cf*64*64
            
            if len(t_bmp) > 0:
                self.bmps.append(t_bmp)
                self.o_bmps.append(o_bmp)
                if len(self.bmps)%100 == 0:
                    self.b_log(True, 1, f"{len(self.bmps)} tiles successfully extracted so far.")
            
            self.bdat = self.bdat[len(t_hdr)+bl:]
            if self.cnt != 0 and len(self.bmps) == self.cnt:
                break
        
        self.b_log(False, 0, f"{len(self.bmps)} tiles successfully extracted in the end.")
        return True

    def b_parse_rgb565(self, data):
        """Parse RGB565 data - exact copy from original"""
        d_out = b""
        while len(data) > 0:
            pxl = unpack("<H", data[:2])[0]
            bl = ((pxl>>8)&0xF8)|((pxl>>13)&0x07)
            gr = ((pxl>>3)&0xFC)|((pxl>>9)&0x03)
            re = ((pxl<<3)&0xF8)|((pxl>>2)&0x07)
            d_out += bytearray((re, gr, bl, 255))
            data = data[2:]
        return bytes(d_out)

    def b_parse_rgb32b(self, data):
        """Parse RGB32 data - exact copy from original"""
        d_out = b""
        d_buf = b""
        while len(data) > 0:
            if self.btype == self.BIN_CONTAINER:
                d_buf += data[:3]+b"\xFF"
                if len(d_buf) == 256:
                    d_out = d_buf+d_out
                    d_buf = b""
            else:
                d_out += data[:3]+b"\xFF"
            data = data[4:]
        return d_out

    def b_parse_rgb24b(self, data):
        """Parse RGB24 data - exact copy from original"""
        d_out = b""
        d_buf = b""
        while len(data) > 0:
            if self.btype == self.BIN_CONTAINER:
                d_buf += data[:3]+b"\xFF"
                if len(d_buf) == 256:
                    d_out = d_buf+d_out
                    d_buf = b""
            else:
                d_out += data[:3]+b"\xFF"
            data = data[3:]
        return d_out

    def b_unrle(self, data):
        """RLE decompression helper - exact copy from original"""
        if len(data) == 0:
            return (-1, 1, 0)
        x = ord(data[0:1])
        if (x&0xF0) == 0xF0:
            if x in [0xF5, 0xFB, 0xFC, 0xFF]:
                return (-1, 2, x)
            elif x in [0xFD, 0xFE]:
                return (x, 0, 1)
            elif x in [0xF9, 0xFA]:
                return (x, 8, 1)
            elif len(data) < 3:
                return (-1, 1, 0)
            else:
                c = unpack("<H", data[1:3])[0]
                return (x, c, 3)
        elif (x&0xE0) == 0xA0:
            return (-1, 2, x)
        else:
            if (x&0x80) == 0x00 or (x&0xE0) == 0x80:
                c = x&0x1F
                x = x&0xE0
                o = 32
            else:
                c = x&0x0F
                x = x&0xF0
                o = 16
            if x in [0x40, 0xD0]:
                c *= 8
                o = 1
            if c == 0:
                if len(data) < 2:
                    return (-1, 1, 0)
                else:
                    c = ord(data[1:2])+o
                o = 2
            else:
                o = 1
            return (x, c, o)
        return (-1, 3, 0)

    def b_uncompress(self, data, bbp):
        """Uncompress bitmap data - exact copy from original"""
        d_out = b""
        bro = -1
        fgc = self.COLOR_WHITE*bbp
        
        while len(data) > 0:
            cmd, rl, sz = self.b_unrle(data[:3])
            if cmd == -1:
                if rl == 1:
                    self.b_log(False, 3, "Unexpected end of compressed stream. Skipping tile.")
                elif rl == 2:
                    self.b_log(False, 3, f"Unexpected decompression command encountered (0x{sz:02X}). Skipping tile.")
                else:
                    self.b_log(False, 3, "Unhandled case in decompression routine. Skipping tile.")
                return b""
            
            data = data[sz:]
            
            if cmd in [0x00, 0xF0]:
                if len(d_out) < 64*bbp:
                    if bro == 0:
                        d_out += fgc
                        rl -= 1
                    d_out += (self.COLOR_BLACK*bbp)*rl
                else:
                    if bro > 0:
                        c = d_out[-64*bbp:][:bbp]
                        for i in range(bbp):
                            d_out += bytearray((ord(c[i:i+1])^ord(fgc[i:i+1]), ))
                        rl -= 1
                    while rl > 0:
                        d_out += d_out[-64*bbp:][:bbp]
                        rl -= 1
                bro = len(d_out)//(64*bbp)
            elif cmd in [0x20, 0xC0, 0xF1, 0xF6]:
                if cmd in [0xC0, 0xF6]:
                    if len(data) < bbp:
                        self.b_log(False, 3, "Unexpected end of compressed stream. Skipping tile.")
                        return b""
                    fgc = data[:bbp]
                    data = data[bbp:]
                if len(d_out) < 64*bbp:
                    d_out += fgc*rl
                else:
                    while rl > 0:
                        c = d_out[-64*bbp:][:bbp]
                        for i in range(bbp):
                            d_out += bytearray((ord(c[i:i+1])^ord(fgc[i:i+1]), ))
                        rl -= 1
            elif cmd in [0xE0, 0xF8]:
                if len(data) < 2*bbp:
                    self.b_log(False, 3, "Unexpected end of compressed stream. Skipping tile.")
                    return b""
                d_out += data[:2*bbp]*rl
                data = data[2*bbp:]
            elif cmd in [0x60, 0xF3]:
                if len(data) < bbp:
                    self.b_log(False, 3, "Unexpected end of compressed stream. Skipping tile.")
                    return b""
                d_out += data[:bbp]*rl
                data = data[bbp:]
            elif cmd in [0x40, 0xD0, 0xF2, 0xF7, 0xF9, 0xFA]:
                if cmd in [0xD0, 0xF7]:
                    if len(data) < bbp:
                        self.b_log(False, 3, "Unexpected end of compressed stream. Skipping tile.")
                        return b""
                    fgc = data[:bbp]
                    data = data[bbp:]
                if cmd == 0xF9:
                    msk = b"\x03"
                    ml = 1
                elif cmd == 0xFA:
                    msk = b"\x05"
                    ml = 1
                else:
                    if (rl%8) != 0:
                        ml = (rl//8)+1
                    else:
                        ml = rl//8
                    if len(data) < ml:
                        self.b_log(False, 3, "Unexpected end of compressed stream. Skipping tile.")
                        return b""
                    msk = data[:ml]
                    data = data[ml:]
                k = 0
                while rl > 0:
                    if (k%8) == 0:
                        m = ord(msk[k//8:][:1])
                    b = m&(0x1<<(k%8))
                    if len(d_out) < 64*bbp:
                        if b == 0:
                            d_out += (self.COLOR_BLACK*bbp)
                        else:
                            d_out += fgc
                    else:
                        c = d_out[-64*bbp:][:bbp]
                        if b == 0:
                            d_out += c
                        else:
                            for i in range(bbp):
                                d_out += bytearray((ord(c[i:i+1])^ord(fgc[i:i+1]), ))
                    k += 1
                    rl -= 1
            elif cmd in [0x80, 0xF4]:
                if len(data) < bbp*rl:
                    self.b_log(False, 3, "Unexpected end of compressed stream. Skipping tile.")
                    return b""
                d_out += data[:rl*bbp]
                data = data[rl*bbp:]
            elif cmd == 0xFD:
                d_out += (self.COLOR_WHITE*bbp)
            elif cmd == 0xFE:
                d_out += (self.COLOR_BLACK*bbp)
            else:
                self.b_log(False, 3, f"Unhandled decompression command (0x{cmd:02X}). Skipping tile.")
                return b""
            if cmd not in [0x00, 0xF0]:
                bro = -1
        return d_out

    def b_export(self, dname):
        """Export processed bitmaps - exact copy from original"""
        if not os.path.isdir(dname):
            self.b_log(False, 3, "Destination must be an already existing folder.")
            return False
        
        fname_base = os.path.basename(self.fname)
        for i in range(len(self.bmps)):
            self.b_write(os.path.join(dname, f"{fname_base}_{i:04d}.bmp"), 
                        self.b_export_bmp(64, len(self.bmps[i])//256, self.bmps[i]))
            if self.oldsave and i < len(self.o_bmps) and len(self.o_bmps[i]) > 0:
                self.b_write(os.path.join(dname, f"{fname_base}_old_{i:04d}.bmp"), 
                            self.b_export_bmp(64, len(self.o_bmps[i])//256, self.o_bmps[i]))
        
        self.b_log(False, 0, f"Successfully exported {len(self.bmps)} files.")
        
        if self.big:
            pad = b"\xFF"
            if not self.pal:
                pad *= 4
            for i in range(len(self.bmps)):
                if self.pal:
                    self.bmps[i] = self.bmps[i][len(self.PALETTE):]
                while len(self.bmps[i]) < 64*64*len(pad):
                    self.bmps[i] += pad*64
            
            w = 64*len(self.bmps)
            h = 64
            if len(self.bmps)//self.STRIPE_WIDTH > 0:
                m = len(self.bmps)%self.STRIPE_WIDTH
                if m != 0:
                    for i in range(self.STRIPE_WIDTH-m):
                        self.bmps.append(pad*64*64)
                w = self.STRIPE_WIDTH*64
                h *= len(self.bmps)//self.STRIPE_WIDTH
            
            c_bmp = b"" if not self.pal else self.PALETTE
            if self.btype == self.BIN_CONTAINER:
                collage_builder = (lambda x, a=self, PAD=len(pad), WIDTH=range(w // 64): b''.join([b''.join([a.bmps[a.STRIPE_WIDTH*(x+1)-1-k][64*PAD*j:64*PAD*(j+1)] for k in WIDTH]) for j in range(64)]))
            else:
                collage_builder = (lambda x, a=self, PAD=len(pad), WIDTH=range(w // 64): b''.join([b''.join([a.bmps[a.STRIPE_WIDTH*x+k][64*PAD*j:64*PAD*(j+1)] for k in WIDTH]) for j in range(64)]))
            
            c_bmp += b''.join(map(collage_builder, range(h//64)))
            self.b_write(os.path.join(dname, f"{fname_base}_collage.bmp"), 
                        self.b_export_bmp(w, h, c_bmp))
            self.b_log(False, 0, "Successfully exported collage file.")
        
        return True

    def b_export_bmp(self, width, height, data):
        """Export BMP format - exact copy from original"""
        if not self.pal:
            return b"BM"+pack("<L", len(data)+122)+b"\x00\x00\x00\x00\x7A\x00\x00\x00\x6C\x00\x00\x00"+pack("<L", width)+pack("<L", height)+b"\x01\x00\x20\x00\x03\x00\x00\x00"+pack("<L", len(data))+b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x00\x00\xFF\x00\x00\xFF\x00\x00\x00\x00\x00\x00\xFF niW"+(b"\x00"*36)+b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"+data
        else:
            return b"BM"+pack("<L", len(data)+0x36)+b"\x00\x00\x00\x00\x36\x04\x00\x00\x28\x00\x00\x00"+pack("<L", width)+pack("<L", height)+b"\x01\x00\x08\x00\x00\x00\x00\x00"+pack("<L", len(data)-0x400)+b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"+data

    def b_write(self, fname, data):
        """Write file - exact copy from original"""
        with open(fname, "wb") as f:
            f.write(data)
        return True

    def b_flush(self):
        """Clear processed data - exact copy from original"""
        self.bdat = ""
        self.bmps = []
        self.o_bmps = []
        return True

# GUI Code remains exactly the same as before
class BMCacheParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RDP Bitmap Cache Parser by sujay_adkesar")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.source_path = tk.StringVar()
        self.dest_path = tk.StringVar()
        self.count_var = tk.IntVar(value=0)
        self.verbose_var = tk.BooleanVar(value=False)
        self.old_var = tk.BooleanVar(value=False)
        self.bitmap_var = tk.BooleanVar(value=False)
        self.width_var = tk.IntVar(value=64)
        self.kape_var = tk.BooleanVar(value=False)
        
        self.processing = False
        self.log_queue = Queue()
        
        self.create_widgets()
        self.setup_layout()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="RDP Bitmap Cache Parser", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Source selection
        ttk.Label(main_frame, text="Source:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        
        source_frame = ttk.Frame(main_frame)
        source_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        source_frame.columnconfigure(0, weight=1)
        
        self.source_entry = ttk.Entry(source_frame, textvariable=self.source_path, 
                                     font=('Arial', 9))
        self.source_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(source_frame, text="Browse File", 
                  command=self.browse_source_file).grid(row=0, column=1, padx=2)
        ttk.Button(source_frame, text="Browse Folder", 
                  command=self.browse_source_folder).grid(row=0, column=2, padx=2)
        
        # Destination selection
        ttk.Label(main_frame, text="Destination:", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        
        dest_frame = ttk.Frame(main_frame)
        dest_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        dest_frame.columnconfigure(0, weight=1)
        
        self.dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_path, 
                                   font=('Arial', 9))
        self.dest_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(dest_frame, text="Browse", 
                  command=self.browse_destination).grid(row=0, column=1)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Processing Options", 
                                      padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                          pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # Count option
        ttk.Label(options_frame, text="Max tiles to extract:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        count_spin = ttk.Spinbox(options_frame, from_=0, to=10000, 
                                textvariable=self.count_var, width=10)
        count_spin.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        ttk.Label(options_frame, text="(0 = extract all)").grid(
            row=0, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Width option
        ttk.Label(options_frame, text="Collage width (tiles):").grid(
            row=1, column=0, sticky=tk.W, pady=2)
        width_spin = ttk.Spinbox(options_frame, from_=1, to=256, 
                                textvariable=self.width_var, width=10)
        width_spin.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Checkboxes
        ttk.Checkbutton(options_frame, text="Verbose output", 
                       variable=self.verbose_var).grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Extract old bitmap data", 
                       variable=self.old_var).grid(row=2, column=1, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Create collage bitmap", 
                       variable=self.bitmap_var).grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="KAPE mode (separate folders)", 
                       variable=self.kape_var).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                           pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.process_button = ttk.Button(button_frame, text="Start Processing", 
                                        command=self.start_processing, 
                                        style='Accent.TButton')
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_processing, 
                                     state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Clear Log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Exit", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                      pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                                 font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def setup_layout(self):
        # Configure custom styles
        self.style.configure('Accent.TButton', foreground='white', 
                           background='#0078d4', focuscolor='none')
        self.style.map('Accent.TButton', 
                      background=[('active', '#106ebe'), ('pressed', '#005a9e')])
        
    def browse_source_file(self):
        filename = filedialog.askopenfilename(
            title="Select BMCache file",
            filetypes=[("BMCache files", "*.bmc *.bin"), ("All files", "*.*")]
        )
        if filename:
            self.source_path.set(filename)
    
    def browse_source_folder(self):
        folder = filedialog.askdirectory(title="Select folder containing BMCache files")
        if folder:
            self.source_path.set(folder)
    
    def browse_destination(self):
        folder = filedialog.askdirectory(title="Select destination folder")
        if folder:
            self.dest_path.set(folder)
    
    def log_message(self, message):
        self.log_queue.put(message)
    
    def update_log(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.root.update_idletasks()
        except:
            pass
        
        if self.processing:
            self.root.after(100, self.update_log)
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def validate_inputs(self):
        if not self.source_path.get():
            messagebox.showerror("Error", "Please select a source file or folder.")
            return False
        
        if not self.dest_path.get():
            messagebox.showerror("Error", "Please select a destination folder.")
            return False
        
        if not os.path.exists(self.source_path.get()):
            messagebox.showerror("Error", "Source path does not exist.")
            return False
        
        if not os.path.exists(self.dest_path.get()):
            messagebox.showerror("Error", "Destination folder does not exist.")
            return False
        
        return True
    
    def start_processing(self):
        if not self.validate_inputs():
            return
        
        self.processing = True
        self.process_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_var.set("Processing...")
        self.progress_bar.start()
        
        # Start processing in a separate thread
        self.process_thread = threading.Thread(target=self.process_files)
        self.process_thread.daemon = True
        self.process_thread.start()
        
        # Start log update loop
        self.update_log()
    
    def stop_processing(self):
        self.processing = False
        self.process_button.config(state='disabled')
        self.stop_button.config(state='disabled')
        self.progress_var.set("Stopped")
        self.progress_bar.stop()
    
    def process_files(self):
        try:
            # Create BMCContainer with GUI callback
            bmcc = BMCContainer(
                verbose=self.verbose_var.get(),
                count=self.count_var.get() if self.count_var.get() > 0 else 0,
                old=self.old_var.get(),
                big=self.bitmap_var.get(),
                width=self.width_var.get(),
                log_callback=self.log_message
            )
            
            src_files = []
            source = self.source_path.get()
            
            if os.path.isdir(source):
                self.log_message("[+++] Processing a directory...")
                for root, dirs, files in os.walk(source):
                    for f in files:
                        if f.rsplit(".", 1)[-1].upper() in ["BIN", "BMC"]:
                            file_path = os.path.join(root, f)
                            if self.verbose_var.get():
                                self.log_message(f"[---] File '{file_path}' has been found.")
                            src_files.append(file_path)
                
                if len(src_files) == 0:
                    self.log_message(f"No suitable files were found under '{source}' directory.")
                    return
            else:
                self.log_message(f"[+++] Processing a single file: '{source}'.")
                src_files.append(source)
            
            total_files = len(src_files)
            for i, src in enumerate(src_files):
                if not self.processing:
                    break
                
                self.progress_var.set(f"Processing file {i+1}/{total_files}: {os.path.basename(src)}")
                self.log_message(f"[+++] Processing file: '{src}'")
                
                if bmcc.b_import(src):
                    destination = self.dest_path.get()
                    
                    if self.kape_var.get():
                        destination = src.replace("\\", "_").replace("//", "_").replace(":", "_")
                        destination = destination.replace("_AppData_Local_Microsoft_Terminal Server Client_Cache", "")
                        destination = os.path.join(self.dest_path.get(), destination)
                        if not os.path.exists(destination):
                            os.makedirs(destination)
                    
                    bmcc.b_process()
                    bmcc.b_export(destination)
                    bmcc.b_flush()
            
            self.log_message("[===] Processing completed successfully!")
            
        except Exception as e:
            self.log_message(f"[!!!] Error during processing: {str(e)}")
        finally:
            self.root.after(0, self.processing_finished)
    
    def processing_finished(self):
        self.processing = False
        self.process_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_var.set("Completed")
        self.progress_bar.stop()
        messagebox.showinfo("Processing Complete", "File processing has been completed!")

def main():
    root = tk.Tk()
    app = BMCacheParserGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
