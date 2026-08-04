"""Write a record so an interrupted run cannot leave a broken one.

This exists because it happened. A build was interrupted mid-write and left
NAVMC-1200.1L.json truncated at 1.3 MB of an intended 9.2 MB - valid on disk
as far as the filesystem was concerned, and unparseable to everything that
opened it afterwards. The next tool in the chain failed with a JSON decode
error 24,671 lines in, which is a long way from the actual problem.

A store of record that can be corrupted by Ctrl-C is not a store of record.

os.replace is atomic on POSIX and on Windows: the destination either has the
old bytes or all of the new ones, never a prefix.
"""

import json
import os
import tempfile


def write_json(path, obj, indent=1):
    """Serialize fully, then swap. Never leave a partial file at `path`."""
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=indent, ensure_ascii=False)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        # BaseException, not Exception: KeyboardInterrupt is the case this
        # function exists for, and it does not inherit from Exception.
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_text(path, text):
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
