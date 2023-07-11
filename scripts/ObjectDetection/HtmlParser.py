from html import escape
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.__t = 0
        self.lines = []
        self.__current_line = ''
        self.__current_tag = ''

    @staticmethod
    def __attr_str(attrs):
        return ' '.join('{}="{}"'.format(name, escape(value)) for (name, value) in attrs)

    def handle_starttag(self, tag, attrs):
        if tag != self.__current_tag:
            self.lines += [self.__current_line]

        self.__current_line = '\t' * self.__t + '<{}>'.format(tag + (' ' + self.__attr_str(attrs) if attrs else ''))
        self.__current_tag = tag
        self.__t += 1

    def handle_endtag(self, tag):
        self.__t -= 1
        if tag != self.__current_tag:
            self.lines += [self.__current_line]
            self.lines += ['\t' * self.__t + '</{}>'.format(tag)]
        else:
            self.lines += [self.__current_line + '</{}>'.format(tag)]

        self.__current_line = ''

    def handle_data(self, data):
        self.__current_line += data

    def get_parsed_string(self):
        return ''.join(l for l in self.lines if l)
