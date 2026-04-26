import pytest

import gen_fingerprints
from gen_fingerprints import Fingerprint


@pytest.fixture(autouse=True)
def _skip_network(monkeypatch):
    """Stub out network verification for every Fingerprint built in tests."""
    monkeypatch.setattr(Fingerprint, "verify", lambda self: (False, "skipped"))


def row(engine="Service", status="Vulnerable", verified="🟥", domains="example.com",
        fingerprint="some text", discussion="", documentation=""):
    return f"| {engine} | {status} | {verified} | {domains} | {fingerprint} | {discussion} | {documentation} |"


def test_basic_row_parses_all_columns():
    f = Fingerprint(row(engine="Ghost", domains="ghost.io", fingerprint="Site unavailable"))
    assert f.engine == "Ghost"
    assert f.status == "Vulnerable"
    assert f.vulnerable is True
    assert f.domains == ["ghost.io"]
    assert f.fingerprint == "Site unavailable"
    assert f.nxdomain is False
    assert f.http_status is None


def test_nxdomain_flag_set():
    f = Fingerprint(row(engine="Foo", fingerprint="NXDOMAIN"))
    assert f.nxdomain is True
    assert f.http_status is None


def test_http_status_parsed():
    f = Fingerprint(row(engine="Foo", fingerprint="HTTP_STATUS=404"))
    assert f.http_status == 404
    assert f.nxdomain is False


def test_http_status_case_insensitive():
    f = Fingerprint(row(engine="Foo", fingerprint="http_status=301"))
    assert f.http_status == 301


def test_multiple_domains_split_on_commas_and_spaces():
    f = Fingerprint(row(domains="a.com, b.com c.com"))
    assert f.domains == ["a.com", "b.com", "c.com"]


def test_status_is_capitalised():
    f = Fingerprint(row(status="not vulnerable"))
    assert f.status == "Not vulnerable"
    assert f.vulnerable is False


def test_header_row_is_skipped():
    header = "| Engine | Status | Verified by CI/CD | Domains | Fingerprint | Discussion | Documentation |"
    with pytest.raises(AssertionError):
        Fingerprint(header)


def test_divider_row_is_skipped():
    divider = "| ----- | ------ | ----------------- | ------- | ----------- | ---------- | ------------- |"
    with pytest.raises(AssertionError):
        Fingerprint(divider)


def test_invalid_regex_falls_back_with_warning(capsys):
    f = Fingerprint(row(engine="Bad", fingerprint="(unclosed"))
    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert "Bad" in captured.err
    # Fallback regex must literal-match the original string
    assert f.fingerprint_regex.findall("(unclosed appears here") == ["(unclosed"]


def test_valid_regex_compiles_directly(capsys):
    f = Fingerprint(row(fingerprint=r"Tunnel .*\.ngrok\.io not found"))
    captured = capsys.readouterr()
    assert "WARNING" not in captured.err
    assert f.fingerprint_regex.search("Tunnel abc.ngrok.io not found")


def test_padding_for_short_rows():
    short = "| Foo | Vulnerable | 🟥 |"
    f = Fingerprint(short)
    assert f.engine == "Foo"
    assert f.fingerprint == ""
    assert f.discussion == ""
    assert f.documentation == ""


def test_json_serialisation_round_trip():
    f = Fingerprint(row(engine="Foo", domains="foo.com", fingerprint="NXDOMAIN"))
    j = f.json
    assert j["service"] == "Foo"
    assert j["cname"] == ["foo.com"]
    assert j["nxdomain"] is True
    assert j["http_status"] is None
    assert j["status"] == "Vulnerable"
    assert j["vulnerable"] is True


def test_parse_fingerprints_uses_correct_row_in_error(monkeypatch, capsys):
    """Regression: previously the closure leaked the last row from the outer loop,
    so every error message reported the same row regardless of which one failed."""

    def fail_init(self, table_row):
        cols = [c.strip(" `") for c in table_row.split("|")][1:-1]
        raise AssertionError(cols[0] if cols else "")

    monkeypatch.setattr(Fingerprint, "__init__", fail_init)
    rows = [
        "| RowAlpha | Vulnerable | 🟥 |  | x |  |  |",
        "| RowBeta  | Vulnerable | 🟥 |  | y |  |  |",
        "| RowGamma | Vulnerable | 🟥 |  | z |  |  |",
    ]
    monkeypatch.setattr(gen_fingerprints, "readme_sections", ["", "\n".join(rows) + "\n"])
    gen_fingerprints.parse_fingerprints()
    err = capsys.readouterr().err
    # Each row must appear in its own "Invalid signature" line — not the row dump
    # leaking from a sibling future.
    for r in rows:
        assert f"Invalid signature: {r}" in err, f"missing diagnostic for {r!r}"
