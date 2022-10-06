import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    cur_date = datetime.datetime.now()
    return {
        'year': cur_date.year,
    }
