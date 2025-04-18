from github import Github, GithubException
from datetime import datetime, timezone
import re
from typing import List, Dict, Optional
import logging
import os
from pathlib import Path
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_github_url(url: str) -> tuple[str, str]:
    """
    Извлекает владельца и название репозитория из URL GitHub.
    
    Args:
        url (str): URL GitHub репозитория.

    Returns:
        tuple[str, str]: Кортеж, содержащий владельца и название репозитория.
    """

    pattern = r'https?://github\.com/([^/]+)/([^/]+)'
    match = re.match(pattern, url)
    if not match:
        raise ValueError("Некорректный URL репозитория GitHub")
    return match.groups()

def save_diff_to_file(diff_content: str, pr_number: int, output_dir: str) -> str:
    """
    Сохраняет дифф в файл и возвращает путь к файлу.
    
    Args:
        diff_content (str): Содержимое диффа.
        pr_number (int): Номер PR.
        output_dir (str): Путь к директории для сохранения файлов.

    Returns:
        str: Путь к сохраненному файлу.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(output_dir, f"pr_{pr_number}_diff.diff")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(diff_content)
    return file_path

def get_diffs(
    github_url: str,
    email: str,
    start_date: datetime,
    end_date: datetime,
    access_token: Optional[str] = None,
    output_dir: str = "diffs"
) -> List[Dict]:
    """
    Получает диффы для merge requests, проверяя email в коммитах.
    Сохраняет изменения коммитов только указанного автора.

    Args:
        github_url (str): URL GitHub репозитория.
        email (str): Email для фильтрации коммитов.
        start_date (datetime): Начальная дата.
        end_date (datetime): Конечная дата.
        access_token (Optional[str]): Токен доступа к GitHub API.
        output_dir (str): Путь к директории для сохранения файлов.

    Returns:
        List[Dict]: Список словарей, содержащих информацию о PR и пути к файлам с изменениями.
    """
    try:
        # Инициализация клиента GitHub
        g = Github(access_token) if access_token else Github()
        
        # Проверка валидности токена
        if access_token:
            try:
                g.get_user().login
            except GithubException as e:
                logger.error("Недействительный токен доступа")
                raise ValueError("Недействительный токен доступа")

        owner, repo_name = parse_github_url(github_url)
        repo = g.get_repo(f"{owner}/{repo_name}")
        
        result = []
        processed_prs = 0
        found_prs = 0
        
        # Получаем все закрытые PR
        pulls = repo.get_pulls(state='closed', sort='updated', direction='desc')
        
        for pr in pulls:
            processed_prs += 1
            logger.info(f"Проверяем PR #{pr.number} (обработано {processed_prs} PR)")
            
            # Пропускаем, если PR не был мерджен или вне диапазона дат
            if not pr.merged_at:
                continue
            if not (start_date <= pr.merged_at <= end_date):
                continue

            # Получаем ВСЕ коммиты PR и фильтруем по email
            try:
                all_commits = list(pr.get_commits())
                author_commits = [
                    commit for commit in all_commits
                    if commit.commit.author and commit.commit.author.email == email
                ]
                
                # Пропускаем PR, если нет коммитов автора
                if not author_commits:
                    continue

                # Собираем diff ТОЛЬКО из коммитов автора
                diff_content = ""
                for commit in author_commits:
                    # Получаем файлы для каждого коммита (через API)
                    commit_details = repo.get_commit(commit.sha)
                    for file in commit_details.files:
                        diff_content += f"diff --git a/{file.filename} b/{file.filename}\n"
                        if file.patch:
                            diff_content += file.patch + "\n\n"
                
                if not diff_content:
                    logger.warning(f"PR #{pr.number} не содержит изменений автора {email}")
                    continue
                
                # Сохраняем diff в файл
                diff_path = save_diff_to_file(diff_content, pr.number, output_dir)
                
                result.append({
                    'pr_number': pr.number,
                    'title': pr.title,
                    'merged_at': pr.merged_at.isoformat(),
                    'author': pr.user.login,
                    'diff_path': diff_path,
                    'commit_sha': pr.merge_commit_sha,
                    'author_commits_count': len(author_commits)  # Добавим количество релевантных коммитов
                })
                found_prs += 1
                logger.info(f"Найден подходящий PR #{pr.number} с {len(author_commits)} коммитами автора")
            
            except GithubException as e:
                logger.warning(f"Не удалось обработать PR #{pr.number}: {str(e)}")
                continue
        
        logger.info(f"Обработано {processed_prs} PR, найдено {found_prs} подходящих PR")
        return result
    
    except GithubException as e:
        if e.status == 403:
            logger.error("Нет доступа к репозиторию. Проверьте токен.")
        elif e.status == 404:
            logger.error("Репозиторий не найден или приватный.")
        else:
            logger.error(f"GitHub API Error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        raise