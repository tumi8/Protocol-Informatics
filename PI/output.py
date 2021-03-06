# vim: set sts=4 sw=4 cindent nowrap expandtab:

"""
Consensus module
Generate consensus based on multiple sequence alignment

Written by Marshall Beddoe <mbeddoe@baselineresearch.net>
Copyright (c) 2004 Baseline Research

Licensed under the LGPL
"""

from curses.ascii import *
import sys

class Output:

    def __init__(self, sequences, gapped):

        self.sequences = sequences
        self.consensus = []
        self.gapped = gapped
        self._go()

    def _go(self):
        pass

class TextBased(Output):
    def __init__(self, sequences, gapped):
        self.gap = "\033[41;30m%s\033[0m"
        self.printable = "\033[42;30m%s\033[0m"
        self.space = "\033[43;30m%s\033[0m"
        self.binary = "\033[44;30m%s\033[0m"
        self.zero = "\033[45;30m%s\033[0m"
        self.bit = "\033[46;30m%s\033[0m"
        self.default = "\033[47;30m%s\033[0m"

        Output.__init__(self, sequences, gapped)

    def _go(self):
        all_cons = []
        for id, seq in self.sequences:
            for byte in seq:
                if byte == 256:
                    #pass
                    sys.stdout.write("_")
                elif isprint(byte):
                    sys.stdout.write(chr(byte))
                else:
                    sys.stdout.write(".")
            print ""
        
        # Calculate consensus sequence
        l = len(self.sequences[0][1])

        for i in range(l):
            histogram = {}
            for id, seq in self.sequences:
                if len(seq) == 0:
                    continue

                try:
                    histogram[seq[i]] += 1
                except:
                    histogram[seq[i]] = 1

            items = histogram.items()
            items.sort()

            m = 1
            v = 257
            for j in items:
                if j[1] > m:
                    m = j[1]
                    v = j[0]

            self.consensus.append(v)

            real = []

            for i in range(len(self.consensus)):
                if self.consensus[i] == 256 and not self.gapped:
                    continue
                real.append(self.consensus[i])

        print "\nUngapped Consensus:"
        self.cons = ""
        for byte in real:
            if byte == 256:
                sys.stdout.write("_")
                self.cons += "_"
            elif isprint(byte):
                sys.stdout.write(chr(byte))
                self.cons += chr(byte)
            else:
                sys.stdout.write(".")
                self.cons += "."
        print ""
                

