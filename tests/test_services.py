from umakaparser.services import init_i18n


def test_init_18n():
    result = init_i18n()
    assert result is None
