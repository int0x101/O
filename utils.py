import re


def pre(input):
    dedent_pattern = r"(?<=\n)(\S)"
    dedent_replacer = r"\1\1"

    results = re.sub(dedent_pattern, dedent_replacer, input)
    return results + "\n"
