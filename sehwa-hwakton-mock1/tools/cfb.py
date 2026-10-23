"""Minimal Compound File Binary (OLE2) writer, version 3 (512-byte sectors)."""
import struct

FREESECT = 0xFFFFFFFF
ENDOFCHAIN = 0xFFFFFFFE
FATSECT = 0xFFFFFFFD
NOSTREAM = 0xFFFFFFFF
SECTOR = 512
MINI = 64
CUTOFF = 4096


class Node:
    def __init__(self, name, kind, data=b'', clsid=b'\0' * 16):
        self.name = name
        self.kind = kind  # 1 storage, 2 stream, 5 root
        self.data = data
        self.clsid = clsid
        self.children = []
        self.sid = None
        self.left = self.right = self.child = NOSTREAM
        self.start = ENDOFCHAIN
        self.size = 0


def _key(n):
    return (len(n.name), n.name.upper())


def write_cfb(path, root):
    """root: Node(kind=5) with nested children."""
    # assign sids in BFS order
    nodes = []

    def walk(n):
        n.sid = len(nodes)
        nodes.append(n)
        for c in n.children:
            walk(c)
    walk(root)

    # build balanced BST of each storage's children (all black)
    def bst(items):
        if not items:
            return NOSTREAM
        m = len(items) // 2
        n = items[m]
        n.left = bst(items[:m])
        n.right = bst(items[m + 1:])
        return n.sid
    for n in nodes:
        if n.kind in (1, 5):
            n.child = bst(sorted(n.children, key=_key))

    # mini stream
    mini = bytearray()
    minifat = []
    big = []
    for n in nodes:
        if n.kind != 2:
            continue
        n.size = len(n.data)
        if n.size == 0:
            n.start = ENDOFCHAIN
        elif n.size < CUTOFF:
            first = len(mini) // MINI
            cnt = (n.size + MINI - 1) // MINI
            mini += n.data + b'\0' * (cnt * MINI - n.size)
            for i in range(cnt):
                minifat.append(first + i + 1 if i < cnt - 1 else ENDOFCHAIN)
            n.start = first
        else:
            big.append(n)

    # sector layout: [stream data...][ministream][minifat][directory][fat]
    sectors = []  # list of bytes(512)
    fat = []

    def alloc(data):
        if not data:
            return ENDOFCHAIN
        cnt = (len(data) + SECTOR - 1) // SECTOR
        data = bytes(data) + b'\0' * (cnt * SECTOR - len(data))
        first = len(sectors)
        for i in range(cnt):
            sectors.append(data[i * SECTOR:(i + 1) * SECTOR])
            fat.append(first + i + 1 if i < cnt - 1 else ENDOFCHAIN)
        return first

    for n in big:
        n.start = alloc(n.data)
    root.start = alloc(bytes(mini)) if mini else ENDOFCHAIN
    root.size = len(mini)
    mf = b''.join(struct.pack('<I', x) for x in minifat)
    minifat_start = alloc(mf) if mf else ENDOFCHAIN
    n_minifat = (len(mf) + SECTOR - 1) // SECTOR

    # directory entries
    def dirent(n):
        nm = n.name.encode('utf-16le') + b'\0\0'
        e = nm + b'\0' * (64 - len(nm))
        e += struct.pack('<HBB', len(nm), n.kind, 1)  # color black
        e += struct.pack('<III', n.left, n.right, n.child)
        e += n.clsid
        e += struct.pack('<I', 0) + b'\0' * 16
        e += struct.pack('<I', n.start if n.kind != 1 else 0)
        e += struct.pack('<II', n.size if n.kind != 1 else 0, 0)
        assert len(e) == 128
        return e
    d = b''.join(dirent(n) for n in nodes)
    while len(d) % SECTOR:
        d += (b'\0' * 64 + struct.pack('<HBB', 0, 0, 0) + struct.pack('<III', NOSTREAM, NOSTREAM, NOSTREAM)
              + b'\0' * 16 + b'\0' * 20 + b'\0' * 12)[:128]
    dir_start = alloc(d)

    # FAT sectors (need to account for themselves)
    nfat = 1
    while True:
        total = len(sectors) + nfat
        if (total + 127) // 128 <= nfat:
            break
        nfat += 1
    assert nfat <= 109
    fat_start = len(sectors)
    for i in range(nfat):
        fat.append(FATSECT)
        sectors.append(None)
    fat += [FREESECT] * (nfat * 128 - len(fat))
    fb = b''.join(struct.pack('<I', x) for x in fat)
    for i in range(nfat):
        sectors[fat_start + i] = fb[i * SECTOR:(i + 1) * SECTOR]

    hdr = bytes.fromhex('D0CF11E0A1B11AE1') + b'\0' * 16
    hdr += struct.pack('<HHHHH', 0x3E, 3, 0xFFFE, 9, 6)
    hdr += b'\0' * 6
    hdr += struct.pack('<I', 0)  # dir sectors (v3 must be 0)
    hdr += struct.pack('<I', nfat)
    hdr += struct.pack('<I', dir_start)
    hdr += struct.pack('<I', 0)  # transaction
    hdr += struct.pack('<I', CUTOFF)
    hdr += struct.pack('<I', minifat_start)
    hdr += struct.pack('<I', n_minifat)
    hdr += struct.pack('<I', ENDOFCHAIN)  # DIFAT start
    hdr += struct.pack('<I', 0)
    difat = [fat_start + i for i in range(nfat)] + [FREESECT] * (109 - nfat)
    hdr += b''.join(struct.pack('<I', x) for x in difat)
    assert len(hdr) == 512
    with open(path, 'wb') as f:
        f.write(hdr)
        for s in sectors:
            f.write(s)


def clone_tree(ole, replace):
    """Build Node tree mirroring an olefile.OleFileIO, replacing stream data by path tuple."""
    root = Node('Root Entry', 5, clsid=bytes.fromhex(ole.root.clsid.replace('-', '')) if ole.root.clsid else b'\0' * 16)
    storages = {(): root}
    for entry in sorted(ole.listdir(streams=True, storages=True), key=len):
        parent = storages[tuple(entry[:-1])]
        t = ole.get_type(entry)
        if t == 1:  # storage
            n = Node(entry[-1], 1)
            storages[tuple(entry)] = n
        else:
            data = replace.get(tuple(entry))
            if data is None:
                data = ole.openstream(entry).read()
            n = Node(entry[-1], 2, data)
        parent.children.append(n)
    return root
