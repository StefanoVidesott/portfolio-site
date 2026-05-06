import re
import textwrap

RST  = "\033[0m"
BOLD = "\033[1m"
CYN  = "\033[36m"
YLW  = "\033[33m"
GRN  = "\033[32m"
WHT  = "\033[97m"
GRY  = "\033[90m"

W = 80

_ANSI = re.compile(r'\033\[[0-9;]*m')


def _vlen(s: str) -> int:
    return len(_ANSI.sub('', s))


def _rpad(s: str, width: int) -> str:
    return s + ' ' * max(0, width - _vlen(s))


def _box_top(title: str, title_color: str, w: int, c: str = GRY) -> str:
    filler = w - len(title) - 3
    return f"{c}┌─{title_color}{BOLD}{title}{RST}{c}{'─' * max(0, filler)}┐{RST}"


def _box_bot(w: int, c: str = GRY) -> str:
    return f"{c}└{'─' * (w - 2)}┘{RST}"


def _box_row(content: str, w: int, c: str = GRY) -> str:
    return f"{c}│{RST}{_rpad(content, w - 2)}{c}│{RST}"


def render_terminal_page(lang: str, data: dict) -> str:
    t = data.get("t", {})
    home_t = t.get("home", {})
    experiences = data.get("experiences", [])
    skills      = data.get("skills", [])
    open_to_work = data.get("open_to_work")

    out = []
    inner = W - 2  # 78

    # ── Header ────────────────────────────────────────────────────────────────
    out.append("")
    out.append(f"{CYN}╭{'─' * inner}╮{RST}")

    name_part = f"  {BOLD}{WHT}STEFANO VIDESOTT{RST}"
    loc_part  = f"{GRY}Trento, Italy{RST}  "
    gap_h     = inner - _vlen(name_part) - _vlen(loc_part)
    out.append(f"{CYN}│{RST}{name_part}{' ' * max(0, gap_h)}{loc_part}{CYN}│{RST}")

    sub = f"  {GRY}Software Engineer  ·  CS Student  ·  Freelancer{RST}"
    out.append(f"{CYN}│{RST}{_rpad(sub, inner)}{CYN}│{RST}")

    if open_to_work and open_to_work.get("is_enabled"):
        otw = f"  {GRN}{BOLD}● {open_to_work.get('title', 'Open to Work')}{RST}"
        out.append(f"{CYN}│{RST}{_rpad(otw, inner)}{CYN}│{RST}")

    out.append(f"{CYN}╰{'─' * inner}╯{RST}")
    out.append("")

    # ── About + Skills (side by side) ─────────────────────────────────────────
    # LW wider so the about paragraph fits in fewer lines without being cut off.
    # Skills shows only category titles — descriptions are too long for terminal.
    ABW = 47                 # About box width
    SKW = W - ABW - 1        # Skills box width (32)

    about_text  = home_t.get("about-desc-1", "")
    about_lines = textwrap.wrap(about_text, width=ABW - 4)[:5] if about_text else []

    sk_title_max = SKW - 2 - 4  # inner minus "  · " prefix
    skill_rows = []
    for sk in skills[:6]:
        sk_title = sk.get("title", "")
        if len(sk_title) > sk_title_max:
            sk_title = sk_title[:sk_title_max - 1] + "…"
        skill_rows.append(f"  {GRY}·{RST} {BOLD}{WHT}{sk_title}{RST}")

    box_h = max(len(about_lines), len(skill_rows), 1)
    out.append(_box_top("About", CYN, ABW) + " " + _box_top("Skills", CYN, SKW))
    for i in range(box_h):
        l = f" {about_lines[i]}" if i < len(about_lines) else ""
        r = skill_rows[i] if i < len(skill_rows) else ""
        out.append(_box_row(l, ABW) + " " + _box_row(r, SKW))
    out.append(_box_bot(ABW) + " " + _box_bot(SKW))
    out.append("")

    # ── Experience ────────────────────────────────────────────────────────────
    if experiences:
        out.append(_box_top("Experience", YLW, W))
        for job in experiences[:3]:
            job_title = job.get("title", "")
            company   = job.get("company", "")
            date      = job.get("date", "")

            row = f"  {YLW}◆{RST}  {BOLD}{WHT}{job_title}{RST}"
            if company:
                row += f"  {GRY}@{RST}  {CYN}{company}{RST}"
            if date:
                row += f"  {GRY}· {date}{RST}"
            out.append(_box_row(row, W))
        out.append(_box_bot(W))
        out.append("")

    # ── Contact + Links (side by side) ────────────────────────────────────────
    CLW = 34                 # Contact box width
    LNW = W - CLW - 1        # Links box width (45) — needs room for full LinkedIn URL

    contact_rows = [
        f"  {CYN}@{RST}   work@stefanovidesott.com",
        f"  {CYN}~{RST}   stefanovidesott.com",
    ]
    link_rows = [
        f"  {GRY}GH{RST}  {CYN}github.com/StefanoVidesott{RST}",
        f"  {GRY}LI{RST}  {CYN}linkedin.com/in/stefano-videsott{RST}",
    ]

    out.append(_box_top("Contact", CYN, CLW) + " " + _box_top("Links", CYN, LNW))
    for i in range(max(len(contact_rows), len(link_rows))):
        l = contact_rows[i] if i < len(contact_rows) else ""
        r = link_rows[i] if i < len(link_rows) else ""
        out.append(_box_row(l, CLW) + " " + _box_row(r, LNW))
    out.append(_box_bot(CLW) + " " + _box_bot(LNW))
    out.append("")

    # ── Footer ────────────────────────────────────────────────────────────────
    hr = f"{GRY}{'─' * W}{RST}"
    out.append(hr)
    left_f  = f"  {GRY}$ curl stefanovidesott.com | less -R{RST}"
    right_f = f"{GRY}stefanovidesott.com  {RST}"
    gap_f   = W - _vlen(left_f) - _vlen(right_f)
    out.append(left_f + ' ' * max(0, gap_f) + right_f)
    out.append(hr)
    out.append("")

    return "\n".join(out)
