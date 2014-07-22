import itertools
import hashlib
import os

# Script to symlink files in one folder to those in another (even with mismatching dir structures).
# Uses the heuristic that same file name and size means the files are probably the same.


source_root = "/Volumes/TARDIS/Files/Photos - Current/"
target_root = "/Users/lgarron/Pictures/Aperture Library.aplibrary/Masters/"

# Based on https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
# The first few chunks of a JPEG usually list unique EXIF data like the time the photo was taken.
# Since we're mostly using this as a sanity check, the first few blocks should be a sufficient heuristic.
def sha256partial(filename):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for chunk in  itertools.islice(iter(lambda: f.read(128 * sha256.block_size), b''), 4):
            sha256.update(chunk)
    return sha256.hexdigest()

h = {}

for root, dirs, files in os.walk(source_root):
  for file in files:
    file_path = os.path.join(root, file)
    s = os.stat(file_path)

    key = "%d:%s"  % (s.st_size, file)
    if not key in h:
      h[key] = file_path


for root, dirs, files in os.walk(target_root):
  for file in files:
    file_path = os.path.join(root, file)
    s = os.stat(file_path)

    if os.path.islink(file_path): # Easier than stat.S_IFLNK
      print "Already a link: %s" % (file_path)

    key = "%d:%s" % (s.st_size, file)
    if key in h:
      target = h[key]
      if sha256partial(file_path) == sha256partial(target):
        print "Replacing `%s` with symlink to `%s`" % (file_path, target)
        os.remove(file_path)
        os.symlink(target, file_path)
      else:
        print "Hash mismatch between `%s` and `%s`" % (file_path, target)
