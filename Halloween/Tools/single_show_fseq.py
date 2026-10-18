"""FSEQ v2 sparse projector extraction; matches FPP's documented header format."""
from pathlib import Path
from compression import zstd
import bisect, hashlib, math, struct

class FSEQ:
    def __init__(self, path):
        self.f = Path(path).open('rb'); h = self.f.read(32)
        assert h[:4] == b'PSEQ' and h[7] == 2 and h[20] & 15 == 1
        self.header = h
        self.channels, self.frames = struct.unpack_from('<II', h, 10); self.step = h[18]
        blocks = [struct.unpack('<II', self.f.read(8)) for _ in range(((h[20] & 240) << 4) | h[21])]
        self.sparse = [(int.from_bytes(self.f.read(3), 'little'), int.from_bytes(self.f.read(3), 'little')) for _ in range(h[22])] or [(0, self.channels)]
        assert sum(n for _, n in self.sparse) == self.channels
        self.blocks = [(f, n) for f, n in blocks if n]; self.starts = [f for f, _ in self.blocks]
        pos = struct.unpack_from('<H', h, 4)[0]; self.offsets = []
        for _, n in self.blocks: self.offsets.append(pos); pos += n
        assert pos <= Path(path).stat().st_size
        self.cache_id = -1; self.cache = b''
    def model(self, ms, start, count):
        number = min(self.frames - 1, int(ms / self.step)); i = bisect.bisect_right(self.starts, number) - 1
        if i != self.cache_id:
            self.f.seek(self.offsets[i]); self.cache = zstd.decompress(self.f.read(self.blocks[i][1])); self.cache_id = i
        base = (number - self.starts[i]) * self.channels; out = bytearray(count); offset = 0; first = start - 1
        for a, n in self.sparse:
            x, y = max(a, first), min(a + n, first + count)
            if y > x: out[x - first:y - first] = self.cache[base + offset + x - a:base + offset + y - a]
            offset += n
        return out

def frame_digest(path):
    reader = FSEQ(path); result = hashlib.sha256()
    for frame in range(reader.frames): result.update(reader.model(frame * reader.step, 1, 147456))
    reader.f.close()
    return result.hexdigest(), reader.frames, reader.step

def projector_file(source, destination):
    reader = FSEQ(source)
    frames_per_block = max(3, math.ceil(reader.frames / 3000))
    count = math.ceil(reader.frames / frames_per_block)
    standard = 32 + count * 8 + 6; offset = (standard + 3) // 4 * 4
    header = bytearray(32); header[:4] = b'PSEQ'; header[6:8] = bytes([2, 2])
    struct.pack_into('<H', header, 4, offset); struct.pack_into('<H', header, 8, standard)
    struct.pack_into('<II', header, 10, 147456, reader.frames)
    header[18] = reader.step; header[20] = ((count >> 4) & 240) | 1
    header[21] = count & 255; header[22] = 1; header[24:32] = reader.header[24:32]
    temporary = Path(str(destination) + '.part'); blocks = []; digest = hashlib.sha256()
    with temporary.open('wb') as output:
        output.write(bytes(offset))
        for first in range(0, reader.frames, frames_per_block):
            raw = b''.join(reader.model(frame * reader.step, 1, 147456) for frame in range(first, min(first + frames_per_block, reader.frames)))
            digest.update(raw); compressed = zstd.compress(raw, level=3)
            blocks.append((first, len(compressed))); output.write(compressed)
        output.seek(0); output.write(header)
        for block in blocks: output.write(struct.pack('<II', *block))
        output.write((0).to_bytes(3, 'little') + (147456).to_bytes(3, 'little'))
    reader.f.close(); temporary.replace(destination)
    expected = digest.hexdigest(), reader.frames, reader.step
    assert frame_digest(destination) == expected
    return expected
