// SPDX-License-Identifier: 0BSD

/*
 *  Copyright (C) 2025 by Forest Crossman <cyrozap@gmail.com>
 *
 *  Permission to use, copy, modify, and/or distribute this software for
 *  any purpose with or without fee is hereby granted.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
 *  WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
 *  WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
 *  AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
 *  DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
 *  PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
 *  TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
 *  PERFORMANCE OF THIS SOFTWARE.
 */


#include <linux/usb.h>
#include <linux/usb/ch9.h>
#include <linux/usb/hcd.h>


struct key_t {
	u32 busnum;
	u32 devnum;

	u16 vendor;
	u16 product;

	u8 endpoint;
	u8 type;

	/* to align to 16 bytes */
	u8 pad[2];
};


BPF_HASH(stats, struct key_t, u64);


int kprobe__usb_hcd_giveback_urb(
	struct pt_regs *ctx,
	struct usb_hcd *hcd,
	struct urb *urb,
	int status)
{
	struct key_t key = { 0 };
	struct usb_device *dev = urb->dev;

	key.busnum = dev->bus->busnum;
	key.devnum = dev->devnum;
	key.vendor = dev->descriptor.idVendor;
	key.product = dev->descriptor.idProduct;
	key.endpoint = urb->ep->desc.bEndpointAddress;
	key.type = urb->ep->desc.bmAttributes & USB_ENDPOINT_XFERTYPE_MASK;

	if (key.type == 0 && key.endpoint == 0) {
		/* For EP0, bEndpointAddress is always 0. Direction is in the pipe. */
		key.endpoint |= urb->pipe & USB_DIR_IN;
	}

	if (urb->actual_length > 0) {
		u64 len = urb->actual_length;
		stats.increment(key, len);
	}

	return 0;
}
