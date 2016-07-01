#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse, os, os.path, sys
from struct import pack, unpack

class BMCContainer():
	BIN_FILE_HEADER = "RDP8bmp\x00"
	BIN_CONTAINER = ".BIN"
	BMC_CONTAINER = ".BMC"
	TILE_HEADER_SIZE = {BMC_CONTAINER: 0x14, BIN_CONTAINER: 0xC}
	LOG_TYPES = ["[===]", "[+++]", "[---]", "[!!!]"]
	PALETTE = "00000000000080000080000000808000800000008000800080800000C0C0C000C0DCC000F0CAA6000020400000206000002080000020A0000020C0000020E00000400000004020000040400000406000004080000040A0000040C0000040E00000600000006020000060400000606000006080000060A0000060C0000060E00000800000008020000080400000806000008080000080A0000080C0000080E00000A0000000A0200000A0400000A0600000A0800000A0A00000A0C00000A0E00000C0000000C0200000C0400000C0600000C0800000C0A00000C0C00000C0E00000E0000000E0200000E0400000E0600000E0800000E0A00000E0C00000E0E00040000000400020004000400040006000400080004000A0004000C0004000E00040200000402020004020400040206000402080004020A0004020C0004020E00040400000404020004040400040406000404080004040A0004040C0004040E00040600000406020004060400040606000406080004060A0004060C0004060E00040800000408020004080400040806000408080004080A0004080C0004080E00040A0000040A0200040A0400040A0600040A0800040A0A00040A0C00040A0E00040C0000040C0200040C0400040C0600040C0800040C0A00040C0C00040C0E00040E0000040E0200040E0400040E0600040E0800040E0A00040E0C00040E0E00080000000800020008000400080006000800080008000A0008000C0008000E00080200000802020008020400080206000802080008020A0008020C0008020E00080400000804020008040400080406000804080008040A0008040C0008040E00080600000806020008060400080606000806080008060A0008060C0008060E00080800000808020008080400080806000808080008080A0008080C0008080E00080A0000080A0200080A0400080A0600080A0800080A0A00080A0C00080A0E00080C0000080C0200080C0400080C0600080C0800080C0A00080C0C00080C0E00080E0000080E0200080E0400080E0600080E0800080E0A00080E0C00080E0E000C0000000C0002000C0004000C0006000C0008000C000A000C000C000C000E000C0200000C0202000C0204000C0206000C0208000C020A000C020C000C020E000C0400000C0402000C0404000C0406000C0408000C040A000C040C000C040E000C0600000C0602000C0604000C0606000C0608000C060A000C060C000C060E000C0800000C0802000C0804000C0806000C0808000C080A000C080C000C080E000C0A00000C0A02000C0A04000C0A06000C0A08000C0A0A000C0A0C000C0A0E000C0C00000C0C02000C0C04000C0C06000C0C08000C0C0A000F0FBFF00A4A0A000808080000000FF0000FF000000FFFF00FF000000FF00FF00FFFF0000FFFFFF00".decode("hex")
	def __init__(self, verbose=False, count=0, old=False):
		self.bdat = ""
		self.o_bmps = []
		self.bmps = []
		self.btype = None
		self.cnt = count
		self.fname = None
		self.oldsave = old
		self.pal = False
		self.verb = verbose
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
		off = 0
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
					bl = 64*64*2
				else:
					cf = t_len/(t_width*t_height)
					if cf not in [1, 2, 4]:
						self.b_log(sys.stderr, False, 3, "Unexpected bpp (%d) found during processing; aborting." % (8*cf))
						return False
					if cf == 4:
						t_bmp = self.b_parse_rgb32b(self.bdat[len(t_hdr):len(t_hdr)+cf*t_width*t_height])
						if t_height != 64:
							old = True
							o_bmp = self.b_parse_rgb32b(self.bdat[len(t_hdr)+cf*t_width*t_height:len(t_hdr)+cf*64*64])
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
					bl = cf*64*64
			if len(t_bmp) > 0:
				self.bmps.append(t_bmp)
				self.o_bmps.append(o_bmp)
				if len(self.bmps)%100 == 0:
					self.b_log(sys.stdout, True, 1, "%d tiles successfully extracted so far." % (len(self.bmps)))
			off+=len(t_hdr)+bl
			self.bdat = self.bdat[len(t_hdr)+bl:]
			if self.cnt != 0 and len(self.bmps) == self.cnt:
				break
		self.b_log(sys.stdout, True, 0, "%d tiles successfully extracted in the end." % (len(self.bmps)))
		return True
	def b_parse_rgb565(self, data):
		d_out = ""
		while len(data) > 0:
			pxl = unpack("<H", data[:2])[0]
			bl = ((pxl>>8)&0xF8)|((pxl>>13)&0x07)
			gr = ((pxl>>3)&0xFC)|((pxl>>9)&0x03)
			re = ((pxl<<3)&0xF8)|((pxl>>2)&0x07)
			d_out+=chr(re)+chr(gr)+chr(bl)+"\xFF"
			data = data[2:]
		return d_out
	def b_parse_rgb32b(self, data):
		d_out = ""
		d_buf = ""
		while len(data) > 0:
			if self.btype == self.BIN_CONTAINER:
				d_buf+=data[:3]+"\xFF"
				if len(d_buf) == 256:
					d_out = d_buf+d_out
					d_buf = ""
			else:
				d_out+=data[:3]+"\xFF"
			data = data[4:]
		return d_out
	def b_export(self, dname):
		if not os.path.isdir(dname):
			self.b_log(sys.stderr, False, 3, "Destination must be an already existing folder.")
			return False
		elif not os.path.isdir(os.path.join(dname, self.fname).rsplit(os.sep, 1)[0]):
			os.makedirs(os.path.join(dname, self.fname).rsplit(os.sep, 1)[0])
		for i in range(len(self.bmps)):
			self.b_write(os.path.join(dname, "%s_%04d.bmp" % (self.fname, i)), self.b_export_bmp(64, len(self.bmps[i])/256, self.bmps[i]))
			if self.oldsave and len(self.o_bmps[i]) > 0:
				self.b_write(os.path.join(dname, "%s_old_%04d.bmp" % (self.fname, i)), self.b_export_bmp(64, len(self.o_bmps[i])/256, self.o_bmps[i]))
		self.b_log(sys.stdout, False, 0, "Successfully exported %d files." % (len(self.bmps)))
		return True
	def b_export_bmp(self, width, height, data):
		if not self.pal:
			return "BM"+pack("<L", len(data)+126)+"\x00\x00\x00\x00\x7A\x00\x00\x00\x6C\x00\x00\x00"+pack("<L", width)+pack("<L", height)+"\x01\x00\x20\x00\x03\x00\x00\x00"+pack("<L", len(data))+"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x00\x00\xFF\x00\x00\xFF\x00\x00\x00\x00\x00\x00\xFF niW"+("\x00"*36)+"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"+data
		else:
			return "BM"+pack("<L", len(data)+0x36)+"\x00\x00\x00\x00\x36\x04\x00\x00\x28\x00\x00\x00"+pack("<L", width)+pack("<L", height)+"\x01\x00\x08\x00\x00\x00\x00\x00"+pack("<L", len(data)-0x400)+"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"+data
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
	prs = argparse.ArgumentParser(description="RDP Bitmap Cache parser (v. 1.00, 27/06/2016)")
	prs.add_argument("-o", "--old", help="Extract the old bitmap data found in the BMCache file.", action="store_true", default=False)
	prs.add_argument("-d", "--dest", help="Specify the directory where to store the extracted bitmaps.", required=True)
	prs.add_argument("-c", "--count", help="Only extract the given number of bitmaps.", type=int, default=-1)
	prs.add_argument("-s", "--src", help="Specify the BMCache file or directory to process.", required=True)
	prs.add_argument("-v", "--verbose", help="Determine the amount of information displayed.", action="store_true", default=False)
	args = prs.parse_args(sys.argv[1:])
	bmcc = BMCContainer(verbose=args.verbose, count=args.count, old=args.old)
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
