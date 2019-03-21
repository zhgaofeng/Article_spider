import hashlib
import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def get_nums(value):
    mark_match = re.match(".*?(\d).*", value)
    if mark_match:
        return int(mark_match.group(1))
    else:
        return 0


if __name__ == "__main__":
    print(get_md5("http://jobbole.com"))