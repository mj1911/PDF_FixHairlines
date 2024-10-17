#!/usr/bin/env python3
""" Enlarges very thin lines of PDF files for visibility and printing.
    by RDTSC 2021 v0.1 """

import os
import re           # regular expressions
import sys
import shutil       # for spawning process
import subprocess   # for running ghostscript

_author_ = 'RDTSC'
_version_ = '0.1'

try:
    gs1 = shutil.which("gs")    # ensure GhostScript is available...
    gs2 = shutil.which("gswin64.exe")
    if not (gs1 or gs2):
        print("GhostScript is required! See http://www.ghostscript.com")
        exit()
    if gs1:
        gs = "gs"
    elif gs2:
        gs = "gswin64.exe"
except shutil.Error as e:
    print("Error checking for GhostScript: " + e)
    exit()


def search(file):
    """ Searches through uncompressed binary data for thin lines below 1pt """
    changes = 0                         # local changes for this file
    pat = re.compile(rb'0.?\d* [wW]')   # regex, binary "0[.*] w"
    d = bytearray()
    with open(file, mode='r+b') as f:   # updateable, binary (cannot resize!)
        d = bytearray(f.read())         # read file data as d
#        d2 = d              # copy to "non-file" buffer
    it = pat.finditer(d)            # find pattern in data as iterable
    for match in it:                # for each match,
        m = match.group()           # bytes of the match string to binary m
        m2 = m[:-2]                 # just the numeric part, strip " w"
        lm = len(m2)                # number of bytes
        dbl = float(m2)*20          # increase value
        if dbl == 0.0:              # for 0pt "hairlines",
            dbl = 0.1               # suggest 0.1pt
        prompt = f'*** Found: "{m.decode("ascii")}"; set to [{dbl}] or custom: '
        while True:
            got = input(prompt)     # ask for val
            if got == "":           # if enter,
                got = dbl           # use doubled value
            try:
                val = float(got)    # else convert to float
            except (ValueError, TypeError, KeyboardInterrupt):
                print("Value not understood... try again or 0 to skip.")
                continue
            if val > 0:             # if legit value,
                val = bytes(str(val).encode("ASCII"))    # convert to bytes
                lv = len(val)       # and get length of this val
#                    if __debug__:
#                        print(f"* m2 = {m2}, len(m2) = {lm}, val = {val}, len(v) = {lv}")
                    #if lv > lm:         # too many digits?
                    #    print("Length too long; use fewer digits.")
                    #    continue
                while lv < lm:      # too few digits?
                    val += b'0'     # append a zero
                    lv += 1         # try again
# bytearray is a sequence-type, and it supports slice-based operations. The
# "insert at position i" idiom with slices goes like this x[i:i] = ...
                val = val + b" w"   # should be same length now
                print(f'*** Changing {m} to {val}')
#                print(f'len(d): {len(d)}, match.start(): {match.start()}, match.end(): {match.end()}, len(bytearray(val)): {len(bytearray(val))}')
                    #d = re.sub(m, val, d, 1)    # assign the bastard
                d[match.start():match.end()] = bytearray(val)
# TODO: THERE MAY STILL BE A POSSIBLE ISSUE HERE...
# BufferError: Existing exports of data: object cannot be re-sized.
                changes += 1        # we changed one
            break
#            if __debug__:
#                print(m)
        print(f"*** Updating bytes in {file}...")
        with open(file, mode='w+b') as f:   # writeable, binary
            f.seek(0)                       # go to beginning of file!
            f.write(d)                      # write out changed data, close
    d = ""                              # purge file buffer
    return changes


