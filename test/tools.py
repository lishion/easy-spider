from os import path


def get_test_page(*dir_path):
    filepath = path.dirname(path.abspath(__file__))
    with open(path.join(filepath, *dir_path), 'r', encoding='utf-8') as fd:
        page = fd.read()
    return page


test_page = get_test_page("test_server", "test_page.html")
