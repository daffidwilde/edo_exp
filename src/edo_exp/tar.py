""" For tarballing and removing directories. """

import os
import tarfile


def make_tarball(root):
    """ Compress the data in `root` to a tarball and remove the original. """

    data = root / "data"

    with tarfile.open(root + ".tar.gz", "w:gz") as tar:
        tar.add(data, arcname=os.path.basename(data))

    os.system(f"rm -r {data}")
