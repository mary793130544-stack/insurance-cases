"""Reconstruct the verified, complete website for GitHub Pages."""
import gzip
import hashlib
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'data-app-build.json').read_text())
assert manifest['kind'] == 'separate-data-v1'
target = root / '_site'
target.mkdir(exist_ok=True)

def verify(path, record):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    assert path.stat().st_size == record['bytes'], 'File size mismatch'
    assert digest.hexdigest() == record['sha256'], 'File checksum mismatch'

snapshot = manifest['snapshot']
assert Path(snapshot['path']).name == snapshot['path']
parts = sorted(root.glob('snapshot.json.gz.part*'))
assert len(parts) == 2, 'Both compressed data parts are required'
compressed = root / 'snapshot.joined.gz'
try:
    with compressed.open('wb') as output:
        for part in parts:
            with part.open('rb') as source:
                shutil.copyfileobj(source, output)
    with gzip.open(compressed, 'rb') as source, (target / snapshot['path']).open('wb') as output:
        shutil.copyfileobj(source, output)
finally:
    compressed.unlink(missing_ok=True)
verify(target / snapshot['path'], snapshot)
verify(root / 'index.html', manifest['html'])
shutil.copyfile(root / 'index.html', target / 'index.html')
shutil.copyfile(root / 'data-app-build.json', target / 'data-app-build.json')
(target / '.nojekyll').touch()
print('Complete website verified and ready for GitHub Pages.')
