from research_rag.ingestion.cleaner import (
    clean_text,
    fix_ligatures,
    join_hyphenated_words,
    remove_control_characters,
    remove_noise_lines,
)


def test_fix_ligatures_turns_special_fi_into_normal_letters():
    assert fix_ligatures("full ﬁne-tuning") == "full fine-tuning"


def test_join_hyphenated_words_across_a_line_break():
    assert join_hyphenated_words("indepen-\ndent") == "independent"


def test_join_hyphenated_words_keeps_normal_hyphens():
    assert join_hyphenated_words("large-scale") == "large-scale"


def test_remove_noise_lines_drops_watermark_and_last_line_page_number():
    page = "Some text.\n7\narXiv:2106.09685v2  [cs.CL]  16 Oct 2021"
    assert remove_noise_lines(page) == "Some text."


def test_remove_noise_lines_keeps_numbers_in_the_middle():
    page = "Results\n95.1\n87\nMore text"
    assert "87" in remove_noise_lines(page)


def test_clean_text_produces_one_flowing_line():
    assert clean_text("first line\nsecond   line\n\nthird") == "first line second line third"


def test_remove_control_characters_drops_nul_but_keeps_line_breaks():
    assert remove_control_characters("log \x00p(y|x) \x01\nnext line") == "log p(y|x) \nnext line"
