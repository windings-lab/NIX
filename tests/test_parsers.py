import pytest

from main import parse_search_results, parse_extras

@pytest.mark.parametrize(
    "html_string,expected",
    [
        # basic case
        (
            """
            <div class="search-title">
                <a href="/user/repo1">Repo 1</a>
                <a href="/user/repo2">Repo 2</a>
                <a>Missing href</a>
            </div>
            """,
            [
                {"url": "https://github.com/user/repo1"},
                {"url": "https://github.com/user/repo2"}
            ]
        ),
        # empty HTML
        ("<div></div>", []),
        # only some valid href
        (
            """
            <div class="search-title">
                <a href="">Empty</a>
                <a href="/repo3">Repo 3</a>
            </div>
            """,
            [{"url": "https://github.com/repo3"}]
        ),
        # multiple divs with search-title
        (
            """
            <div class="search-title"><a href="/repo4">Repo 4</a></div>
            <div class="search-title"><a href="/repo5">Repo 5</a></div>
            """,
            [
                {"url": "https://github.com/repo4"},
                {"url": "https://github.com/repo5"}
            ]
        )
    ]
)
def test_parse_search_results(html_string, expected):
    result = parse_search_results(html_string)
    assert result == expected

@pytest.mark.parametrize(
    "extra_html,expected",
    [
        # language stats exist
        (
            """
            <div itemprop="author">
                <a>owner_name</a>
            </div>
            <div class="BorderGrid-row">
                <h2>Languages</h2>
                <ul>
                    <li><span>Python</span><span>50%</span></li>
                    <li><span>JavaScript</span><span>50%</span></li>
                </ul>
            </div>
            """,
            {
                "extra": {
                    "owner": "owner_name",
                    "language_stats": {"Python": "50", "JavaScript": "50"}
                }
            }
        ),
        # language stats missing
        (
            """
            <div itemprop="author">
                <a>owner_name</a>
            </div>
            """,
            {
                "extra": {
                    "owner": "owner_name",
                    "language_stats": None
                }
            }
        ),
    ]
)
def test_parse_extras(extra_html, expected):
    result = parse_extras(extra_html)
    assert result == expected

def test_parse_extras_missing_owner():
    html_missing_owner = """
        <div class="BorderGrid-row">
            <h2>Languages</h2>
            <ul>
                <li><span>Python</span><span>100%</span></li>
            </ul>
        </div>
    """
    with pytest.raises(IndexError):
        parse_extras(html_missing_owner)