#!/usr/bin/env python3
"""Build every catalogue nail with 'nail.py' and weigh it against its source's count.

    python3 tools/check_masses.py

The tables in 'imperial.j2' and 'metric.j2' carry their source's approximate
count per pound or per kilogram. Nothing builds from that count, which is what
makes it a check: a nail's volume times the density of steel has to come back
to it, and a row that does not is a row to compare with its source again - a
diameter typed wrong moves the mass by the square of the error. Where a nail is
mostly shank the two agree to within about 10 %; where it is mostly head the
model is heavier, because no table states how thick a head is and 'nail.py' has
to assume one; and the heaviest metric sizes' counts are rounded to a handful
per kg. 'imperial.j2' and 'metric.j2' say which rows are off and why. Prints
every row, flags the ones off by more than 12 %, and exits 0 either way: it is
a reading, not a gate.

Needs build123d (the version PartCAD's sandbox pins) and Jinja2.
"""

import pathlib
import sys
import xml.parsers.expat  # noqa: F401 - before OCP loads its own libexpat, or pyexpat cannot load

import jinja2

ROOT = pathlib.Path(__file__).resolve().parent.parent
STEEL = 0.00787  # g/mm^3, as //pub/std/manufacturing/material/metal:steel-1018 states it
POUND = 453.59237  # g


def tables():
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(ROOT)))
    env.globals.update({"INCH": 25.4})
    imperial = env.from_string("{% from 'imperial.j2' import families %}{{ families | tojson }}").render()
    metric = env.from_string(
        "{% from 'metric.j2' import families, sizes, heads %}"
        "{{ {'families': families, 'sizes': sizes, 'heads': heads | dictsort} | tojson }}"
    ).render()
    import json

    return json.loads(imperial), json.loads(metric)


def build(**overrides):
    """Run nail.py with these parameters, the way PartCAD hands them in."""
    lines = []
    for line in (ROOT / "nail.py").read_text().splitlines():
        name = line.split("=", 1)[0].strip()
        if name in overrides and "=" in line and not line.startswith(" "):
            line = "%s = %r" % (name, overrides[name])
        lines.append(line)
    scope = {}
    exec(compile("\n".join(lines), "nail.py", "exec"), scope)
    return scope["nail"]


def report(family, name, grams, expected):
    error = (grams - expected) / expected * 100
    flag = "  <-- compare with the source" if abs(error) > 12 else ""
    print("%-24s %-20s %8.3f g vs %8.3f g (%+5.1f%%)%s" % (family, name, grams, expected, error, flag))


def main():
    imperial, metric = tables()
    for family in imperial:
        for name, L, D, H, count in family["rows"]:
            if not count:
                continue
            nail = build(d=D * 25.4, length=L * 25.4, head_d=H * 25.4, head=family["head"], measured=family["measured"])
            report(family["name"], name, nail.volume * STEEL, POUND / count)
    heads = {float(d): head for d, head in metric["heads"]}
    for family in metric["families"]:
        for d, length, count in metric["sizes"]:
            nail = build(
                d=d, length=float(length), head_d=heads[d][0], head=family["head"], measured=family["measured"]
            )
            report(family["name"], "%.1fx%d" % (d, length), nail.volume * STEEL, 1000.0 / count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
