import md5, settings

# Truncates a string and adds ... if it exceeds a specified limit
# @param input original string
# @param limit max length that the string can be
# @return string within specified char limit
def limit(input, limit):
    if input is None or input == "":
        return input
    if len(input) > limit:
        return input[:limit] + "..."
    return input

def create_hash(input, salt=None):
    if not salt:
        return md5.new(input).digest()
    return md5.new(input + salt).digest()

