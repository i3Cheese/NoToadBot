from telegram_markdown import bold, escape


def test_bold_ok():
    string = "any"
    assert(bold(string) == f"**{string}**")


def test_escape_ok():
    string = "_*-\\!"
    assert(escape(string) == r"\_\*\-\\\!")

def test_escape_normal():
    string = "watafak"
    assert(escape(string) == string)
    
