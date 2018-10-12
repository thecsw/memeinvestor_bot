import datetime

def investment_duration_string(duration):
    hours = duration // 3600
    duration %= 3600
    minutes = duration // 60
    duration %= 60

    inv_string = ""
    if (hours):
        inv_string += f"{hours} hour"
        if (hours > 1):
            inv_string += "s "
        inv_string += " "
    if (minutes):
        inv_string += f"{minutes} minute"
        if (minutes > 1):
            inv_string += "s "
        inv_string += " "
    if (duration):
        inv_string += f"{duration} second"
        if (duration > 1):
            inv_string += "s "
        inv_string += " "

    return inv_string

def upvote_string():
    return {
        10:"upd00ts",
    }.get(datetime.date.today().month, "upvotes")
