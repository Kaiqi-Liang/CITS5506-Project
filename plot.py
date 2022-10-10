import pandas as pd
import seaborn as sns
import datetime
import matplotlib

matplotlib.use('AGG')
sns.set_style('darkgrid')

def plot(datetimes: list[datetime.datetime]):
	df = pd.DataFrame(datetimes, columns=['datetime'])

	# Split datetime into 2 columns of date and time
	df['date'] = df['datetime'].dt.date
	df['time'] = df['datetime'].dt.time

	# Count the number of times each hour appears
	hours = pd.DataFrame(
		[int(d.strftime('%H')) for d in df['time']] + list(range(24)),
		columns=['hour']
	).groupby(['hour']).agg(
		count=pd.NamedAgg(column='hour', aggfunc='count')
	)
	hours['count'] -= 1

	# Get the dates for the past week
	last_7_days = pd.DataFrame(
		[datetime.datetime.now() - datetime.timedelta(days=i)
			for i in range(7)
		],
		columns=['date']
	)['date'].dt.date.values.tolist()

	# Count the number of times each day appears
	days = pd.DataFrame(
		[date for date in df['date'] if date in last_7_days] + last_7_days,
		columns=['date']
	).groupby(['date']).agg(
		count=pd.NamedAgg(column='date', aggfunc='count')
	)
	days['count'] -= 1
	days = days.reset_index()

	# Sort by days and display the short name
	days['day'] = pd.Categorical(
		days['date'].astype('datetime64').dt.day_name(),
		categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
		ordered=True
	)
	days = days.sort_values('day')
	days['day'] = [day[:3] for day in days['day']]

	sns.barplot(x = hours.index, y = hours['count'])
	matplotlib.pyplot.savefig('static/hours.jpeg')

	sns.barplot(x = days['day'], y = days['count'])
	matplotlib.pyplot.savefig('static/days.jpeg')
