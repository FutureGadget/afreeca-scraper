from constants import BANNER_FILE

def show_banner():
    with open(BANNER_FILE) as f:
        line = f.readline()
        while line:
            print(line)
            line = f.readline()

if __name__ == '__main__':
    show_banner()
