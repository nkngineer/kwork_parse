import re


# TODO: посмотреть библиотеку re
def remove_duplicates(input_file):
    with open(input_file) as input, open("output.md", "w") as output:
        input_file_lines = input.read()
        input_file_lines = re.sub(r"\d\.", "", input_file_lines)
        final_lines = "\n".join(
            f"{i}." + line
            for i, line in enumerate(set(input_file_lines.splitlines()), start=1)
        )
        output.writelines(final_lines)


def main():
    remove_duplicates("test.md")


if __name__ == "__main__":
    main()
