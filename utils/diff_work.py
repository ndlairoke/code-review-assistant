from unidiff import PatchSet
from pathlib import Path

def parse_diff_to_code_files(diff_path: str, output_dir: str) -> None:
    """This function parses diff to code files
        diff: diff to parse
        Returns: dict with file name and code
    """
    patch = PatchSet.from_filename(diff_path)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for patched_file in patch:
        new_file_path = Path(output_dir) / patched_file.path
        new_file_path.parent.mkdir(parents=True, exist_ok=True)

        new_lines = []
        for hunk in patched_file:
            for line in hunk:
                if line.is_added or line.is_context:
                    new_lines.append(line.value)

        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        print(f"Файл восстановлен: {new_file_path}")