import json

def compare_elements(elements1, elements2):
    # Initialize the result dictionary
    result = {
        "ids": [],
        "classes": [],
        "variables": [],
        "functions": []
    }

    def compare_lists(list1, list2, key):
        # Convert lists to dictionaries indexed by 'name'
        dict1 = {item['name']: item for item in list1}
        dict2 = {item['name']: item for item in list2}

        # Find keys that exist in both dictionaries
        common_keys = set(dict1.keys()).intersection(set(dict2.keys()))
        # Find keys that exist in only one dictionary
        unique_keys_1 = set(dict1.keys()) - set(dict2.keys())
        unique_keys_2 = set(dict2.keys()) - set(dict1.keys())

        # Compare elements with the same name
        for name in common_keys:
            item1 = dict1[name]
            item2 = dict2[name]
            if item1["pattern"] != item2["pattern"] or item1["account"] != item2["account"]:
                result[key].append({
                    "name": name,
                    "pattern1": item1["pattern"],
                    "pattern2": item2["pattern"],
                    "account1": item1["account"],
                    "account2": item2["account"],
                    "replace1": item1["replace"],
                    "replace2": item2["replace"],
                    "replace_pattern1": item1["replace_pattern"],
                    "replace_pattern2": item2["replace_pattern"],
                })

        # Add unique elements from list1
        for name in unique_keys_1:
            result[key].append({
                "name": name,
                "pattern1": dict1[name]["pattern"],
                "pattern2": None,
                "account1": dict1[name]["account"],
                "account2": 0,
                "replace1": dict1[name]["replace"],
                "replace2": None,
                "replace_pattern1": dict1[name]["replace_pattern"],
                "replace_pattern2": None,
            })

        # Add unique elements from list2
        for name in unique_keys_2:
            result[key].append({
                "name": name,
                "pattern1": None,
                "pattern2": dict2[name]["pattern"],
                "account1": 0,
                "account2": dict2[name]["account"],
                "replace1": None,
                "replace2": dict2[name]["replace"],
                "replace_pattern1": None,
                "replace_pattern2": dict2[name]["replace_pattern"],
            })

    # Compare each category in the elements
    compare_lists(elements1["ids"], elements2["ids"], "ids")
    compare_lists(elements1["classes"], elements2["classes"], "classes")
    compare_lists(elements1["variables"], elements2["variables"], "variables")
    compare_lists(elements1["functions"], elements2["functions"], "functions")

    return result

if __name__ == "__main__":
    main_do_path = 'C:/Users/windowadmin1.WIN-TAQQ3RO5V1L.000/Desktop/Github/ecoweb/ecoweb/test/main_do.txt'
    main_do_design_path = 'C:/Users/windowadmin1.WIN-TAQQ3RO5V1L.000/Desktop/Github/ecoweb/ecoweb/test/main_do_design.txt'

    with open(main_do_path, 'r', encoding='utf-8') as file:
        file_content_main_do = file.read()
    with open(main_do_design_path, 'r', encoding='utf-8') as file:
        file_content_main_do_design = file.read()

    # Parse the JSON strings into Python dictionaries
    elements_main_do = json.loads(file_content_main_do)
    elements_main_do_design = json.loads(file_content_main_do_design)

    print(compare_elements(file_content_main_do, file_content_main_do_design))
