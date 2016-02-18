import subprocess


from badimsicore_sniffing_gsmband_search import RadioBandSearcher
import badimsicore_sniffing_toxml
import argparse
import badimsicore_sniffing_xml_parsing
import time


class BadIMSICoreListener:

    @staticmethod
    def set_args(parser):
        group = parser.add_argument_group("listen")
        group.add_argument("-o", "--operator", help="search bts of this operator", default="orange", choices=["orange", "sfr", "bouygues_telecom"])
        group.add_argument("-b", "--band", help="search bts in this band of frequency", default="all")
        group.add_argument("-t", "--scan_time", help="Set the scan time for each frequency", default=2, type=float)
        group.add_argument("-n", "--repeat", help="Set the number of repeat of the scanning cycle", default=1, type=int)


    @staticmethod
    def scan_frequencies(repeat, scan_time, frequencies):
        opts = ["sudo", "python2.7", "airprobe/airprobe_rtlsdr_non_graphical.py"]
        opt_freq = ["-f"]
        frequencies = list(map(lambda freq: str(freq), frequencies))
        opt_freq.extend(frequencies)
        opts.extend(opt_freq)
        opts.extend(["-t", str(scan_time)])
        opts.extend(["-n", str(repeat)])
        return subprocess.call(args=opts) != 0



    @staticmethod
    def toxml(xmlFile, duration):
        badimsicore_sniffing_toxml.redirect_to_xml(xmlFile, "lo", "gsmtap && ! icmp", int(duration+1))

    @staticmethod
    def parse_xml(xmlFile):
        return badimsicore_sniffing_xml_parsing.parse_xml_file(xmlFile)


def main():

    rds = RadioBandSearcher('../ressources/all_gsm_channels_arfcn.csv')

    parser = argparse.ArgumentParser()
    BadIMSICoreListener.set_args(parser)
    args = parser.parse_args()
    bands = rds.get_bands()
    if args.band == "all":
        freqs = []
        for band in bands:
            freqs.extend(rds.get_arfcn(args.operator, band))
    else:
        freqs = rds.get_arfcn(args.operator, args.band)

    print(freqs)

    duration = 6 + len(freqs) * args.repeat * args.scan_time
    xmlFile = 'xml_output'

    BadIMSICoreListener.toxml(xmlFile, duration)
    if BadIMSICoreListener.scan_frequencies(args.repeat, args.scan_time, freqs) != 0:
        print("error scanning for BTS cells, exiting")
        exit(0)

    btss = BadIMSICoreListener.parse_xml(xmlFile)
    print(btss)
    exit(1)
if __name__ == '__main__':
    main()
