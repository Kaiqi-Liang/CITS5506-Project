import pandas as pd
import datetime
import matplotlib
import seaborn

matplotlib.use('AGG')

def plot(datetimes: list[datetime.datetime]):
    df = pd.DataFrame(datetimes, columns=['date'])
    dfdate_only = df['date'].dt.date

    l7d = []
    start = 0
    for i in range(7):
        l7d.append(datetime.datetime.now() - datetime.timedelta(days=start))
        start = start + 1
    dfl7d = pd.DataFrame(l7d, columns=['date'])
    l7d_date = dfl7d["date"].dt.date

    l7d_list = l7d_date.values.tolist()
    dateonly_list = dfdate_only.values.tolist()
    l3 = [x for x in dateonly_list if x in l7d_list]
    final_list = l3 + l7d_list

    final_df = pd.DataFrame(final_list, columns=['date'])
    final_df["date"] = final_df["date"].astype("datetime64")

    final_df_grouped = final_df.groupby(["date"]).agg(
        count_col=pd.NamedAgg(column="date", aggfunc="count")
    )
    final_df_grouped['count_col'] = final_df_grouped['count_col'] - 1

    final_df_grouped = final_df_grouped.reset_index()
    final_df_grouped['date'] = final_df_grouped['date'].dt.day_name()
    final_df_grouped['count_col'] = final_df_grouped['count_col'].astype('int')

    seaborn.set_style('darkgrid')
    seaborn.barplot(final_df_grouped['date'], final_df_grouped['count_col'])
    matplotlib.pyplot.savefig('static/plot.jpeg')
