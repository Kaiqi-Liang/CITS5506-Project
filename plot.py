import pandas as pd
import datetime
import calendar
from collections import Counter

def plot(dtlist):
    datetime.datetime.now()

    dateonly = []

    for i in dtlist:
        dateonly.append(i.date())

    df = pd.DataFrame (dtlist, columns = ['date'])

    dfdate_only = df["date"].dt.date
    df.groupby(df["date"].dt.date).count()

    #day of week
    print(calendar.day_name[datetime.datetime.now().weekday()])

    print(datetime.datetime.now() - datetime.timedelta(days=9))
    l7d = []
    start = 0
    for i in range(7):
        l7d.append(datetime.datetime.now() - datetime.timedelta(days=start))
        start = start + 1


    dfl7d = pd.DataFrame (l7d, columns = ['date'])

    l7d_date = dfl7d["date"].dt.date
    l7d_date

    l7d_list = l7d_date.values.tolist()

    dateonly_list = dfdate_only.values.tolist()

    Counter(zip(l7d_list, dateonly_list))

    l3 = [x for x in dateonly_list if x in l7d_list]




    final_list = l3 + l7d_list




    final_list




    final_df = pd.DataFrame(final_list, columns=['date'])




    final_df["date"] = final_df["date"].astype("datetime64")


    plot = (final_df.groupby(final_df["date"].dt.day).count()-1).plot(kind="bar")
    fig = plot.get_figure()
    fig.savefig("output.png")