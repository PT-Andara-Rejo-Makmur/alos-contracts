import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent / "scripts"))
import generate_typescript as g  # noqa: E402

expected = g.render()
current = pathlib.Path("generated/typescript/factory.ts").read_text(encoding="utf-8")
lines = current.split("\n")
out = [
    "equal=" + str(expected == current),
    "line155=" + repr(lines[154]),
    "line177=" + repr(lines[176]),
]
for i, line in enumerate(expected.split("\n")):
    if "replace(/" in line:
        out.append("expected:%d=%s" % (i + 1, repr(line)))
for i, line in enumerate(lines):
    if "replace(/" in line:
        out.append("current:%d=%s" % (i + 1, repr(line)))
pathlib.Path("_diag.txt").write_text("\n".join(out), encoding="utf-8")