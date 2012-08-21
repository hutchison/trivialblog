from markdown import Markdown

def markdown(value):
    md = Markdown(extensions=['subscript'])
    return md.convert(value)
