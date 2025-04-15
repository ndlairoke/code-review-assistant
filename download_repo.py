import os
import subprocess
import shutil
def download_repo(url: str, author: str, start_date: str, end_date: str, save_path: str) -> None:
    """This function clones repo and finds files commited during a certain period of time with a certain author
        
        url: the url of the repo
        author: the author of the files
        start_date: the start date of the period
        end_date: the end date of the period
        save_path: the path to save the files
    """
    repo_name = url.split("/")[-1].replace(".git", "")
    repo_path = os.path.abspath(repo_name)
    save_path = os.path.abspath(save_path)

    # клонируем репу если ее нет
    if not os.path.exists(repo_path):
        subprocess.run(["git", "clone", url])

    # находим файлы с автором и датами
    os.chdir(repo_path)
    log = ["git", "log",
        f'--author={author}',
        f'--since={start_date}',
        f'--until={end_date}',
        "--pretty=format:%H"
        ]
    
    result = subprocess.run(log, stdout=subprocess.PIPE, text=True)
    # print(result)
    commits = result.stdout.strip().split("\n")
    # print(commits)

    print(f"Found {len(commits)} commits by {author} from {start_date} to {end_date}")

    for commit in commits:
        changed = ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit]
        result = subprocess.run(changed, stdout=subprocess.PIPE, text=True)
        files = result.stdout.strip().split("\n")
        print(f"{commit}: {files}")

        for file in files:
            # копируем файлы с сохранением структуры папок
            # обязательно вне репы!
            if not file or not os.path.exists(file):
                continue

            src_path = os.path.abspath(file)
            dst_path = os.path.join(save_path, file)

            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
    
    print(f'Successfully copied the files to {save_path}')

    # камбек в исходную папку
    os.chdir("..")
        

# пример: добываем файлы из репы модуля "requests" от anupam-arista с 1 февраля по 1 марта 2025
# 4 коммита: 1 мердж и 3 файла с изменением файла models.py
download_repo(
    "https://github.com/psf/requests.git",
    "anupam-arista",
    "2025-02-01",
    "2025-03-01",
    "./requests_author_changes"
)


