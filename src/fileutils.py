from datetime import datetime

def get_date_time_file_name():
    now = datetime.now()
    return f'{now.strftime("%m-%d-%Y_%H-%M")}.mpeg'
