# usbtop-ebpf

A top-like tool for monitoring USB traffic using [eBPF][eBPF], inspired by [usbtop][usbtop].

Unlike [usbtop][usbtop], which captures packets from [usbmon][usbmon] and performs bus traffic calculations on URBs at the userspace level, this program uses an [eBPF][eBPF] [kprobe][kprobe] to collect USB traffic stats directly from [URBs][URB] in the kernel.


## Example output

Below is an example of the output from `usbtop.py`, showing a very fast read from a USB SSD connected to a 5 Gbps port and a much slower read from an RTL-SDR dongle.

```
Bus 6:
  Device   6.12  [0bda:9210]:
    0x81 (BULK, IN ):       3.38 Gbps    402.55 MiB/s
    0x83 (BULK, IN ):     104.88 Kbps     12.80 KiB/s
    0x04 (BULK, OUT):     209.77 Kbps     25.61 KiB/s
Bus 9:
  Device   9.30  [0bda:2838]:
    0x81 (BULK, IN ):       4.19 Mbps    512.00 KiB/s
```


## Quick start


### Software dependencies

* Python 3
* [bcc and its Python bindings][bcc]
  * On Arch Linux, run `sudo pacman -S python-bcc`.
  * On Debian, run `sudo apt-get install python3-bpfcc`


### Procedure

1. Install dependencies.
2. Run `sudo ./usbtop.py`.


## License

Except where stated otherwise, the contents of this repository are made available under the [Zero-Clause BSD (0BSD) license][license].


[bcc]: https://github.com/iovisor/bcc
[eBPF]: https://ebpf.io/
[kprobe]: https://docs.ebpf.io/linux/program-type/BPF_PROG_TYPE_KPROBE/
[license]: LICENSE.txt
[URB]: https://www.kernel.org/doc/html/latest/driver-api/usb/URB.html
[usbmon]: https://www.kernel.org/doc/html/latest/usb/usbmon.html
[usbtop]: https://github.com/aguinet/usbtop
