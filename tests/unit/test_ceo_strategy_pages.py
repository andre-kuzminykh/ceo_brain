"""Structural checks for the CEO Brain Strategy static pages.

These tests don't execute the HTML — they read each page as text and assert
that the expected markup / JS hooks are present.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PAGES_DIR = Path(__file__).resolve().parents[2] / "docs" / "ceo_strategy"

ALL_PAGES = [
    "index.html",
    "architecture.html",
    "ai-memory.html",
    "performance.html",
    "tasks.html",
    "notes.html",
    "calendar.html",
    "email.html",
    "docs.html",
    "tables.html",
    "slides.html",
    "reports.html",
]

MODULE_PAGES = [p for p in ALL_PAGES if p not in {"index.html", "architecture.html"}]


@pytest.fixture(params=ALL_PAGES)
def page(request) -> tuple[str, str]:
    name = request.param
    text = (PAGES_DIR / name).read_text(encoding="utf-8")
    return name, text


class TestSidebarStructure:
    def test_doctype(self, page):
        _, html = page
        assert html.strip().startswith("<!DOCTYPE html>")

    def test_sidebar_has_id(self, page):
        _, html = page
        assert 'id="sidebar"' in html, "sidebar must expose id for JS to find it"

    def test_sidebar_has_class(self, page):
        _, html = page
        assert 'class="sidebar"' in html or 'class="sidebar ' in html

    def test_sidebar_toggle_button(self, page):
        _, html = page
        assert 'class="sidebar-toggle"' in html
        assert "onclick=\"toggleSidebar()\"" in html

    def test_mobile_menu_button(self, page):
        _, html = page
        assert 'class="mobile-menu-btn"' in html

    def test_sidebar_overlay(self, page):
        _, html = page
        assert 'id="sidebar-overlay"' in html

    def test_toggle_sidebar_js(self, page):
        _, html = page
        assert "toggleSidebar" in html

    def test_toggle_sidebar_uses_correct_classes(self, page):
        _, html = page
        # mobile-open for mobile overlay, collapsed for desktop collapse
        assert "mobile-open" in html
        assert "collapsed" in html

    def test_collapsible_css_present(self, page):
        _, html = page
        assert "Collapsible sidebar + mobile overlay" in html


class TestSidebarContent:
    def test_all_module_links_present(self, page):
        _, html = page
        for link in MODULE_PAGES:
            assert link in html, f"expected link to {link}"

    def test_architecture_link_in_resources(self, page):
        _, html = page
        assert "architecture.html" in html

    def test_overview_link(self, page):
        _, html = page
        assert "index.html" in html or page[0] == "index.html"


class TestHtmlIntegrity:
    def test_balanced_script_tags(self, page):
        _, html = page
        opens = len(re.findall(r"<script[\s>]", html))
        closes = html.count("</script>")
        assert opens == closes, f"script tags not balanced ({opens} open, {closes} close)"

    def test_balanced_style_tags(self, page):
        _, html = page
        opens = len(re.findall(r"<style[\s>]", html))
        closes = html.count("</style>")
        assert opens == closes, f"style tags not balanced ({opens} open, {closes} close)"

    def test_balanced_body_tags(self, page):
        _, html = page
        assert html.count("<body>") == 1
        assert html.count("</body>") == 1

    def test_no_orphan_mobile_header_markup(self, page):
        _, html = page
        assert 'class="mobile-header"' not in html
        assert 'class="menu-toggle"' not in html

    def test_no_stale_mobile_active_class(self, page):
        _, html = page
        assert "mobile-active" not in html, "old class mobile-active must be replaced by mobile-open"


class TestModulePages:
    @pytest.mark.parametrize("page_name", MODULE_PAGES)
    def test_toggle_has_asis_tobe(self, page_name):
        html = (PAGES_DIR / page_name).read_text(encoding="utf-8")
        assert 'id="btn-asis"' in html
        assert 'id="btn-tobe"' in html

    @pytest.mark.parametrize("page_name", MODULE_PAGES)
    def test_views_present(self, page_name):
        html = (PAGES_DIR / page_name).read_text(encoding="utf-8")
        assert 'id="view-asis"' in html
        assert 'id="view-tobe"' in html

    @pytest.mark.parametrize("page_name", MODULE_PAGES)
    def test_both_diagrams_present(self, page_name):
        html = (PAGES_DIR / page_name).read_text(encoding="utf-8")
        assert html.count("sequenceDiagram") >= 2, "expected AS-IS and TO-BE mermaid diagrams"

    @pytest.mark.parametrize("page_name", MODULE_PAGES)
    def test_drawer_present(self, page_name):
        html = (PAGES_DIR / page_name).read_text(encoding="utf-8")
        assert 'id="drawer"' in html
        assert 'class="drawer"' in html

    @pytest.mark.parametrize("page_name", MODULE_PAGES)
    def test_five_user_stories(self, page_name):
        html = (PAGES_DIR / page_name).read_text(encoding="utf-8")
        stories = re.findall(r'<li><span>', html)
        # story-list items use exactly this pattern
        assert len(stories) >= 5, f"expected at least 5 user stories in {page_name}, got {len(stories)}"


class TestIndexPage:
    def test_modules_data_order(self):
        html = (PAGES_DIR / "index.html").read_text(encoding="utf-8")
        ids_in_order = re.findall(r"id: '(ai_memory|performance|tasks|email|reports|notes|calendar|docs|tables|slides)'", html)
        assert ids_in_order == [
            "ai_memory", "performance", "tasks",
            "email", "reports", "notes",
            "calendar", "docs", "tables", "slides",
        ], f"MODULES array order wrong: {ids_in_order}"

    def test_ten_modules(self):
        html = (PAGES_DIR / "index.html").read_text(encoding="utf-8")
        ids = re.findall(r"^                id: '", html, re.MULTILINE)
        assert len(ids) == 10

    def test_has_drawer(self):
        html = (PAGES_DIR / "index.html").read_text(encoding="utf-8")
        assert 'id="drawer"' in html


class TestArchitecturePage:
    def test_has_six_layers(self):
        html = (PAGES_DIR / "architecture.html").read_text(encoding="utf-8")
        for label in [
            "Client Layer",
            "Business Layer",
            "AI Layer",
            "Services &amp; Orchestration Layer",
            "Data Layer",
            "Infrastructure (Foundation)",
        ]:
            assert label in html, f"missing architecture layer: {label}"
