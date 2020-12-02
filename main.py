from controller import Controller
from osgeo import gdal
import sys


def main():
    # c = Controller()
    #  c = Controller(src="./example", cfg="./example/config.txt")
    # c = Controller(cfg="./example/config.txt")
    src = input("[+] Input tiff files dir(default is \".\"): ")
    cfg = input("[+] Input config file path(default is \"./config.txt\"): ")
    c = Controller(src, cfg)
    c.read_cfg(c.cfg)
    c.scan_tifs(c.src)
    c.set_tifs_area()
    c.rename()


if __name__ == "__main__":
    while 1:
        try:
            main()
            what = input("[+] Done.\n\n\n" +
                         "[!] Press Enter to continue\n" +
                         "[!] OR\n" +
                         "[!] Input `exit` to quit job.\n" +
                         "[*] >>> ")
            if what == "exit":
                sys.exit(0)
            else:
                continue
        except FileNotFoundError:
            print("[-] Please make sure config file at right spot as you input.")
        except Exception as err:
            print(err)
