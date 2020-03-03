import posixpath


def get_extension(url):
    return posixpath.splitext(url)[-1].lower().lstrip(".")
