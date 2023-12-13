import re
import yaml

def to_instruction(origin):
    if origin == None:
        return None
    elif isinstance(origin, (list, tuple, set, dict)):
        return yaml.dump(origin, allow_unicode=True, sort_keys=False)
    else:
        return str(origin)

def to_json_desc(origin, layer_count = 0):
    if isinstance(origin, dict):
        json_string = ""
        if layer_count > 0:
            json_string += "\n"
        json_string += ("\t" * layer_count) + "{\n"
        for key, value in origin.items():
            json_string += ("\t" * (layer_count + 1)) + "\"" + key + "\": " + to_json_desc(value, layer_count + 1) + "\n"
        if layer_count > 0:
            json_string += ("\t" * (layer_count + 1)) + "},"
        else:
            json_string += "}"
        return json_string
    elif isinstance(origin, (list, set)):
        json_string = ""
        if layer_count > 0:
            json_string += "\n"
        json_string += ("\t" * layer_count) + "[\n"
        for item in origin:
            json_string += ("\t" * (layer_count + 1)) + to_json_desc(item, layer_count + 1) + ",\n"
        json_string += ("\t" * (layer_count + 1)) + "...\n"
        if layer_count > 0:
            json_string += ("\t" * layer_count) + "],"
        else:
            json_string += "]"
        return json_string
    elif isinstance(origin, tuple):
        if isinstance(origin[0], str):
            json_string = f"<{ origin[0] }>,"
        else:
            json_string = f"{ to_json_desc(value, layer_count + 1) },"
        if len(origin) >= 2:
            json_string += f"//{ origin[1] }"
        return json_string
    else:
        return str(origin)

def find_all_jsons(origin: str):
    pattern = r'"""(.*?)"""'
    origin = re.sub(
        pattern,
        lambda match: json.dumps(match.group(1)),
        origin,
        flags=re.DOTALL
    )
    origin = origin.replace("\"\"\"", "\"")
    stage = 1
    json_blocks = []
    block_num = 0
    layer = 0
    skip_next = False
    in_quote = False
    for index, char in enumerate(origin):
        if skip_next:
            skip_next = False
            continue
        if stage == 1:
            if char == "\\":
                skip_next = True
                continue
            if char == "[" or char == "{":
                json_blocks.append(char)
                stage = 2
                layer += 1
                continue
        elif stage == 2:
            if not in_quote:
                if char == "\\":
                    skip_next = True
                    continue
                if char == "\"":
                    in_quote = True
                if char == "[" or char == "{":
                    layer += 1
                elif char == "]" or char == "}":
                    layer -= 1
                elif char in ("\t", " ", "\n"):
                    char = ""
                json_blocks[block_num] += char
            else:
                if char == "\n":
                    char = "\\n"
                elif char == "\t":
                    char = "\\t"
                elif char == "\"":
                    in_quote = not in_quote
                json_blocks[block_num] += char
            if layer == 0:
                block_num += 1
                stage = 1
    return json_blocks

def find_json(origin: str):
    result = find_all_jsons(origin)
    if len(result) > 0:
        return result[0]
    else:
        return None