def main(argv):
    """ Main application, fix PDF hair/thin lines """
    retval = 0      # 1 for error
    nfiles = 0      # number of processed files
    nchanges = 0    # number of total changes made
    print(f"*** GhostScript found as: \"{gs}\"")
    for infile in argv[1:]:
        # qualify input file(s)...
        print(f"*** Input file: {infile}")
        if not (infile.endswith(".pdf") or infile.endswith(".PDF")):
            print("*** File is not a .PDF file, ignored!\n")
            retval = 1
            continue    # next file
        if not os.path.isfile(infile):
            print("*** File does not exist, ignored!\n")
            retval = 1
            continue

        # file data must start with "%PDF"
        with open(infile, mode='rb') as file: # b -> binary
            indata = file.read()        # file is immediately closed
        if indata.startswith(b"%PDF"):  # binary string
            print(f"*** {infile} signature is correct, processing...")
            indata = b""                # free buffer
            nfiles += 1
        else:
            print(f"*** {infile} is not a valid .PDF file!\n")
            indata = b""
            retval = 1
            continue

        # decompress input file
        midfile = os.path.splitext(infile)[0] + "-decompressed.pdf"
        if os.path.isfile(midfile):     # if midfile exists
            choice = "q"
            while choice not in ("y", "n"):
                choice = input(f"*** WARNING: {midfile} exists, overwrite? [Y/N] (Y): ")
#                if __debug__:
#                    print(f"Choice: \"{choice}\"")
                if choice in ("Y", ""):
                    choice = "y"
                if choice == ("N"):
                    choice = "n"
            if choice == "n":
                continue        # skip this file
        print(f"*** Decompressing {infile} to {midfile} via GS...")
        try:
            ret = subprocess.run([gs, '-sDEVICE=pdfwrite', f'-o{midfile}', \
                '-q', '-dCompressPages=false', f'{infile}'])
            ret.check_returncode()
        except subprocess.CalledProcessError:
            print(f"*** Error decompressing {infile}!")
            retval = 1
            continue

        # open uncompressed file data as RW bytes, operate directly on it
        print(f"*** Searching {midfile} for lines smaller than 1pt...")
        nchanges += search(midfile)     # perform search, returning count

        # recompress to outfile
        outfile = os.path.splitext(infile)[0] + "-fixed.pdf"
        if os.path.isfile(outfile):     # if outfile exists
            choice = "q"
            while choice not in ("y", "n"):
                choice = input(f"*** WARNING: {outfile} exists, overwrite? [Y/N] (Y): ")
                if choice in ("Y", ""):
                    choice = "y"
                if choice == ("N"):
                    choice = "n"
            if choice == "n":
                continue
        print(f"*** Compressing {midfile} to {outfile} via GS...")
        try:
            ret = subprocess.run([gs, '-sDEVICE=pdfwrite', f'-o{outfile}', \
                '-q', '-dCompressPages=true', f'{midfile}'])
            ret.check_returncode()
        except subprocess.CalledProcessError:
            print(f"*** Error compressing {outfile}!")
            retval = 1
            continue

        # remove decompressed file
        print(f"*** Deleting {midfile}...")
        try:
            os.remove(midfile)
        except (FileNotFoundError, OSError):
            print(f"*** Could not delete {midfile}!")
            retval = 1

        # this file is complete!
        print("*** Success!\n")

    # all files are complete!
    print(f"{nfiles} file(s) processed. {nchanges} change(s) made.")
    if retval == 1:
        tmp = input("\nErrors occurred! Press <Enter> to exit: ")
        tmp = tmp
    return retval


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(f"""PDF Fix Hairlines by {_author_} v{_version_}\n
Usage:  [python3 PDF_Fix.py file.pdf]  or drag .pdf file(s) onto .cmd or .sh
Purpose: uncompresses and searches for line widths less than 1.000pt.  If any
thin lines are found, these may be changed.  The default increase is twenty
times the original, so a width of 0.123pt defaults to 2.46pt, but you may enter
a size if desired.  A special case is 0pt, so-called HairLines. These default to
0.1pt but you may need to experiment to get a usable size.\n
You may want to try printing the Test.pdf and Test-fixed.pdf examples.\n""")
        tmp = input("Press <Enter> to exit: ")
        tmp = tmp
# for debugging, un-comment and run this with no params to define these args:
#        if __debug__:
#            sys.argv = ["PDF_Fix.py", "Test.pdf", "b.PDF", "c.XDF"]
#            main(sys.argv)
        exit()
    main(sys.argv[0:])

# EOF
