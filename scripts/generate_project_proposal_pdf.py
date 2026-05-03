import textwrap
from pathlib import Path


OUTPUT_PATH = Path("docs/project_proposal.pdf")


CONTENT = [
    ("title", "Easint Project Proposal"),
    ("subtitle", "A guided OSINT investigation platform focused on analysis, learning, and reporting"),
    ("body", "Project overview"),
    (
        "text",
        "Easint is a web-based OSINT platform created to reduce the friction of digital investigations. "
        "Instead of forcing users to jump between disconnected tools, it combines collection, organization, "
        "interpretation, and reporting in one workflow."
    ),
    ("body", "Core value proposition"),
    (
        "bullet",
        "18+ integrated tools for file analysis, network intelligence, domain intelligence, and identity research."
    ),
    (
        "bullet",
        "Saved investigations that keep related findings grouped, searchable, and easier to review."
    ),
    (
        "bullet",
        "AI-assisted analysis that summarizes risk, identifies correlations, and suggests next steps."
    ),
    (
        "bullet",
        "Built-in export support for turning investigation outputs into structured reports."
    ),
    (
        "bullet",
        "OPSEC and learning content that helps users understand safer and more responsible OSINT practice."
    ),
    ("body", "Key features"),
    (
        "bullet",
        "File workflows: upload analysis, hash checking, and metadata extraction."
    ),
    (
        "bullet",
        "Infrastructure workflows: IP reputation, geolocation, reverse IP, WHOIS, DNS, SSL, and subdomain enumeration."
    ),
    (
        "bullet",
        "Identity workflows: email OSINT, breach checks, and username discovery."
    ),
    (
        "bullet",
        "Investigation dashboard: create cases, track status, tag findings, and review result history."
    ),
    (
        "bullet",
        "AI dashboard support: ask questions about an investigation and receive summary-level guidance."
    ),
    ("body", "Why it stands out against similar tools"),
    (
        "bullet",
        "Many similar tools focus on one lookup at a time. Easint keeps the full investigation context in one place."
    ),
    (
        "bullet",
        "Many tools return raw data only. Easint adds interpretation through AI-assisted analysis and follow-up guidance."
    ),
    (
        "bullet",
        "Many tools are technical or overwhelming for new users. Easint introduces a guided homepage and clearer navigation."
    ),
    (
        "bullet",
        "Many tools support collection but not learning. Easint adds OPSEC and educational content for students and beginners."
    ),
    (
        "bullet",
        "Many tools require separate notes and manual report writing. Easint is designed around saved investigations and report export."
    ),
    ("body", "Target users"),
    (
        "bullet",
        "Cybersecurity students learning practical OSINT workflows."
    ),
    (
        "bullet",
        "Researchers and analysts handling small to medium investigations."
    ),
    (
        "bullet",
        "Teams that need organized case tracking instead of isolated checks."
    ),
    ("body", "Expected impact"),
    (
        "text",
        "Easint improves efficiency by reducing tool-switching, supports better case management through saved investigations, "
        "and increases accessibility by combining operational capability with guidance. Its strongest advantage is that it is "
        "not only a toolbox; it is a lightweight investigation environment."
    ),
    ("body", "Positioning statement"),
    (
        "text",
        "Easint helps users investigate, understand, and present OSINT findings in one guided workflow."
    ),
]


def escape_pdf_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def wrap_text(text: str, width: int):
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)


def build_pages():
    pages = []
    page = []
    y = 770

    def ensure_space(lines_needed: int, line_height: int):
        nonlocal page, y
        if y - (lines_needed * line_height) < 60:
            pages.append(page)
            page = []
            y = 770

    for kind, value in CONTENT:
        if kind == "title":
            ensure_space(2, 24)
            page.append(("F2", 20, 54, y, value))
            y -= 30
        elif kind == "subtitle":
            lines = wrap_text(value, 70)
            ensure_space(len(lines) + 1, 16)
            for line in lines:
                page.append(("F1", 12, 54, y, line))
                y -= 16
            y -= 8
        elif kind == "body":
            ensure_space(2, 18)
            page.append(("F2", 14, 54, y, value))
            y -= 22
        elif kind == "text":
            lines = wrap_text(value, 88)
            ensure_space(len(lines) + 1, 15)
            for line in lines:
                page.append(("F1", 11, 54, y, line))
                y -= 15
            y -= 6
        elif kind == "bullet":
            lines = wrap_text(value, 80)
            ensure_space(len(lines) + 1, 15)
            for index, line in enumerate(lines):
                prefix = "- " if index == 0 else "  "
                page.append(("F1", 11, 54, y, prefix + line))
                y -= 15
            y -= 3

    if page:
        pages.append(page)
    return pages


def build_content_stream(page_items, page_number, total_pages):
    commands = ["BT"]
    for font_name, size, x, y, text in page_items:
        commands.append(f"/{font_name} {size} Tf")
        commands.append(f"1 0 0 1 {x} {y} Tm")
        commands.append(f"({escape_pdf_text(text)}) Tj")
    commands.extend(
        [
            "/F1 10 Tf",
            f"1 0 0 1 54 30 Tm",
            f"(Generated on 2026-04-21 | Page {page_number} of {total_pages}) Tj",
            "ET",
        ]
    )
    return "\n".join(commands).encode("latin-1", errors="replace")


def generate_pdf(output_path: Path):
    pages = build_pages()
    objects = []

    def add_object(data: bytes):
        objects.append(data)
        return len(objects)

    catalog_id = add_object(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids_placeholder = b"<< /Type /Pages /Count 0 /Kids [] >>"
    pages_id = add_object(kids_placeholder)
    font1_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    font2_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

    page_ids = []
    content_ids = []
    total_pages = len(pages)

    for index, page_items in enumerate(pages, start=1):
        stream = build_content_stream(page_items, index, total_pages)
        content_id = add_object(
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream"
        )
        page_id = add_object(
            (
                f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 595 842] "
                f"/Resources << /Font << /F1 {font1_id} 0 R /F2 {font2_id} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            ).encode("ascii")
        )
        content_ids.append(content_id)
        page_ids.append(page_id)

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[pages_id - 1] = f"<< /Type /Pages /Count {len(page_ids)} /Kids [{kids}] >>".encode("ascii")

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for obj_id, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{obj_id} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(pdf)


if __name__ == "__main__":
    generate_pdf(OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH}")
