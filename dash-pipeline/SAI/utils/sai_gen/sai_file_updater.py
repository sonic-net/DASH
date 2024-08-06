import os
from typing import List


class SAIFileUpdater:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def __enter__(self):
        with open(self.file_path, "r") as f:
            self.lines = f.readlines()
        return self

    def __exit__(self, *args):
        print("Updating file: " + self.file_path + " ...")
        SAIFileUpdater.write_if_different(self.file_path, "".join(self.lines))

    def insert_before(
        self, target_line: str, insert_lines: List[str], new_line_only: bool = False
    ) -> None:
        new_lines: List[str] = []

        existing_lines = set([l.strip() for l in self.lines])
        for line in self.lines:
            if target_line in line:
                if new_line_only:
                    for insert_line in insert_lines:
                        if insert_line.strip() not in existing_lines:
                            new_lines.append(insert_line + "\n")
                else:
                    new_lines.extend(
                        [insert_line + "\n" for insert_line in insert_lines]
                    )

            new_lines.append(line)

        self.lines = new_lines

    def insert_after(
        self, target_line: str, insert_lines: List[str], new_line_only: bool = False
    ) -> None:
        new_lines: List[str] = []

        existing_lines = set([l.strip() for l in self.lines])
        for line in self.lines:
            new_lines.append(line)
            if target_line in line:
                if new_line_only == True:
                    for insert_line in insert_lines:
                        if insert_line.strip() not in existing_lines:
                            new_lines.append(insert_line + "\n")
                else:
                    new_lines.extend(
                        [insert_line + "\n" for insert_line in insert_lines]
                    )

        self.lines = new_lines

    # don't write content to file if file already exists
    # and the content is the same, this will not touch
    # the file and let make utilize this
    @staticmethod
    def write_if_different(file: str, content: str) -> None:
        if os.path.isfile(file) == True:
            o = open(file, "r")
            data = o.read()
            o.close()
            if data == content:
                return  # nothing to change, file is up to date
        with open(file, "w") as o:
            o.write(content)
