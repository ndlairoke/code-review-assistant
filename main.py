import logging
from form_report import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        result = form_report(github_url="https://github.com/natasha/natasha",
            email="122558239+the-lenoz@users.noreply.github.com",
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 4, 17, tzinfo=timezone.utc),
            # токен гитхаба из переменных окружения
            access_token=os.getenv("GITHUB_TOKEN"))
    except Exception as e:
        result = 'Please, try again!'
    print(result)
