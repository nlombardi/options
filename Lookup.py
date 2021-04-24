from Ichimoku import ViewData
import pickle
from PIL import Image
import os
from pick import pick

path = "\PycharmProjects\Options\output"


def get_file_list():
    # TODO: sort by the newest file
    file_list = []
    for i in os.listdir(path=os.environ["USERPROFILE"]+path):
        if i[:len(symbol)] == symbol.upper():
            file_list.append(i)

    return file_list


def load_chart(file):
    # TODO: open the file based on the input by checking the file_list
    img = pickle.load(open(os.environ["USERPROFILE"]+path+f"\{file}", "rb"))
    return Image.open(img).show()


def view_graph(symbol, period, interval, save=False):
    view = ViewData(symbol=symbol, period=period, interval=interval, save=save)
    if view:
        image = view.plot_ichimoku()
        return image
    else:
        return False


if __name__ == "__main__":
    symbol = input("Please input symbol: ")
    view, index1 = pick(['Yes', 'Hist', 'No'], 'View graph? ')
    if view.lower() != "hist":
        period, index2 = pick(['6mo', '1mo', '5d', '1d'], 'Select a time period: ')
        interval, index3 = pick(['1d', '15m', '5m', '1m'], 'Select an interval: ')
        save = False if input("Save file? (yes/no): ").upper() == "NO" else True
        image = view_graph(symbol=symbol, period=period, interval=interval, save=save)
        if not image:
            print(f"Sorry no data to view for {symbol} during the past {period} over {interval} intervals.")
        elif view.lower() == "yes":
            try:
                # If "no" for save, then ViewData will return an empty picture and will throw an exception
                Image.open(image).show()
            except Exception:
                # plot the graph instead in MPF
                pass
        else:
            pass
    else:
        title = "Please select a file to view"
        file_list = get_file_list()
        if file_list:
            file, index = pick(file_list, title)
            load_chart(file)
        else:
            print("No charts saved")
