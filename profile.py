
import pandas as pd
import simplejson as json
import openpyxl
import requests
import os
from datetime import datetime, timedelta

#import date from dateime 


class Profile(object):
    def __init__(self, excel_file):

        self.excel_profile_data = None
        self.excel_videos_data = None
        self.parse_excel(excel_file)
        self.clean_excel_videos_data()

        self.profile_details = {}
        self.get_profile_details()
        self.scrape_additional_profile_details()

        self.totals = None
        self.get_totals()

        self.averages = None
        self.get_averages()

        self.top_videos = None
        self.get_top_videos()

        self.video_duration_data = None
        self.get_video_duration_data()

        self.hashtags_data = None
        self.get_hashtags_data()

        self.views_timeseries = None
        self.get_views_timeseries()

        self.likes_timeseries = None
        self.get_likes_timeseries()

        self.comments_timeseries = None
        self.get_comments_timeseries()

        self.shares_timeseries = None
        self.get_shares_timeseries()

        self.videos_timeseries = None
        self.get_videos_timeseries()

        self.videos_timeseries_by_week = None
        self.split_videos_timeseries_into_weeks()

        self.data = None
        self.save_as_json()

    def parse_excel(self, excel_file):
        excel_videos_data = pd.read_excel(
            excel_file, sheet_name='Profile Breakdown', header=5, usecols="B:L", skipfooter=1)
        excel_profile_data = pd.read_excel(
            excel_file, sheet_name='Profile Breakdown', header=2, usecols="B:J", nrows=2)
        excel_videos_data = pd.DataFrame(excel_videos_data)
        excel_profile_data = pd.DataFrame(excel_profile_data)

        #loop through excel_profile_data and remove any items that has a value NaN
        for index, row in excel_profile_data.iterrows():
            for key, value in row.items():
                if pd.isna(value):
                    del row[key]
        

        #loop through excel_videos_data (a list) and remove any items that has a value NaN
        for index, row in excel_videos_data.iterrows():
            for key, value in row.items():
                if pd.isna(value):
                    del row[key]


        self.excel_videos_data = excel_videos_data
        self.excel_profile_data = excel_profile_data

    def get_profile_details(self):
        excel_profile_data_dict = self.excel_profile_data.to_dict(orient='records')[0]

        self.profile_details['bio'] = excel_profile_data_dict['Bio']
        self.profile_details['likes'] = excel_profile_data_dict[' Profile Likes']
        self.profile_details['followers'] = excel_profile_data_dict['Followers']
        self.profile_details['followers'] = excel_profile_data_dict['Followers']
        self.profile_details['link_in_bio'] = excel_profile_data_dict['Link in Bio']
        self.profile_details['profile_link'] = excel_profile_data_dict['Profile Link']
        username = excel_profile_data_dict['Username:']
        username = username[1:]
        if username[-1] == '✅':
            username = username[:-1]
        self.profile_details['username'] = username

    def scrape_additional_profile_details(self):

       
        username = self.profile_details['username']
        print('sending request to get pic and following count of username : ' + username)
        try:
            response = requests.post(
                'https://tokscraper.com/api/user/id', json={'username': username})
            print(response.json())

            self.profile_details['following'] = response.json()['following']
             #send a request and download response.picUrl (jpeg photo link) to static folder profiles-pics

            url = response.json()['picUrl']

            file_path = os.path.join('profiles-photos', username+'.jpg')

            response = requests.get(url)

            with open(file_path, 'wb') as f:
                f.write(response.content)
        except Exception as e:
            print(e.message)
            print('failed to get profile pic and following count')
            return
        
    def clean_excel_videos_data(self):
        #self.excel_videos_data.columns = excel_videos_data.columns.str.replace(r"[^a-zA-Z]+","", regex=True)
        # from excel videos data columns, remove any character that's not a letter or a space
        self.excel_videos_data.columns = self.excel_videos_data.columns.str.replace(
            r"[^a-zA-Z ]+", "", regex=True).str.strip()

        self.excel_videos_data['Views'] = self.excel_videos_data['Views'].str.replace(
            ',', '').astype(float)
        self.excel_videos_data['Likes'] = self.excel_videos_data['Likes'].str.replace(
            ',', '').astype(float)
        self.excel_videos_data['Comments'] = self.excel_videos_data['Comments'].str.replace(
            ',', '').astype(float)
        self.excel_videos_data['Shares'] = self.excel_videos_data['Shares'].str.replace(
            ',', '').astype(float)

    def get_totals(self):
        # get total videos, turn from string to int, and sum all the values
        total_views = self.excel_videos_data['Views'].sum()
        total_likes = self.excel_videos_data['Likes'].sum()
        total_comments = self.excel_videos_data['Comments'].sum()
        total_shares = self.excel_videos_data['Shares'].sum()
        total_duration = self.excel_videos_data['Duration'].sum()

        # total videos is the number of rows excluding the header
        total_videos = len(self.excel_videos_data.index) - 1

        # create a dictionary with the totals
        self.totals = {
            'total_views': int(total_views),
            'total_likes': int(total_likes),
            'total_comments': int(total_comments),
            'total_shares': int(total_shares),
            'total_videos': int(total_videos),
            'total_duration': int(total_duration)
        }

        return self.totals

    def get_averages(self):
        # get averages of views, likes, comments, shares, and duration
        average_views = (self.totals['total_views'] /
                         self.totals['total_videos'])
        average_likes = (self.totals['total_likes'] /
                         self.totals['total_videos'])
        average_comments = (
            self.totals['total_comments'] / self.totals['total_videos'])
        average_shares = (
            self.totals['total_shares'] / self.totals['total_videos'])
        average_duration = (
            self.totals['total_duration'] / self.totals['total_videos'])

        # create a dictionary with the averages
        self.averages = {
            'average_views': int(average_views),
            'average_likes': int(average_likes),
            'average_comments': int(average_comments),
            'average_shares': int(average_shares),
            'average_duration': int(average_duration)
        }

        return self.averages

    def get_top_videos(self):
        # get top videos in views, sowe have a list with dicionaries of the top 5 videos
        top_views_videos = self.excel_videos_data.nlargest(5, 'Views')
        top_views = top_views_videos.to_dict(orient='records')

        top_likes_videos = self.excel_videos_data.nlargest(5, 'Likes')
        top_likes = top_likes_videos.to_dict(orient='records')

        top_comments_videos = self.excel_videos_data.nlargest(5, 'Comments')
        top_comments = top_comments_videos.to_dict(orient='records')

        top_shares_videos = self.excel_videos_data.nlargest(5, 'Shares')
        top_shares = top_shares_videos.to_dict(orient='records')

        # create a dictionary with the top videos

        self.top_videos = {
            'top_views': top_views,
            'top_likes': top_likes,
            'top_comments': top_comments,
            'top_shares': top_shares
        }

        return self.top_videos

    def get_video_duration_data(self):
        # percentages og videos with duration 0-15secs and 15-30secs and 30secs -1min and 1min-3mins and 3-10mins (duration in seconds)
        duration_0_15 = 0
        duration_15_30 = 0
        duration_30_60 = 0
        duration_60_180 = 0
        duration_180_600 = 0

        total_videos = self.totals['total_videos']
        # loop through all the rows in the excel file
        for index, row in self.excel_videos_data.iterrows():
            # if duration is 0-15secs
            if row['Duration'] >= 0 and row['Duration'] <= 15:
                duration_0_15 += 1
            # if duration is 15-30secs
            elif row['Duration'] > 15 and row['Duration'] <= 30:
                duration_15_30 += 1
            # if duration is 30secs -1min
            elif row['Duration'] > 30 and row['Duration'] <= 60:
                duration_30_60 += 1
            # if duration is 1min-3mins
            elif row['Duration'] > 60 and row['Duration'] <= 180:
                duration_60_180 += 1
            # if duration is 3-10mins
            elif row['Duration'] > 180 and row['Duration'] <= 600:
                duration_180_600 += 1

        # create a dictionary with the duration data in percentages
        self.video_duration_data = {
            'duration_0_15': (duration_0_15 / total_videos) * 100,
            'duration_15_30': (duration_15_30 / total_videos) * 100,
            'duration_30_60': (duration_30_60 / total_videos) * 100,
            'duration_60_180': (duration_60_180 / total_videos) * 100,
            'duration_180_600': (duration_180_600 / total_videos) * 100
        }

        return self.video_duration_data

    def get_hashtags_data(self):
        frequently_used_hashtags = self.excel_profile_data['Frequently Used Hashtags'][0].split(
            ', ')
        # turn to a string, then split by comma and turn to list
        # it's a string in this format icecream[448],  satisfying[224],  cake[160] so turn it to a list of dictionaries of key hashtag name and value number of times used
        hashtags_list = []
        for hashtag in frequently_used_hashtags:
            if ('[' not in hashtag):
                continue
            count = hashtag.split('[')[1].split(']')[0]
            if (int(count) < 2):
                continue
            item = {
                'hashtag': hashtag.split('[')[0].strip(),
                'count': hashtag.split('[')[1].split(']')[0]
            }
            hashtags_list.append(item)

        # if len(hashtags_list) if bigger than 100, then take the top 100
        if (len(hashtags_list) > 100):
            hashtags_list = hashtags_list[:100]

        self.hashtags_data = hashtags_list
        return self.hashtags_data

    def get_views_timeseries(self):
        # get the views time series
        views_timeseries = self.excel_videos_data[['Date Posted', 'Views']]
        views_timeseries = views_timeseries.set_index('Date Posted')
        views_timeseries = views_timeseries.groupby('Date Posted')[
            'Views'].sum()
        views_timeseries = views_timeseries.to_frame()
        views_timeseries = views_timeseries.reset_index()
        views_timeseries['Date Posted'] = pd.to_datetime(
            views_timeseries['Date Posted'])
        views_timeseries = views_timeseries.sort_values(by='Date Posted')
        views_timeseries = views_timeseries.set_index('Date Posted')
        views_timeseries = views_timeseries.resample('D').sum()
        views_timeseries = views_timeseries.fillna(0)
        views_timeseries = views_timeseries.reset_index()
        views_timeseries['Date Posted'] = views_timeseries['Date Posted'].dt.strftime(
            '%Y-%m-%d')
        views_timeseries = views_timeseries.to_dict('records')
        self.views_timeseries = views_timeseries
        return self.views_timeseries

    def get_likes_timeseries(self):
        # get the likes time series
        likes_timeseries = self.excel_videos_data[['Date Posted', 'Likes']]
        likes_timeseries = likes_timeseries.set_index('Date Posted')
        likes_timeseries = likes_timeseries.groupby('Date Posted')[
            'Likes'].sum()
        likes_timeseries = likes_timeseries.to_frame()
        likes_timeseries = likes_timeseries.reset_index()
        likes_timeseries['Date Posted'] = pd.to_datetime(
            likes_timeseries['Date Posted'])
        likes_timeseries = likes_timeseries.sort_values(by='Date Posted')
        likes_timeseries = likes_timeseries.set_index('Date Posted')
        likes_timeseries = likes_timeseries.resample('D').sum()
        likes_timeseries = likes_timeseries.fillna(0)
        likes_timeseries = likes_timeseries.reset_index()
        likes_timeseries['Date Posted'] = likes_timeseries['Date Posted'].dt.strftime(
            '%Y-%m-%d')
        likes_timeseries = likes_timeseries.to_dict('records')
        self.likes_timeseries = likes_timeseries
        return self.likes_timeseries

    def get_comments_timeseries(self):
        # get the comments time series
        comments_timeseries = self.excel_videos_data[[
            'Date Posted', 'Comments']]
        comments_timeseries = comments_timeseries.set_index('Date Posted')
        comments_timeseries = comments_timeseries.groupby('Date Posted')[
            'Comments'].sum()
        comments_timeseries = comments_timeseries.to_frame()
        comments_timeseries = comments_timeseries.reset_index()
        comments_timeseries['Date Posted'] = pd.to_datetime(
            comments_timeseries['Date Posted'])
        comments_timeseries = comments_timeseries.sort_values(
            by='Date Posted')
        comments_timeseries = comments_timeseries.set_index('Date Posted')
        comments_timeseries = comments_timeseries.resample('D').sum()
        comments_timeseries = comments_timeseries.fillna(0)
        comments_timeseries = comments_timeseries.reset_index()
        comments_timeseries['Date Posted'] = comments_timeseries['Date Posted'].dt.strftime(
            '%Y-%m-%d')
        comments_timeseries = comments_timeseries.to_dict('records')
        self.comments_timeseries = comments_timeseries
        return self.comments_timeseries

    def get_shares_timeseries(self):
        # get the shares time series
        shares_timeseries = self.excel_videos_data[['Date Posted', 'Shares']]
        shares_timeseries = shares_timeseries.set_index('Date Posted')
        shares_timeseries = shares_timeseries.groupby('Date Posted')[
            'Shares'].sum()
        shares_timeseries = shares_timeseries.to_frame()
        shares_timeseries = shares_timeseries.reset_index()
        shares_timeseries['Date Posted'] = pd.to_datetime(
            shares_timeseries['Date Posted'])
        shares_timeseries = shares_timeseries.sort_values(by='Date Posted')
        shares_timeseries = shares_timeseries.set_index('Date Posted')
        shares_timeseries = shares_timeseries.resample('D').sum()
        shares_timeseries = shares_timeseries.fillna(0)
        shares_timeseries = shares_timeseries.reset_index()
        shares_timeseries['Date Posted'] = shares_timeseries['Date Posted'].dt.strftime(
            '%Y-%m-%d')
        shares_timeseries = shares_timeseries.to_dict('records')
        self.shares_timeseries = shares_timeseries
        return self.shares_timeseries

    def get_videos_timeseries(self):
        # get the videos time series
        videos_timeseries = self.excel_videos_data[[
            'Date Posted', 'Link to TikTok']]
        videos_timeseries = videos_timeseries.set_index('Date Posted')
        videos_timeseries = videos_timeseries.groupby(
            'Date Posted')['Link to TikTok'].count()
        videos_timeseries = videos_timeseries.to_frame()
        videos_timeseries = videos_timeseries.reset_index()
        videos_timeseries['Date Posted'] = pd.to_datetime(
            videos_timeseries['Date Posted'])
        videos_timeseries = videos_timeseries.sort_values(by='Date Posted')
        videos_timeseries = videos_timeseries.set_index('Date Posted')
        videos_timeseries = videos_timeseries.resample('D').sum()
        videos_timeseries = videos_timeseries.fillna(0)
        videos_timeseries = videos_timeseries.reset_index()
        videos_timeseries['Date Posted'] = videos_timeseries['Date Posted'].dt.strftime(
            '%Y-%m-%d')
        videos_timeseries = videos_timeseries.to_dict('records')
        self.videos_timeseries = videos_timeseries
        # change Link to TikTok column name to videos
        self.videos_timeseries = pd.DataFrame(self.videos_timeseries)
        self.videos_timeseries = self.videos_timeseries.rename(
            columns={'Link to TikTok': 'Videos'})
        #add day name column
        self.videos_timeseries['Day'] = self.videos_timeseries['Date Posted'].apply(self.get_day_name_from_date)
        self.videos_timeseries = self.videos_timeseries.to_dict('records')

        return self.videos_timeseries

    def get_day_name_from_date(self, date):
        day = datetime.strptime(date, '%Y-%m-%d').weekday()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[day]
    
    def split_videos_timeseries_into_weeks(self):
        weeks = []
        videos_timeseries = self.videos_timeseries
        # make sure the first day is a sunday, if it's not, add empty days to the start of the array until we reach sunday
        first_day = self.get_day_name_from_date(videos_timeseries[0]['Date Posted'])
        if first_day != 'Sunday':
            days_to_add = 6 if first_day == 'Monday' else 5 if first_day == 'Tuesday' else 4 if first_day == 'Wednesday' else 3 if first_day == 'Thursday' else 2 if first_day == 'Friday' else 1 if first_day == 'Saturday' else 0
            for i in range(days_to_add):
                # date posted is the difference between the first day and the current day in the loop
                date_posted = datetime.strptime(videos_timeseries[0]['Date Posted'], '%Y-%m-%d')
                date_posted -= timedelta(days=i)
                date_posted = date_posted.strftime('%Y-%m-%d')

                videos_timeseries.insert(0, {'Videos': 0, 'Date Posted': date_posted})

        weeks_count = (len(videos_timeseries) + 6) // 7

        for i in range(weeks_count):
            week = videos_timeseries[i*7 : i*7+7]
            weeks.append(week)

        self.videos_timeseries_by_week = weeks
        return weeks

    def save_as_json(self):
        # save all the data as one json file
        data = {
            "profile_details": self.profile_details,
            "totals": self.totals,
            "averages": self.averages,
            "top_videos": (self.top_videos),
            "video_duration_data": self.video_duration_data,
            "hashtags_data": self.hashtags_data,
            "views_timeseries": self.views_timeseries,
            "likes_timeseries": self.likes_timeseries,
            "comments_timeseries": self.comments_timeseries,
            "shares_timeseries": self.shares_timeseries,
            "videos_timeseries": self.videos_timeseries,
            "videos_timeseries_by_week": self.videos_timeseries_by_week
        }

        self.data = data

        data = json.dumps(data, ignore_nan=True)


