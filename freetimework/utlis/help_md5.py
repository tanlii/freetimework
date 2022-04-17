import hashlib


class MakeMD5:
    def __init__(self):
        pass

    def get_md5(self, text):
        hl = hashlib.md5()
        hl.update(text.encode(encoding="utf-8"))
        return hl.hexdigest()


if __name__ == '__main__':
    m = MakeMD5()
    print(m.get_md5('shdsjhddfdjfkdhjfhdfjkdhfhdkhskskkskweeirlakn dbfjh'))
