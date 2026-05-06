import re
import pytest
from app.terminal import render_terminal_page, W

_ANSI = re.compile(r'\033\[[0-9;]*m')


def vlen(s: str) -> int:
    return len(_ANSI.sub('', s))


def _render(**overrides) -> str:
    """Render with sensible defaults; override any key."""
    data = {
        "t": {"home": {"about-desc-1": "Short bio text for testing."}},
        "experiences": [],
        "skills": [],
        "open_to_work": None,
    }
    data.update(overrides)
    return render_terminal_page("en", data)


# ── Width invariant ────────────────────────────────────────────────────────────

def test_no_line_exceeds_terminal_width():
    """No non-blank line may be wider than W — the main overflow invariant."""
    output = _render(
        skills=[
            {"title": "Programming",     "skills_list": "Application, game, and scripting"},
            {"title": "Web Development", "skills_list": "Building SPAs, MPAs and REST APIs"},
            {"title": "Databases",       "skills_list": "Design and data modeling"},
            {"title": "DevOps & Cloud",  "skills_list": "Containerization with Docker"},
        ],
        experiences=[
            {"title": "Freelance Web Developer", "company": "Freelance",  "date": "March 2026 - Present"},
            {"title": "Software Developer",       "company": "Airpim SRL", "date": "May 2024 - May 2025"},
        ],
        open_to_work={"is_enabled": True, "title": "Open to Work"},
    )
    for line in output.splitlines():
        if line.strip():
            assert vlen(line) <= W, f"Overflow ({vlen(line)} > {W}): {line!r}"


def test_all_non_blank_lines_are_exactly_terminal_width():
    """Every non-blank line is padded/constructed to be exactly W chars."""
    output = _render(
        skills=[{"title": "Programming", "skills_list": "desc"}],
        experiences=[{"title": "Dev", "company": "Co", "date": "2024"}],
    )
    for line in output.splitlines():
        if line.strip():
            assert vlen(line) == W, f"Width {vlen(line)} != {W}: {line!r}"


def test_long_skill_titles_do_not_overflow():
    """Regression: the old :<9 format didn't truncate, so 'Web Development'
    (15 chars) pushed content past the right border of the skills box."""
    output = _render(skills=[
        {"title": "Programming",                   "skills_list": "desc"},
        {"title": "Web Development",               "skills_list": "desc"},
        {"title": "DevOps & Cloud Infrastructure", "skills_list": "desc"},
    ])
    for line in output.splitlines():
        if line.strip():
            assert vlen(line) <= W, f"Long title overflow: {line!r}"


# ── Header ─────────────────────────────────────────────────────────────────────

def test_header_contains_name_and_location():
    output = _render()
    assert "STEFANO VIDESOTT" in output
    assert "Trento, Italy" in output


def test_open_to_work_shown_when_enabled():
    output = _render(open_to_work={"is_enabled": True, "title": "Open to Work"})
    assert "Open to Work" in output


def test_open_to_work_custom_title():
    output = _render(open_to_work={"is_enabled": True, "title": "Available for hire"})
    assert "Available for hire" in output


def test_open_to_work_hidden_when_disabled():
    output = _render(open_to_work={"is_enabled": False, "title": "Open to Work"})
    assert "Open to Work" not in output


def test_open_to_work_hidden_when_none():
    output = _render(open_to_work=None)
    assert "Open to Work" not in output


# ── About ──────────────────────────────────────────────────────────────────────

def test_about_text_appears():
    output = _render(**{"t": {"home": {"about-desc-1": "Unique marker text XYZ."}}})
    assert "Unique marker text XYZ" in output


def test_about_long_text_capped_at_five_lines():
    """A very long about paragraph must not produce more than 5 box rows."""
    long_text = "word " * 300
    output = _render(**{"t": {"home": {"about-desc-1": long_text}}})
    lines = output.splitlines()
    in_about = False
    content_lines = 0
    for line in lines:
        plain = _ANSI.sub("", line)
        if "┌─About" in plain:
            in_about = True
            continue
        if in_about and plain.startswith("└"):
            break
        if in_about:
            content_lines += 1
    assert content_lines <= 5


def test_about_missing_key_does_not_crash():
    output = render_terminal_page("en", {"t": {"home": {}}, "skills": [], "experiences": []})
    assert "STEFANO VIDESOTT" in output


# ── Skills ─────────────────────────────────────────────────────────────────────

def test_skill_titles_appear():
    output = _render(skills=[
        {"title": "Programming",     "skills_list": "whatever"},
        {"title": "Web Development", "skills_list": "whatever"},
    ])
    assert "Programming" in output
    assert "Web Development" in output


def test_skills_box_empty_when_no_skills():
    """The Skills header always appears (paired with About), but no bullet items."""
    output = _render(skills=[])
    assert "Skills" in output  # box header always shown
    # Skill bullets are rendered as ANSI-grey "·" followed by a bold title.
    # Check no such pattern exists in the skills box lines.
    lines = output.splitlines()
    in_skills = False
    for line in lines:
        plain = _ANSI.sub("", line)
        if "┌─Skills" in plain:
            in_skills = True
            continue
        if in_skills and plain.startswith("└"):
            break
        if in_skills:
            assert not plain.strip().startswith("·"), f"Unexpected skill item: {plain!r}"


def test_at_most_six_skills_shown():
    output = _render(skills=[
        {"title": f"Category {i}", "skills_list": ""} for i in range(10)
    ])
    # Only 6 should appear; categories 7-10 should be absent
    assert "Category 6" not in output


# ── Experience ─────────────────────────────────────────────────────────────────

def test_experience_fields_appear():
    output = _render(experiences=[
        {"title": "Software Engineer", "company": "Acme Corp", "date": "2024 – Present"},
    ])
    assert "Software Engineer" in output
    assert "Acme Corp" in output
    assert "2024" in output


def test_experience_section_absent_when_empty():
    output = _render(experiences=[])
    assert "Experience" not in output


def test_at_most_three_experiences_shown():
    output = _render(experiences=[
        {"title": f"Job {i}", "company": "Co", "date": "2024"} for i in range(5)
    ])
    assert "Job 3" not in output
    assert "Job 4" not in output


def test_experience_without_company_or_date():
    output = _render(experiences=[{"title": "Freelancer", "company": "", "date": ""}])
    assert "Freelancer" in output


# ── Contact & Links ────────────────────────────────────────────────────────────

def test_contact_info_present():
    output = _render()
    assert "work@stefanovidesott.com" in output
    assert "stefanovidesott.com" in output


def test_links_present():
    output = _render()
    assert "github.com/StefanoVidesott" in output
    assert "linkedin.com/in/stefano-videsott" in output


# ── Robustness ─────────────────────────────────────────────────────────────────

def test_empty_data_does_not_crash():
    output = render_terminal_page("en", {})
    assert isinstance(output, str)
    assert len(output) > 0


def test_italian_lang_accepted():
    output = render_terminal_page("it", {
        "t": {"home": {"about-desc-1": "Testo bio."}},
        "experiences": [],
        "skills": [],
        "open_to_work": None,
    })
    assert "STEFANO VIDESOTT" in output


def test_output_ends_with_newline():
    output = _render()
    assert output.endswith("\n")
