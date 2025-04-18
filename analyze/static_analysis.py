import subprocess
import json
from pathlib import Path
import os
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def stat_analyze_diff(diff: str) -> None:
    """
    Анализирует диффы с помощью flake8 и bandit, сохраняет результаты в JSON.
    
    Args:
        diffs_data: Список словарей с информацией о PR (результат работы get_diffs)
    """
    pr_number = diff['pr_number']
    diff_path = diff['diff_path']
    
    try:
        if not os.path.exists(diff_path):
            logger.warning(f"Файл диффа {diff_path} для PR #{pr_number} не найден")
        else:  
            # Анализ с flake8
            flake8_result = run_flake8_analysis(diff_path)
            
            # Анализ с bandit
            bandit_result = run_bandit_analysis(diff_path)
            
            # Формируем результат
            analysis_result = {
                'pr_number': pr_number,
                'title': diff['title'],
                'merged_at': diff['merged_at'],
                'author': diff['author'],
                'commit_sha': diff['commit_sha'],
                'flake8_issues': flake8_result,
                'bandit_issues': bandit_result,
                'github_url': f"https://github.com/{diff.get('repo_owner', '')}/{diff.get('repo_name', '')}/pull/{pr_number}"
            }
            
            logger.info(f"Анализ PR #{pr_number} завершен: {len(flake8_result)} issues flake8, {len(bandit_result)} issues bandit")

            return analysis_result
            
    except Exception as e:
        logger.error(f"Ошибка при анализе PR #{pr_number}: {str(e)}")


def extract_added_lines(diff_path: str) -> str:
    """
    Извлекает только добавленные строки ('+') из .diff-файла.
    
    Args:
        diff_path: Путь к файлу с диффом.
    """
    added_lines = []
    with open(diff_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.startswith('+') and not line.startswith('+++'):
                added_lines.append(line[1:])  # Убираем '+' в начале
    return ''.join(added_lines)

def run_flake8_analysis(diff_path: str) -> List[Dict]:
    """
    Анализирует только добавленный код с помощью flake8.
    
    Args:
        diff_path: Путь к файлу с диффом.
    Returns:
        Список словарей с информацией об ошибках и предупреждениях flake8.
    """
    try:
        content = extract_added_lines(diff_path)
        if not content:
            return []

        result = subprocess.run(
            ['flake8', '--format=json', '--stdin-display-name', diff_path, '-'],
            input=content,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            return []
        
        try:
            # Парсим JSON вывод flake8
            issues = json.loads(result.stdout)
            return [
                {
                    'file': issue['filename'],
                    'line': issue['line_number'],
                    'column': issue['column_number'],
                    'code': issue['code'],
                    'message': issue['text'],
                    'severity': 'style'
                }
                for issue in issues
            ]
        except json.JSONDecodeError:
            logger.warning(f"Не удалось распарсить вывод flake8 для {diff_path}")
            return []
            
    except Exception as e:
        logger.error(f"Ошибка при запуске flake8 для {diff_path}: {str(e)}")
        return []

def run_bandit_analysis(diff_path: str) -> List[Dict]:
    """
    Запускает bandit для анализа безопасности кода и возвращает результаты.
    
    Args:
        diff_path: Путь к файлу с диффом.
    Returns:
        Список словарей с информацией об ошибках безопасности.
    """
    try:
        # Создаем временный файл для анализа, так как bandit не поддерживает stdin
        temp_file = Path(diff_path).with_suffix('.py')
        try:
            # Пытаемся извлечь только добавленные строки (начинающиеся с '+')
            with open(diff_path, 'r', encoding='utf-8') as f:
                added_lines = [
                    line[1:] for line in f 
                    if line.startswith('+') and not line.startswith('+++')
                ]
            
            temp_file.write_text('\n'.join(added_lines), encoding='utf-8')
            
            # Запускаем bandit с форматированием вывода в JSON
            result = subprocess.run(
                ['bandit', '-f', 'json', '-q', '-n', '1', str(temp_file)],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                return []
            
            try:
                # Парсим JSON вывод bandit
                report = json.loads(result.stdout)
                return [
                    {
                        'file': diff_path,
                        'line': issue['line_range'][0] if issue['line_range'] else 0,
                        'code': issue['test_id'],
                        'message': issue['issue_text'],
                        'severity': issue['issue_severity'],
                        'confidence': issue['issue_confidence']
                    }
                    for issue in report.get('results', [])
                ]
            except json.JSONDecodeError:
                logger.warning(f"Не удалось распарсить вывод bandit для {diff_path}")
                return []
                
        finally:
            if temp_file.exists():
                temp_file.unlink()
                
    except Exception as e:
        logger.error(f"Ошибка при запуске bandit для {diff_path}: {str(e)}")
        return []