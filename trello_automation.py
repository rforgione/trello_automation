from trello import TrelloClient, Board, List
from sys import argv
import os
import datetime
import pytz

client = TrelloClient(os.environ["TRELLO_API_KEY"],
                      os.environ["TRELLO_API_SECRET"],
                      os.environ["TRELLO_OAUTH_TOKEN"],
                      os.environ["TRELLO_OAUTH_TOKEN_SECRET"])


gtd_board = Board(client,board_id='56aef9b21bf0d91a358e8dad')

def get_list_with_name(board=None, name=None):
    # this breaks if there's more than one list with the same name
    # which probably shouldn't happen anyway.
    return [i for i in board.open_lists() if i.name==name][0]

def copy_all_cards(board, first_list_name, second_list_name):
    for i in get_list_with_name(board, first_list_name).list_cards():
        get_list_with_name(board, second_list_name).\
            add_card(name=i.name,
                     due=i.due_date.astimezone(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S'),
                     labels=i.list_labels,
                     source=i.id)

def update_all_due(board, listname, time_delta_hours=24):
    for i in get_list_with_name(board, listname).list_cards():
        i.set_due(i.due_date + datetime.timedelta(hours=time_delta_hours))

def refresh_recurring(board, recurring_list, actual_list, time_delta_hours=24):
    update_all_due(board, recurring_list, time_delta_hours)
    copy_all_cards(board, recurring_list, actual_list)

def clear_out_old_recurring(board, listname):
    for i in get_list_with_name(board, listname).list_cards():
        if "#recurring" in [j.name for j in i.list_labels]:
            i.set_closed(True)

def execute_update(board, recurring_list, actual_list, date_update):
    clear_out_old_recurring(board, actual_list)
    refresh_recurring(board, recurring_list, actual_list, time_delta_hours=date_update)

def update(update_type):
    if update_type == "daily":
        execute_update(gtd_board, "Daily Recurring", "Today", 24)
    elif update_type == "weekly":
        execute_update(gtd_board, "Weekly Recurring", "This Week", 168)
    elif update_type == "full":
        execute_update(gtd_board, "Daily Recurring", "Today", 24)

        if datetime.datetime.today().weekday() == 6:
            execute_update(gtd_board, "Weekly Recurring", "This Week", 168)

if __name__ == "__main__":

    if len(argv) == 1:
        update_type = "full"
    else:
        update_type = argv[1]

    update(update_type)

