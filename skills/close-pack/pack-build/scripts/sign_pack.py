"""Write the signed filing copy of the pack: the DRAFT status line becomes
the reviewer's sign-off, everything else is untouched. Requires python-pptx.

Usage: sign_pack.py <built_pack.pptx> "<reviewer>" <signed_out.pptx>
  e.g. sign_pack.py "step3/Management Pack - May-26.pptx" "KL" \
       "step3/Management Pack - May-26 SIGNED KL.pptx"

Mirrors write_rec.py's status column: nothing signed carries a DRAFT mark.
Fails (exit 1) if no DRAFT status line is found — the template contract
("DRAFT" on the title slide) has changed and needs looking at.
"""
import datetime
import sys

from pptx import Presentation

MARK = "DRAFT"


def main(pack_path: str, reviewer: str, out_path: str) -> None:
    prs = Presentation(pack_path)
    today = datetime.date.today().isoformat()
    swapped = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                text = "".join(run.text for run in para.runs)
                if MARK in text and para.runs:
                    para.runs[0].text = text.replace(
                        MARK, f"SIGNED {reviewer} {today}", 1)
                    for run in para.runs[1:]:
                        run.text = ""
                    swapped += 1
    if not swapped:
        print(f"sign_pack: no '{MARK}' status line found in {pack_path} - "
              "template contract changed; not writing a signed copy")
        sys.exit(1)
    prs.save(out_path)
    print(f"signed pack written: {out_path} ({swapped} status line(s) -> SIGNED {reviewer})")


if __name__ == "__main__":
    main(*sys.argv[1:4])
