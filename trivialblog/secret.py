# Exec this script and replace the following empty string with the result:
AUTH_SECRET = ''

if __name__ == '__main__':
    with open('/dev/urandom', 'r') as f:
        print(repr(f.read(20)))
