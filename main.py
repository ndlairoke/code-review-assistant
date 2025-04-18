from download_repo import get_diffs
import os
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Пример использования
    try:
        diffs = get_diffs(
            github_url="https://github.com/natasha/natasha",
            email="122558239+the-lenoz@users.noreply.github.com",
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 4, 17, tzinfo=timezone.utc),
            # токен гитхаба из переменных окружения
            access_token=os.getenv("GITHUB_TOKEN"),
            output_dir="diffs"
        )
        for diff in diffs:
            logger.info(f"PR #{diff['pr_number']}: {diff['title']} (Diff saved to {diff['diff_path']})")
        logger.info(f"Найдено {len(diffs)} PR")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")

#             email="avasilev1992@gmail.com",
#             repo_url="https://github.com/AlfaInsurance/devQ_testData_PythonProject.git",