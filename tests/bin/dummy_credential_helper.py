import sys
from configparser import ConfigParser


def main(out_path, action):
    with open(out_path, 'w') as f:
        data = sys.stdin.read()

        cp = ConfigParser()
        cp.read_string("[desc]\n" + data)
        sec = cp["desc"]
        print(dict(sec), file=sys.stderr)

        if action == "get":
            if sec['host'] == "example.org":
                f.write("ok_fill")
                sys.stdout.write(f"host={sec['host']}\nprotocol={sec['protocol']}\npath={sec['path']}\nusername=success\npassword=youwin\n\n")
            else:
                f.write("fail_fill")
                sys.stdout.write("quit 1\n\n")
        elif action == "store":
            f.write(data)
        elif action == "erase":
            f.write("reject\n")
            f.write(data)
        else:
            f.write("Unknown op.")
            exit(1)


if __name__ == '__main__':
    main(*sys.argv[1:])
