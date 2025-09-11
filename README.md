# usbtop-ebpf

A top-like tool for monitoring USB traffic using [eBPF][eBPF], inspired by [usbtop][usbtop].

Unlike [usbtop][usbtop], which captures packets from [usbmon][usbmon] and performs bus traffic calculations on URBs at the userspace level, this program uses an [eBPF][eBPF] [kprobe][kprobe] to collect USB traffic stats directly from [URBs][URB] in the kernel.


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
