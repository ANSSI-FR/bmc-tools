#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse, os, os.path, sys
from struct import pack, unpack

class BMCContainer():
	BIN_FILE_HEADER = b"RDP8bmp\x00"
	BIN_CONTAINER = b".BIN"
	BMC_CONTAINER = b".BMC"
	TILE_HEADER_SIZE = {BMC_CONTAINER: 0x14, BIN_CONTAINER: 0xC}
	STRIPE_WIDTH = 64
	LOG_TYPES = ["[===]", "[+++]", "[---]", "[!!!]"]
	PALETTE = bytes(bytearray((0, 0, 0, 0, 0, 0, 128, 0, 0, 128, 0, 0, 0, 128, 128, 0, 128, 0, 0, 0, 128, 0, 128, 0, 128, 128, 0, 0, 192, 192, 192, 0, 192, 220, 192, 0, 240, 202, 166, 0, 0, 32, 64, 0, 0, 32, 96, 0, 0, 32, 128, 0, 0, 32, 160, 0, 0, 32, 192, 0, 0, 32, 224, 0, 0, 64, 0, 0, 0, 64, 32, 0, 0, 64, 64, 0, 0, 64, 96, 0, 0, 64, 128, 0, 0, 64, 160, 0, 0, 64, 192, 0, 0, 64, 224, 0, 0, 96, 0, 0, 0, 96, 32, 0, 0, 96, 64, 0, 0, 96, 96, 0, 0, 96, 128, 0, 0, 96, 160, 0, 0, 96, 192, 0, 0, 96, 224, 0, 0, 128, 0, 0, 0, 128, 32, 0, 0, 128, 64, 0, 0, 128, 96, 0, 0, 128, 128, 0, 0, 128, 160, 0, 0, 128, 192, 0, 0, 128, 224, 0, 0, 160, 0, 0, 0, 160, 32, 0, 0, 160, 64, 0, 0, 160, 96, 0, 0, 160, 128, 0, 0, 160, 160, 0, 0, 160, 192, 0, 0, 160, 224, 0, 0, 192, 0, 0, 0, 192, 32, 0, 0, 192, 64, 0, 0, 192, 96, 0, 0, 192, 128, 0, 0, 192, 160, 0, 0, 192, 192, 0, 0, 192, 224, 0, 0, 224, 0, 0, 0, 224, 32, 0, 0, 224, 64, 0, 0, 224, 96, 0, 0, 224, 128, 0, 0, 224, 160, 0, 0, 224, 192, 0, 0, 224, 224, 0, 64, 0, 0, 0, 64, 0, 32, 0, 64, 0, 64, 0, 64, 0, 96, 0, 64, 0, 128, 0, 64, 0, 160, 0, 64, 0, 192, 0, 64, 0, 224, 0, 64, 32, 0, 0, 64, 32, 32, 0, 64, 32, 64, 0, 64, 32, 96, 0, 64, 32, 128, 0, 64, 32, 160, 0, 64, 32, 192, 0, 64, 32, 224, 0, 64, 64, 0, 0, 64, 64, 32, 0, 64, 64, 64, 0, 64, 64, 96, 0, 64, 64, 128, 0, 64, 64, 160, 0, 64, 64, 192, 0, 64, 64, 224, 0, 64, 96, 0, 0, 64, 96, 32, 0, 64, 96, 64, 0, 64, 96, 96, 0, 64, 96, 128, 0, 64, 96, 160, 0, 64, 96, 192, 0, 64, 96, 224, 0, 64, 128, 0, 0, 64, 128, 32, 0, 64, 128, 64, 0, 64, 128, 96, 0, 64, 128, 128, 0, 64, 128, 160, 0, 64, 128, 192, 0, 64, 128, 224, 0, 64, 160, 0, 0, 64, 160, 32, 0, 64, 160, 64, 0, 64, 160, 96, 0, 64, 160, 128, 0, 64, 160, 160, 0, 64, 160, 192, 0, 64, 160, 224, 0, 64, 192, 0, 0, 64, 192, 32, 0, 64, 192, 64, 0, 64, 192, 96, 0, 64, 192, 128, 0, 64, 192, 160, 0, 64, 192, 192, 0, 64, 192, 224, 0, 64, 224, 0, 0, 64, 224, 32, 0, 64, 224, 64, 0, 64, 224, 96, 0, 64, 224, 128, 0, 64, 224, 160, 0, 64, 224, 192, 0, 64, 224, 224, 0, 128, 0, 0, 0, 128, 0, 32, 0, 128, 0, 64, 0, 128, 0, 96, 0, 128, 0, 128, 0, 128, 0, 160, 0, 128, 0, 192, 0, 128, 0, 224, 0, 128, 32, 0, 0, 128, 32, 32, 0, 128, 32, 64, 0, 128, 32, 96, 0, 128, 32, 128, 0, 128, 32, 160, 0, 128, 32, 192, 0, 128, 32, 224, 0, 128, 64, 0, 0, 128, 64, 32, 0, 128, 64, 64, 0, 128, 64, 96, 0, 128, 64, 128, 0, 128, 64, 160, 0, 128, 64, 192, 0, 128, 64, 224, 0, 128, 96, 0, 0, 128, 96, 32, 0, 128, 96, 64, 0, 128, 96, 96, 0, 128, 96, 128, 0, 128, 96, 160, 0, 128, 96, 192, 0, 128, 96, 224, 0, 128, 128, 0, 0, 128, 128, 32, 0, 128, 128, 64, 0, 128, 128, 96, 0, 128, 128, 128, 0, 128, 128, 160, 0, 128, 128, 192, 0, 128, 128, 224, 0, 128, 160, 0, 0, 128, 160, 32, 0, 128, 160, 64, 0, 128, 160, 96, 0, 128, 160, 128, 0, 128, 160, 160, 0, 128, 160, 192, 0, 128, 160, 224, 0, 128, 192, 0, 0, 128, 192, 32, 0, 128, 192, 64, 0, 128, 192, 96, 0, 128, 192, 128, 0, 128, 192, 160, 0, 128, 192, 192, 0, 128, 192, 224, 0, 128, 224, 0, 0, 128, 224, 32, 0, 128, 224, 64, 0, 128, 224, 96, 0, 128, 224, 128, 0, 128, 224, 160, 0, 128, 224, 192, 0, 128, 224, 224, 0, 192, 0, 0, 0, 192, 0, 32, 0, 192, 0, 64, 0, 192, 0, 96, 0, 192, 0, 128, 0, 192, 0, 160, 0, 192, 0, 192, 0, 192, 0, 224, 0, 192, 32, 0, 0, 192, 32, 32, 0, 192, 32, 64, 0, 192, 32, 96, 0, 192, 32, 128, 0, 192, 32, 160, 0, 192, 32, 192, 0, 192, 32, 224, 0, 192, 64, 0, 0, 192, 64, 32, 0, 192, 64, 64, 0, 192, 64, 96, 0, 192, 64, 128, 0, 192, 64, 160, 0, 192, 64, 192, 0, 192, 64, 224, 0, 192, 96, 0, 0, 192, 96, 32, 0, 192, 96, 64, 0, 192, 96, 96, 0, 192, 96, 128, 0, 192, 96, 160, 0, 192, 96, 192, 0, 192, 96, 224, 0, 192, 128, 0, 0, 192, 128, 32, 0, 192, 128, 64, 0, 192, 128, 96, 0, 192, 128, 128, 0, 192, 128, 160, 0, 192, 128, 192, 0, 192, 128, 224, 0, 192, 160, 0, 0, 192, 160, 32, 0, 192, 160, 64, 0, 192, 160, 96, 0, 192, 160, 128, 0, 192, 160, 160, 0, 192, 160, 192, 0, 192, 160, 224, 0, 192, 192, 0, 0, 192, 192, 32, 0, 192, 192, 64, 0, 192, 192, 96, 0, 192, 192, 128, 0, 192, 192, 160, 0, 240, 251, 255, 0, 164, 160, 160, 0, 128, 128, 128, 0, 0, 0, 255, 0, 0, 255, 0, 0, 0, 255, 255, 0, 255, 0, 0, 0, 255, 0, 255, 0, 255, 255, 0, 0, 255, 255, 255, 0)))
	def __init__(self, verbose=False, count=0, old=False, big=False, width=64):
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
		if count > 0:
			self.b_log(sys.stdout, True, 2, "At most %d tiles will be processed." % (count))
		if old:
			self.b_log(sys.stdout, True, 2, "Old data will also be saved in separate files.")
	def b_log(self, stream, verbose, ltype, lmsg):
		if not verbose or self.verb:
			stream.write("%s %s%s" % (self.LOG_TYPES[ltype], lmsg, os.linesep))
		return True
	def b_import(self, fname):
		if len(self.bdat) > 0:
			self.b_log(sys.stderr, False, 3, "Data is already waiting to be processed; aborting.")
			return False
		with open(fname, "rb") as f:
			self.bdat = f.read()
		if len(self.bdat) == 0:
			self.b_log(sys.stderr, False, 3, "Unable to retrieve file contents; aborting.")
			return False
		self.fname = fname
		self.btype = self.BMC_CONTAINER
		if self.bdat[:len(self.BIN_FILE_HEADER)] == self.BIN_FILE_HEADER:
			self.b_log(sys.stdout, True, 2, "Subsequent header version: %d." % (unpack("<L", self.bdat[len(self.BIN_FILE_HEADER):len(self.BIN_FILE_HEADER)+4])[0]))
			self.bdat = self.bdat[len(self.BIN_FILE_HEADER)+4:]
			self.btype = self.BIN_CONTAINER
		self.b_log(sys.stdout, True, 0, "Successfully loaded '%s' as a %s container." % (self.fname, self.btype))
		return True
	def b_process(self):
		if len(self.bdat) == 0:
			self.b_log(sys.stderr, False, 3, "Nothing to process.")
			return False
		bl = 0
		while len(self.bdat) > 0:
			old = False
			o_bmp = ""
			t_hdr = self.bdat[:self.TILE_HEADER_SIZE[self.btype]]
			key1, key2, t_width, t_height = unpack("<LLHH", t_hdr[:0xC])
			if self.btype == self.BIN_CONTAINER:
				bl = 4*t_width*t_height
				t_bmp = self.b_parse_rgb32b(self.bdat[len(t_hdr):len(t_hdr)+bl])
			elif self.btype == self.BMC_CONTAINER:
				t_bmp = ""
				t_len, t_params = unpack("<LL", t_hdr[-0x8:])
				if t_params & 0x08: #This bit is always ONE when relevant data is smaller than expected data, thus it is most likely the "compression" bit flag.
					self.b_log(sys.stdout, False, 3, "Tile data is compressed (%d bytes compressed in %d bytes); skipping." % (t_width*t_height*4, t_len))
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
								self.b_log(sys.stderr, False, 3, "Unable to determine data pattern size; exiting before throwing any error!")
								return False
				else:
					cf = t_len//(t_width*t_height)
					if cf == 4:
						t_bmp = self.b_parse_rgb32b(self.bdat[len(t_hdr):len(t_hdr)+cf*t_width*t_height])
						if t_height != 64:
							old = True
							o_bmp = self.b_parse_rgb32b(self.bdat[len(t_hdr)+cf*t_width*t_height:len(t_hdr)+cf*64*64])
					elif cf == 3:
						t_bmp = self.b_parse_rgb24b(self.bdat[len(t_hdr):len(t_hdr)+cf*t_width*t_height])
						if t_height != 64:
							old = True
							o_bmp = self.b_parse_rgb24b(self.bdat[len(t_hdr)+cf*t_width*t_height:len(t_hdr)+cf*64*64])
					elif cf == 2:
						t_bmp = self.b_parse_rgb565(self.bdat[len(t_hdr):len(t_hdr)+cf*t_width*t_height])
						if t_height != 64:
							old = True
							o_bmp = self.b_parse_rgb565(self.bdat[len(t_hdr)+cf*t_width*t_height:len(t_hdr)+cf*64*64])
					elif cf == 1:
						self.pal = True
						t_bmp = self.PALETTE+self.bdat[len(t_hdr):len(t_hdr)+cf*t_width*t_height]
						if t_height != 64:
							old = True
							o_bmp = self.PALETTE+self.bdat[len(t_hdr)+cf*t_width*t_height:len(t_hdr)+cf*64*64]
					else:
						self.b_log(sys.stderr, False, 3, "Unexpected bpp (%d) found during processing; aborting." % (8*cf))
						return False
					bl = cf*64*64
			if len(t_bmp) > 0:
				self.bmps.append(t_bmp)
				self.o_bmps.append(o_bmp)
				if len(self.bmps)%100 == 0:
					self.b_log(sys.stdout, True, 1, "%d tiles successfully extracted so far." % (len(self.bmps)))
			self.bdat = self.bdat[len(t_hdr)+bl:]
			if self.cnt != 0 and len(self.bmps) == self.cnt:
				break
		self.b_log(sys.stdout, False, 0, "%d tiles successfully extracted in the end." % (len(self.bmps)))
		return True
	def b_parse_rgb565(self, data):
		d_out = b""
		while len(data) > 0:
			pxl = unpack("<H", data[:2])[0]
			bl = ((pxl>>8)&0xF8)|((pxl>>13)&0x07)
			gr = ((pxl>>3)&0xFC)|((pxl>>9)&0x03)
			re = ((pxl<<3)&0xF8)|((pxl>>2)&0x07)
			d_out+=bytearray((re, gr, bl, 255))
			data = data[2:]
		return bytes(d_out)
	def b_parse_rgb32b(self, data):
		d_out = b""
		d_buf = b""
		while len(data) > 0:
			if self.btype == self.BIN_CONTAINER:
				d_buf+=data[:3]+b"\xFF"
				if len(d_buf) == 256:
					d_out = d_buf+d_out
					d_buf = b""
			else:
				d_out+=data[:3]+b"\xFF"
			data = data[4:]
		return d_out
	def b_parse_rgb24b(self, data):
		d_out = b""
		d_buf = b""
		while len(data) > 0:
			if self.btype == self.BIN_CONTAINER:
				d_buf+=data[:3]+b"\xFF"
				if len(d_buf) == 256:
					d_out = d_buf+d_out
					d_buf = b""
			else:
				d_out+=data[:3]+b"\xFF"
			data = data[3:]
		return d_out
	def b_export(self, dname):
		if not os.path.isdir(dname):
			self.b_log(sys.stderr, False, 3, "Destination must be an already existing folder.")
			return False
		self.fname = os.path.basename(self.fname)
		for i in range(len(self.bmps)):
			self.b_write(os.path.join(dname, "%s_%04d.bmp" % (self.fname, i)), self.b_export_bmp(64, len(self.bmps[i])//256, self.bmps[i]))
			if self.oldsave and len(self.o_bmps[i]) > 0:
				self.b_write(os.path.join(dname, "%s_old_%04d.bmp" % (self.fname, i)), self.b_export_bmp(64, len(self.o_bmps[i])//256, self.o_bmps[i]))
		self.b_log(sys.stdout, False, 0, "Successfully exported %d files." % (len(self.bmps)))
		if self.big:
			pad = b"\xFF"
			if not self.pal:
				pad*=4
			for i in range(len(self.bmps)):
				if self.pal:
					self.bmps[i] = self.bmps[i][len(self.PALETTE):]
				while len(self.bmps[i]) != 64*64*len(pad):
					self.bmps[i]+=pad*64
			w = 64*len(self.bmps)
			h = 64
			if len(self.bmps)//self.STRIPE_WIDTH > 0:
				m = len(self.bmps)%self.STRIPE_WIDTH
				if m != 0:
					for i in range(self.STRIPE_WIDTH-m):
						self.bmps.append(pad*64*64)
				w = self.STRIPE_WIDTH*64
				h*=len(self.bmps)//self.STRIPE_WIDTH
			c_bmp = b"" if not self.pal else self.PALETTE
			if self.btype == self.BIN_CONTAINER:
				collage_builder = (lambda x, a=self, PAD=len(pad), WIDTH=range(w // 64): b''.join([b''.join([a.bmps[a.STRIPE_WIDTH*(x+1)-1-k][64*PAD*j:64*PAD*(j+1)] for k in WIDTH]) for j in range(64)]))
			else:
				collage_builder = (lambda x, a=self, PAD=len(pad), WIDTH=range(w // 64): b''.join([b''.join([a.bmps[a.STRIPE_WIDTH*x+k][64*PAD*j:64*PAD*(j+1)] for k in WIDTH]) for j in range(64)]))

			c_bmp += b''.join(map(collage_builder, range(h//64)))
			self.b_write(os.path.join(dname, "%s_collage.bmp" % (self.fname)), self.b_export_bmp(w, h, c_bmp))
			self.b_log(sys.stdout, False, 0, "Successfully exported collage file.")
		return True
	def b_export_bmp(self, width, height, data):
		if not self.pal:
			return b"BM"+pack("<L", len(data)+122)+b"\x00\x00\x00\x00\x7A\x00\x00\x00\x6C\x00\x00\x00"+pack("<L", width)+pack("<L", height)+b"\x01\x00\x20\x00\x03\x00\x00\x00"+pack("<L", len(data))+b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x00\x00\xFF\x00\x00\xFF\x00\x00\x00\x00\x00\x00\xFF niW"+(b"\x00"*36)+b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"+data
		else:
			return b"BM"+pack("<L", len(data)+0x36)+b"\x00\x00\x00\x00\x36\x04\x00\x00\x28\x00\x00\x00"+pack("<L", width)+pack("<L", height)+b"\x01\x00\x08\x00\x00\x00\x00\x00"+pack("<L", len(data)-0x400)+b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"+data
	def b_write(self, fname, data):
		with open(fname, "wb") as f:
			f.write(data)
		return True
	def b_flush(self):
		self.bdat = ""
		self.bmps = []
		self.o_bmps = []
		return True

if __name__ == "__main__":
	prs = argparse.ArgumentParser(description="RDP Bitmap Cache parser (v. 2.00, 04/12/2020)")
	prs.add_argument("-s", "--src", help="Specify the BMCache file or directory to process.", required=True)
	prs.add_argument("-d", "--dest", help="Specify the directory where to store the extracted bitmaps.", required=True)
	prs.add_argument("-c", "--count", help="Only extract the given number of bitmaps.", type=int, default=-1)
	prs.add_argument("-v", "--verbose", help="Determine the amount of information displayed.", action="store_true", default=False)
	prs.add_argument("-o", "--old", help="Extract the old bitmap data found in the BMCache file.", action="store_true", default=False)
	prs.add_argument("-b", "--bitmap", help="Provide a big bitmap aggregating all the tiles.", action="store_true", default=False)
	prs.add_argument("-w", "--width", help="Specify the number of tiles per line of the aggregated bitmap (default=64).", type=int, default=64)
	args = prs.parse_args(sys.argv[1:])
	bmcc = BMCContainer(verbose=args.verbose, count=args.count, old=args.old, big=args.bitmap, width=args.width)
	if os.path.isdir(args.src):
		sys.stdout.write("[+++] Processing a directory...%s" % (os.linesep))
		src_files = []
		for root, dirs, files in os.walk(args.src):
			for f in files:
				if f.rsplit(".", 1)[-1].upper() in ["BIN", "BMC"]:
					if args.verbose:
						sys.stdout.write("[---] File '%s' has been found.%s" % (os.path.join(root, f), os.linesep))
					src_files.append(os.path.join(root, f))
		if len(src_files) == 0:
			sys.stderr.write("No suitable files were found under '%s' directory.%s" % (args.src, os.linesep))
			exit(-1)
	elif not os.path.isfile(args.src):
		sys.stderr.write("Invalid -s/--src parameter; use -h/--help for help.%s" % (os.linesep))
		exit(-1)
	else:
		sys.stdout.write("[+++] Processing a single file: '%s'.%s" % (args.src, os.linesep))
		src_files = [args.src]
	for src in src_files:
		if bmcc.b_import(src):
			bmcc.b_process()
			bmcc.b_export(args.dest)
			bmcc.b_flush()
	del bmcc
