def get_root_from_url(url: str) -> str:
    """
    Get root domain from URL

    @param url: URL to extract root domain from
    @return: Root domain of URL
    """
    import re
    regex = r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)"
    return re.findall(regex, url)[0]