class Ansi(Output):

    def __init__(self, sequences, gapped):

        # Color defaults for composition
        self.gap = "\033[41;30m%s\033[0m"
        self.printable = "\033[42;30m%s\033[0m"
        self.space = "\033[43;30m%s\033[0m"
        self.binary = "\033[44;30m%s\033[0m"
        self.zero = "\033[45;30m%s\033[0m"
        self.bit = "\033[46;30m%s\033[0m"
        self.default = "\033[47;30m%s\033[0m"

        Output.__init__(self, sequences, gapped)

    def _go(self):
        # how many bytes to print by default
        # output will be split into multiple blocks according to this
        # a byte is printed using three charactes (e.g. x52) and invidiual
        # bytes are separated via one space. 18 is a good default value for
        # 80 character terminals
        term_width = 18

        seqLength = len(self.sequences[0][1])
        rounds = seqLength / term_width
        remainder = seqLength % term_width
        l = len(self.sequences[0][1])

        start = 0
        end = term_width

        dtConsensus = []
        mtConsensus = []

        for i in range(rounds):
            for id, seq in self.sequences:
                print "%04d" % id,
                for byte in seq[start:end]:
                    if byte == 256:
                        print self.gap % "___",
                    elif isspace(byte):
                        print self.space % "   ",
                    elif isprint(byte):
                        print self.printable % "x%02x" % byte,
                    elif byte == 0:
                        print self.zero % "x00",
                    else:
                        print self.default % "x%02x" % byte,
                print ""

            # Calculate datatype consensus

            print "DT  ",
            for j in range(start, end):
                column = []
                for id, seq in self.sequences:
                    if len(seq) == 0:
                        continue
                    column.append(seq[j])
                dt = self._dtConsensus(column)
                print dt,
                dtConsensus.append(dt)
            print ""

            print "MT  ",
            for j in range(start, end):
                column = []
                for id, seq in self.sequences:
                    if len(seq) == 0:
                        continue
                    column.append(seq[j])
                rate = self._mutationRate(column)
                print "%03d" % (rate * 100),
                mtConsensus.append(rate)
            print "\n"

            start += term_width
            end += term_width

        if remainder:
            for id, seq in self.sequences:
                print "%04d" % id,
                for byte in seq[start:start + remainder]:
                    if byte == 256:
                        print self.gap % "___",
                    elif isspace(byte):
                        print self.space % "   ",
                    elif isprint(byte):
                        print self.printable % "x%02x" % byte,
                    elif byte == 0:
                        print self.zero % "x00",
                    else:
                        print self.default % "x%02x" % byte,
                print ""

            print "DT  ",
            for j in range(start, start + remainder):
                column = []
                for id, seq in self.sequences:
                    if len(seq) == 0:
                        continue
                    column.append(seq[j])
                dt = self._dtConsensus(column)
                print dt,
                dtConsensus.append(dt)
            print ""

            print "MT  ",
            for j in range(start, start + remainder):
                column = []
                for id, seq in self.sequences:
                    if len(seq) == 0:
                        continue
                    column.append(seq[j])
                rate = self._mutationRate(column)
                mtConsensus.append(rate)
                print "%03d" % (rate * 100),
            print ""

        # Calculate consensus sequence
        l = len(self.sequences[0][1])

        real = []
        for i in range(l):
            histogram = {}
            for id, seq in self.sequences:
                if len(seq) == 0:
                    continue

                try:
                    histogram[seq[i]] += 1
                except:
                    histogram[seq[i]] = 1


            items = histogram.items()
            items.sort()

            m = 1
            v = 257
            for j in items:
                if j[1] > m:
                    m = j[1]
                    v = j[0]

            self.consensus.append(v)

            real = []

            for i in range(len(self.consensus)):
                if self.consensus[i] == 256 and not self.gapped:
                    continue
                real.append((self.consensus[i], dtConsensus[i], mtConsensus[i]))

        #
        # Display consensus data
        #
        totalLen = len(real)
        rounds = totalLen / 18
        remainder = totalLen % 18

        start = 0
        end = 18

        print "\nUngapped Consensus:"

        for i in range(rounds):
            print "CONS",
            for byte,type,rate in real[start:end]:
                if byte == 256:
                   print self.gap % "___",
                elif byte == 257:
                    print self.default % "???",
                elif isspace(byte):
                    print self.space % "   ",
                elif isprint(byte):
                    print self.printable % "x%02x" % byte,
                elif byte == 0:
                    print self.zero % "x00",
                else:
                    print self.default % "x%02x" % byte,
            print ""

            print "DT  ",
            for byte,type,rate in real[start:end]:
                print type,
            print ""

            print "MT  ",
            for byte,type,rate in real[start:end]:
                print "%03d" % (rate * 100),
            print "\n"

            start += 18
            end += 18

        if remainder:
            print "CONS",
            for byte,type,rate in real[start:start + remainder]:
                if byte == 256:
                   print self.gap % "___",
                elif byte == 257:
                    print self.default % "???",
                elif isspace(byte):
                    print self.space % "   ",
                elif isprint(byte):
                    print self.printable % "x%02x" % byte,
                elif byte == 0:
                    print self.zero % "x00",
                else:
                    print self.default % "x%02x" % byte,
            print ""

            print "DT  ",
            for byte,type,rate in real[start:end]:
                print type,
            print ""

            print "MT  ",
            for byte,type,rate in real[start:end]:
                print "%03d" % (rate * 100),
            print ""

    def _dtConsensus(self, data):
        histogram = {}

        for byte in data:
            if byte == 256:
                try:
                    histogram["G"] += 1
                except:
                    histogram["G"] = 1
            elif isspace(byte):
                try:
                    histogram["S"] += 1
                except:
                    histogram["S"] = 1
            elif isprint(byte):
                try:
                    histogram["A"] += 1
                except:
                    histogram["A"] = 1
            elif byte == 0:
                try:
                    histogram["Z"] += 1
                except:
                    histogram["Z"] = 1
            else:
                try:
                    histogram["B"] += 1
                except:
                    histogram["B"] = 1

        items = histogram.items()
        items.sort()

        m = 1
        v = '?'
        for j in items:
           if j[1] > m:
               m = j[1]
               v = j[0]

        return v * 3

    def _mutationRate(self, data):

        histogram = {}

        for x in data:
            try:
                histogram[x] += 1
            except:
                histogram[x] = 1

        items = histogram.items()
        items.sort()

        if len(items) == 1:
            rate = 0.0
        else:
            rate = len(items) * 1.0 / len(data) * 1.0

        return rate
