import re

regex = re.compile(r'(\d+)$')


def increment_reference(reference: str):
    previous_count = regex.findall(reference)[0]
    next_count = str(int(previous_count) + 1).zfill(len(previous_count))
    return re.sub(regex, next_count, reference)
