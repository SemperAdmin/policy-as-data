"""Write a tool's corrections entry so that re-running the build is a no-op.

Every stage of this pipeline is idempotent: it removes its own prior output
before writing. A record's `corrections` array is output like any other, so a
stage that appends unconditionally grows the record by one entry per build,
and the provenance trail degenerates into a run log.

That matters more here than it looks. A corrections entry is the record's
statement of what was done to it and against which authority. Three identical
entries do not mean the period was replaced three times; they mean the build
ran three times. Anyone reading the record to adjudicate the [ID2] promotion
would be counting builds and calling them changes.

A tool is identified by the `"<name>.py - "` prefix its first change line
already carries, so no new field is introduced and existing records are
recognised without migration. Entries written by any other tool, and entries
written by hand, are left exactly where they are.
"""


def _key(entry, tool):
    changes = entry.get("changes") or []
    return bool(changes) and str(changes[0]).startswith(tool + " - ")


def record(rec, tool, entry):
    """Set this tool's correction entry on `rec`, replacing any earlier one.

    tool  the script's filename, e.g. "normalize_identifiers.py"
    entry the full correction dict, whose changes[0] must open with that name
    """
    changes = entry.get("changes") or []
    if not changes or not str(changes[0]).startswith(tool + " - "):
        raise ValueError(
            f"changes[0] must open with {tool!r} so the entry can be found "
            f"again on the next run; got {changes[0] if changes else None!r}")
    kept = [c for c in (rec.get("corrections") or []) if not _key(c, tool)]
    kept.append(entry)
    rec["corrections"] = kept
    return rec
