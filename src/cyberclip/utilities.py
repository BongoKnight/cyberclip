import re
import uuid

def clean_tsv(new_text: str, text:str):
    """If new_text is a TSV value that starts with text as a first field, returns everythings except this field

    Code exemple ::
    clean_tsv("a\tbaba", "a")
    >>> "baba"
    clean_tsv("b\tbaba", "a")
    >>> "b\tbaba"
    """
    result = new_text
    if new_text.startswith(f"{text}\t"):
        result = re.sub("^"+re.escape(text)+"\t", "", new_text)
    return result


def get_rectangle_text(text: str, max_width: int, max_height:int):
    clean_text = ""
    lines = text.splitlines()
    nb_lines = len(lines)
    clean_text = "\n".join([line[0:min(len(line), max_width)] for line in lines[0:min(nb_lines,max_height)]])
    return clean_text

# def add_node(graph: nx.DiGraph, node: dict, type: str = "text", previous_node: dict = {}) -> dict:
#     new_id = str(uuid.uuid4())
#     if type == "text":
#         for id, _node in graph.nodes.items():
#             if _node.get("text") == node.get("text"):
#                 return _node
#         label = get_rectangle_text(node.get("text"), 25, 15)
#         node.update({"id":new_id, "type":type, "label":label})
#         graph.add_node(new_id, **node)
#     else:
#         if edges:=graph.out_edges(previous_node.get("id")):
#             for source, target in edges:
#                 if type == "parser" and graph.nodes.get(target).get("label") == node.get("label",""):
#                     return graph.nodes.get(target)
#                 if type == "action" and graph.nodes.get(target).get("label") == node.get("label",""):
#                     return graph.nodes.get(target)
#         node.update({"id":new_id, "type":type})
#         graph.add_node(new_id, **node)
#     return node

