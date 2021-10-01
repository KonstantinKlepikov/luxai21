from logging import getLogger, INFO, FileHandler,  Formatter,  StreamHandler


def init_logger(log_file='run.log'):
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    handler1 = StreamHandler()
    handler1.setFormatter(Formatter("%(message)s"))
    handler2 = FileHandler(filename=log_file, mode='w')
    handler2.setFormatter(Formatter("%(message)s"))
    logger.addHandler(handler1)
    logger.addHandler(handler2)
    return logger


def get_times_of_days() -> dict:
    
    day_list = list(range(0, 30))
    night_list = list(range(310, 360))
    mult = [0, 80, 160, 240]
    
    for i in list(range(70, 110)):
        day_list.extend([num + i for num in mult])
            
    for i in list(range(30, 70)):
        night_list.extend([num + i for num in mult])

    return {'day_list': day_list, 'night_list': night_list}