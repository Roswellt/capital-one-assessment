import argparse
import os


MULTILINE_COMMENT_CHARS = {
    "/*": "*/",   # Java / Typescript
    "/**": "*/",  # JavaDocs
    "#": "#",     # Python
}
BLOCK_LINE_CHARS = {
    "/*": "*",      # Java / Typescript
    "#": "#",       # Python
}
SINGLE_LINE_COMMENT_CHARS = [
    "//",    # Java / Typescript
    "#",     # Python
]
TODO_CHARS = [
    "//TODO",
    "// TODO",
    "# TODO",
    "#TODO",
]


class CommentCount:
    LINES = 0
    COMMENTS = 0
    SINGLE_LINE_COMMENTS = 0
    COMMENT_LINES_IN_BLOCK = 0
    BLOCK_COMMENTS = 0
    TODOS = 0

    # Keeps track of current line
    CURRENT_LINE = None

    def parse_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                self.CURRENT_LINE = file.readline()
                while self.CURRENT_LINE:
                    self.LINES += 1

                    # See if line is a todo first
                    self.check_for_todos(file)
                    self.check_for_block_comment(file)
                    self.check_for_single_comment(file)
                    self.CURRENT_LINE = file.readline()

                self.print_comment_info()
        except OSError as ex:
            print('Error {}'.format(ex))

    def check_for_todos(self, file):
        for todo_pattern in TODO_CHARS:
            if todo_pattern in self.CURRENT_LINE:
                self.TODOS += 1

    def check_for_single_comment(self, file):
        for single_line_pattern in SINGLE_LINE_COMMENT_CHARS:
            if single_line_pattern in self.CURRENT_LINE:
                self.COMMENTS += 1
                self.SINGLE_LINE_COMMENTS += 1

    def check_for_block_comment(self, file):
        for block_pattern in MULTILINE_COMMENT_CHARS.keys():
            if block_pattern in self.CURRENT_LINE:
                inline_count = 0
                # Continue until closing multiline is found
                while(self.CURRENT_LINE):

                    self.CURRENT_LINE = self.CURRENT_LINE.strip()

                    # Check if current line is a comment in block
                    if BLOCK_LINE_CHARS[block_pattern] in self.CURRENT_LINE:
                        self.COMMENTS += 1

                        # Case where block opening block comment is the same as closing block comment
                        # don't add to inline_count when comment is inline
                        if (MULTILINE_COMMENT_CHARS[block_pattern] != block_pattern or
                                self.CURRENT_LINE[0] == BLOCK_LINE_CHARS[block_pattern]):
                            inline_count += 1

                    # Check if block line has ended
                    if MULTILINE_COMMENT_CHARS[block_pattern] in self.CURRENT_LINE and block_pattern != '#':
                        self.BLOCK_COMMENTS += 1
                        self.COMMENT_LINES_IN_BLOCK += inline_count
                        return

                    # If opening block is the same as closing block, add block comment count if inline > 1
                    elif (block_pattern == MULTILINE_COMMENT_CHARS[block_pattern] and block_pattern not in self.CURRENT_LINE):
                        if inline_count > 1:
                            self.BLOCK_COMMENTS += 1
                            self.COMMENT_LINES_IN_BLOCK += inline_count
                        else:
                            self.SINGLE_LINE_COMMENTS += 1
                        return
                    self.CURRENT_LINE = file.readline()

                    if self.CURRENT_LINE:
                        self.LINES += 1

    def print_comment_info(self):
        print('Total # of lines: {}'.format(self.LINES))
        print('Total # of comment lines: {}'.format(self.COMMENTS))
        print('Total # of single line comments: {}'.format(
            self.SINGLE_LINE_COMMENTS))
        print('Total # of comment lines within block comments: {}'.format(
            self.COMMENT_LINES_IN_BLOCK))
        print('Total # of block line comments: {}'.format(self.BLOCK_COMMENTS))
        print('Total # of TODO\'s: {}'.format(self.TODOS))


def validate_arg(file_path):
    if not os.path.isfile(file_path):
        print('File does not exist at path {}'.format(file_path))
        return False
    if len(file_path.split('.')) < 2:
        print('File needs an extension, ignoring {}'.format(file_path))
        return False
    if file_path[0] == '.':
        print("File name starts with a '.', ignoring {}".format(file_path))
        return False
    return True


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Takes in a file path and returns comment information')
    parser.add_argument('input', metavar='file_name', type=str,
                        help='The file path to parse for comments')
    args = parser.parse_args()
    if validate_arg(args.input):
        comment_count = CommentCount()
        comment_count.parse_file(args.input)


if __name__ == "__main__":
    main()
