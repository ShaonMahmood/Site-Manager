#!/usr/bin/python3

import os

def main_function():
    file_name = input("Enter file name: ")
    try:
        line_number = int(input("Enter line number(where to insert): "))
    except ValueError as err:
        print(err)
        line_number = None
    new_inserted_data = input("Type what to insert: ")
    if not line_number and not file_name:
        print("sorry, missing data!!, re-run the script")
        return

    exclude_folders = {"site_template_structure", "snippets"}  # enter excluded folder name here

    # save excluded folder name as directory
    exclude_folders_path = []
    print("SubDir")
    for subDir in [os.path.join(os.getcwd(), excf) for excf in exclude_folders]:
        for d, s, f in os.walk(subDir):
            exclude_folders_path.append(d)

    for dir_path, sub_dirs, file in os.walk(os.getcwd()):
        if dir_path in exclude_folders_path:
            continue  # no need to check excluded folders
        for x in file:
            if x != file_name:
                continue
            file_path = (os.path.join(dir_path, x))
            try:
                lines = []
                with open(file_path, 'r') as f:
                    lines = f.readlines()

                with open(file_path, 'w') as b:
                    for i, line in enumerate(lines):
                        if new_inserted_data and i == line_number:
                            print("linenumber")
                            b.write('\n' + new_inserted_data)
                        b.write(line)
            except Exception as err:
                print('sorry can\'t write in files: {0}'.format(err))


if __name__ == "__main__":
    main_function()
