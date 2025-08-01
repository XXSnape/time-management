def generate_hours(start_hour: int, end_hour: int):
    return [
        (str(h).zfill(2), h) for h in range(start_hour, end_hour)
    ]
