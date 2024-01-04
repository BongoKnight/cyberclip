"""Generate the code reference pages."""

from pathlib import Path
import mkdocs_gen_files
import sys, inspect
import re

src = Path(__file__).parent / "src"  

EXCLUDE_PATTERNS = [r"graveyard\b",r"enrich",r"private\b",r"tui\b",r"__"]

for path in sorted(src.rglob("*.py")): 
    if not (True in [True if re.search(pattern, str(path)) else False  for pattern in EXCLUDE_PATTERNS]): 
        module_path = path.relative_to(src).with_suffix("")  
        doc_path = path.relative_to(src).with_suffix(".md")
        full_doc_path = Path("docs", doc_path)

        parts = list(module_path.parts)

        if parts[-1] == "__init__":  
            parts = parts[:-1]
        elif parts[-1] == "__main__":
            continue
        identifier = ".".join(parts)
        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            try:
                print(f"""::: src.{identifier}""" , file=fd)
            except Exception as e:
                print(f"Error producing doc for {identifier} : {str(e)}" , file=fd)


        mkdocs_gen_files.set_edit_path(full_doc_path, path)  
