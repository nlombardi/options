import yfinance as yf
import matplotlib.pyplot as plt

# pull data for a symbol
SPY = yf.download('SPY')
SPY.head()

# pull more detailed ticker data
SPY50 = yf.Ticker('SPY')
SPY50_hist = SPY50.history(start="2020-05-01", end="2021-01-30")

# pull info
SPY50.info
SPY50.info['fiftyDayAverage']
SPY50.info['averageDailyVolume10Day']


def plotData(p1, p2='', p3='', p4='', days=10):
    # pull multiple symbols and plot against
    data = yf.download(f'{p1} {p2} {p3} {p4}')
    # data['Close'].tail(10).plot(figsize=(10,5))
    fig, ax = plt.subplots()
    # first line
    p1 = ax.plot(data.tail(10).index, data['Close'][p1].tail(10), color='red', marker='o', label=p1)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_xticklabels(ax.get_xticks(), rotation=90, fontsize=8)
    ax.set_ylabel('Close Price', fontsize=12)
    # second line
    if p2 != '':
        ax2 = ax.twinx()
        p2 = ax2.plot(data.tail(10).index, data['Close'][p2].tail(10), color='green', marker='o', label=p2)
    # format graph
    lns = p1 + p2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0)
    ax.grid()
    # show / save graph
    plt.show()
    # fig.savefig(path+f'{p1}_{p2}_last{days}days.jpg', format='jpeg', dpi=300, bbox_inches='tight')
