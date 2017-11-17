# kud-testing-code
Project KUD online testing python code.

Bluegiga  BLED112 Bluetooth Smart Dongle
# Bluetooth Smart Software API Reference Manual for BLE Version 1.5
https://www.silabs.com/products/wireless/bluetooth/bluetooth-low-energy-modules/bled112-bluetooth-smart-dongle

https://draapho.github.io/2016/11/15/1616-python-ble/


# python bled112_scanner.py -p COM7
# MAC = B0912269818D
# UUID = 0201061106684C05633E7742A28245F10A0000140E
# 1504691228.419 -47 0 B0912269818D 0 255 0201061106684C05633E7742A28245F10A0000140E

# Getting Started with the BlueGiga BLE112 Bluetooth Low Energy module 
https://eewiki.net/display/Wireless/Getting+Started+with+the+BlueGiga+BLE112+Bluetooth+Low+Energy+module

# Dfu-util
http://wiki.openmoko.org/wiki/Dfu-util


# read memory size
awk '$3=="kB"{if ($2>1024**2){$2=$2/1024**2;$3="GB";} else if ($2>1024){$2=$2/1024;$3="MB";}} 1' /proc/meminfo | column -t


# read eMMC size
$MMC_DEV=/dev/mmcblk0
fdisk -l $MMC_DEV | awk '/Disk/ {print $5; exit}'
fdisk -l /dev/mmcblk0 | awk '/Disk/ {print $5; exit}'

df
cat /proc/partitions | grep mmcblk0 | column -t
cat /proc/mounts
busybox fdisk -lu mmcblk0
    >> Disk mmcblk0: 7.3 GiB, 7818182656 bytes, 15269888 sectors
dmesg |grep "mmc"
    >> mmcblk0: mmc0:0001 8GME4R 7.28 GiB
dmesg |grep "partition"
    >> [    3.726830] mmcblk0boot0: mmc0:0001 8GME4R partition 1 4.00 MiB
    >> [    3.727074] mmcblk0boot1: mmc0:0001 8GME4R partition 2 4.00 MiB
    >> [    3.727246] mmcblk0rpmb: mmc0:0001 8GME4R partition 3 512 KiB
cat /sys/block/mmcblk0/size
    >> 15269888 (need * 512 byte)

# read wifi rssi
iw dev mlan0 scan | egrep "signal|SSID" | sed -e "s/\tsignal: //" -e "s/\tSSID: //" | awk '{ORS = (NR % 2 == 0)? "\n" : " "; print}' | grep -v '\x00' | sort
iw dev mlan0 scan | egrep  signal | sed -ne "s|\(signal \([0-9]\+\).*\)|\2}\1|p"
iw dev mlan0 scan | perl -nle '/SSID:(.*)$/ && print $1'
iw dev mlan0 scan | awk -F ':' '/SSID:/ {print $2;}'


# bluetooth
hciconfig -a hci0 | grep Name
    >> Name: 'BlueZ 5.37'

btmon & hcitool lescan
hcitool lescan --duplicates & hcidump --raw
hcidump -a | egrep 'RSSI|bdaddr' | cut -f 8 -d ' ' | ./tester.sh > /tmp/result.csv
(timeout -s SIGINT 5s hcitool -i hci0 lescan | grep 00:00:00:00:00:00)

sh bluetoothconfig.sh | bluetoothctl


堵 GND
フ TX
厚 RX
