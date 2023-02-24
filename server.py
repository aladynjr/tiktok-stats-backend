import pandas as pd
import json
import openpyxl

import requests
from bs4 import BeautifulSoup

# Define the TikTok profile URL
url = 'https://www.tiktok.com/@dylanlemay'

# Send a GET request to the URL with fake headers
response = requests.get(url)

print(response.content)



excelVideosData = pd.read_excel('test_excel.xlsx', sheet_name='Profile Breakdown', header=5, usecols="B:L", skipfooter=1)
excelProfileData = pd.read_excel('test_excel.xlsx', sheet_name='Profile Breakdown', header=2, usecols="B:J", nrows=2)
excelVideosData = pd.DataFrame(excelVideosData)
excelProfileData = pd.DataFrame(excelProfileData)


class Profile(object):
    def __init__(self, excelProfileData, excelVideosData):
        self.excelProfileData = excelProfileData
        self.excelVideosData = excelVideosData
        self.clean_excel_videos_data()

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

        self.views_time_series = None
        self.get_views_time_series()

        self.likes_time_series = None
        self.get_likes_time_series()

        self.comments_time_series = None
        self.get_comments_time_series()

        self.shares_time_series = None
        self.get_shares_time_series()

        self.videos_time_series = None
        self.get_videos_time_series()



    def scrape_profile_details():
        #TODO scrape profile details from tiktok api
        pass

    def clean_excel_videos_data(self):
        #self.excelVideosData.columns = excelVideosData.columns.str.replace(r"[^a-zA-Z]+","", regex=True)
        #from excel videos data columns, remove any character that's not a letter or a space
        self.excelVideosData.columns = self.excelVideosData.columns.str.replace(r"[^a-zA-Z ]+", "", regex=True).str.strip()

        self.excelVideosData['Views'] = self.excelVideosData['Views'].str.replace(',', '').astype(float)
        self.excelVideosData['Likes'] = self.excelVideosData['Likes'].str.replace(',', '').astype(float)
        self.excelVideosData['Comments'] = self.excelVideosData['Comments'].str.replace(',', '').astype(float)
        self.excelVideosData['Shares'] = self.excelVideosData['Shares'].str.replace(',', '').astype(float)

    def get_totals(self):
        #get total videos, turn from string to int, and sum all the values
        total_views = self.excelVideosData['Views'].sum()
        total_likes = self.excelVideosData['Likes'].sum()
        total_comments = self.excelVideosData['Comments'].sum()
        total_shares = self.excelVideosData['Shares'].sum()
        total_duration = self.excelVideosData['Duration'].sum()

        #total videos is the number of rows excluding the header
        total_videos = len(self.excelVideosData.index) - 1

        #create a dictionary with the totals
        self.totals = {
            'total_views': (total_views),
            'total_likes': (total_likes),
            'total_comments': (total_comments),
            'total_shares': (total_shares),
            'total_videos': (total_videos),
            'total_duration': (total_duration)
        }

        return self.totals
    
    def get_averages(self):
        #get averages of views, likes, comments, shares, and duration
        average_views = (self.totals['total_views'] / self.totals['total_videos'])
        average_likes = (self.totals['total_likes'] / self.totals['total_videos'])
        average_comments = (self.totals['total_comments'] / self.totals['total_videos'])
        average_shares = (self.totals['total_shares'] / self.totals['total_videos'])
        average_duration = (self.totals['total_duration'] / self.totals['total_videos'])


        #create a dictionary with the averages
        self.averages = {
            'average_views': int(average_views),
            'average_likes': int(average_likes),
            'average_comments': int(average_comments),
            'average_shares': int(average_shares),
            'average_duration': int(average_duration)
        }

        return self.averages
    
    def get_top_videos(self):
        #get top videos in views, likes, comments, and shares
        top_views = self.excelVideosData.nlargest(5, 'Views')
        top_likes = self.excelVideosData.nlargest(5, 'Likes')
        top_comments = self.excelVideosData.nlargest(5, 'Comments')
        top_shares = self.excelVideosData.nlargest(5, 'Shares')

        #create a dictionary with the top videos

        self.top_videos = {
            'top_views': top_views,
            'top_likes': top_likes,
            'top_comments': top_comments,
            'top_shares': top_shares
        }

        return self.top_videos

    def get_video_duration_data(self):
        #percentages og videos with duration 0-15secs and 15-30secs and 30secs -1min and 1min-3mins and 3-10mins (duration in seconds)
        duration_0_15 = 0
        duration_15_30 = 0
        duration_30_60 = 0
        duration_60_180 = 0
        duration_180_600 = 0

        total_videos = self.totals['total_videos']
        #loop through all the rows in the excel file
        for index, row in self.excelVideosData.iterrows():
            #if duration is 0-15secs
            if row['Duration'] >= 0 and row['Duration'] <= 15:
                duration_0_15 += 1
            #if duration is 15-30secs
            elif row['Duration'] > 15 and row['Duration'] <= 30:
                duration_15_30 += 1
            #if duration is 30secs -1min
            elif row['Duration'] > 30 and row['Duration'] <= 60:
                duration_30_60 += 1
            #if duration is 1min-3mins
            elif row['Duration'] > 60 and row['Duration'] <= 180:
                duration_60_180 += 1
            #if duration is 3-10mins
            elif row['Duration'] > 180 and row['Duration'] <= 600:
                duration_180_600 += 1

        #create a dictionary with the duration data in percentages
        self.video_duration_data = {
            'duration_0_15': (duration_0_15 / total_videos) * 100,
            'duration_15_30': (duration_15_30 / total_videos) * 100,
            'duration_30_60': (duration_30_60 / total_videos) * 100,
            'duration_60_180': (duration_60_180 / total_videos) * 100,
            'duration_180_600': (duration_180_600 / total_videos) * 100
        }

        return self.video_duration_data

    def get_hashtags_data(self):
        frequently_used_hashtags = self.excelProfileData['Frequently Used Hashtags'][0].split(', ')
        #turn to a string, then split by comma and turn to list
        #it's a string in this format icecream[448],  satisfying[224],  cake[160] so turn it to a list of dictionaries of key hashtag name and value number of times used
        hashtags_list = []
        for hashtag in frequently_used_hashtags:
            if('[' not in hashtag):
                continue
            count = hashtag.split('[')[1].split(']')[0]
            if(int(count) < 2):
                continue
            item = {
                'hashtag': hashtag.split('[')[0].strip(),
                'count': hashtag.split('[')[1].split(']')[0]
            }
            hashtags_list.append(item)
        
        #if len(hashtags_list) if bigger than 100, then take the top 100
        if(len(hashtags_list) > 100):
            hashtags_list = hashtags_list[:100]
        
       
        self.hashtags_data = hashtags_list
        return self.hashtags_data

    def get_views_time_series(self):
        #get the views time series
        views_time_series = self.excelVideosData[['Date Posted', 'Views']]
        views_time_series = views_time_series.set_index('Date Posted')
        views_time_series = views_time_series.groupby('Date Posted')['Views'].sum()
        views_time_series = views_time_series.to_frame()
        views_time_series = views_time_series.reset_index()
        views_time_series['Date Posted'] = pd.to_datetime(views_time_series['Date Posted'])
        views_time_series = views_time_series.sort_values(by='Date Posted')
        views_time_series = views_time_series.set_index('Date Posted')
        views_time_series = views_time_series.resample('D').sum()
        views_time_series = views_time_series.fillna(0)
        views_time_series = views_time_series.reset_index()
        views_time_series['Date Posted'] = views_time_series['Date Posted'].dt.strftime('%Y-%m-%d')
        views_time_series = views_time_series.to_dict('records')
        self.views_time_series = views_time_series
        return self.views_time_series

    def get_likes_time_series(self):
        #get the likes time series
        likes_time_series = self.excelVideosData[['Date Posted', 'Likes']]
        likes_time_series = likes_time_series.set_index('Date Posted')
        likes_time_series = likes_time_series.groupby('Date Posted')['Likes'].sum()
        likes_time_series = likes_time_series.to_frame()
        likes_time_series = likes_time_series.reset_index()
        likes_time_series['Date Posted'] = pd.to_datetime(likes_time_series['Date Posted'])
        likes_time_series = likes_time_series.sort_values(by='Date Posted')
        likes_time_series = likes_time_series.set_index('Date Posted')
        likes_time_series = likes_time_series.resample('D').sum()
        likes_time_series = likes_time_series.fillna(0)
        likes_time_series = likes_time_series.reset_index()
        likes_time_series['Date Posted'] = likes_time_series['Date Posted'].dt.strftime('%Y-%m-%d')
        likes_time_series = likes_time_series.to_dict('records')
        self.likes_time_series = likes_time_series
        return self.likes_time_series
    

    def get_comments_time_series(self):
        #get the comments time series
        comments_time_series = self.excelVideosData[['Date Posted', 'Comments']]
        comments_time_series = comments_time_series.set_index('Date Posted')
        comments_time_series = comments_time_series.groupby('Date Posted')['Comments'].sum()
        comments_time_series = comments_time_series.to_frame()
        comments_time_series = comments_time_series.reset_index()
        comments_time_series['Date Posted'] = pd.to_datetime(comments_time_series['Date Posted'])
        comments_time_series = comments_time_series.sort_values(by='Date Posted')
        comments_time_series = comments_time_series.set_index('Date Posted')
        comments_time_series = comments_time_series.resample('D').sum()
        comments_time_series = comments_time_series.fillna(0)
        comments_time_series = comments_time_series.reset_index()
        comments_time_series['Date Posted'] = comments_time_series['Date Posted'].dt.strftime('%Y-%m-%d')
        comments_time_series = comments_time_series.to_dict('records')
        self.comments_time_series = comments_time_series
        return self.comments_time_series

    def get_shares_time_series(self):
        #get the shares time series
        shares_time_series = self.excelVideosData[['Date Posted', 'Shares']]
        shares_time_series = shares_time_series.set_index('Date Posted')
        shares_time_series = shares_time_series.groupby('Date Posted')['Shares'].sum()
        shares_time_series = shares_time_series.to_frame()
        shares_time_series = shares_time_series.reset_index()
        shares_time_series['Date Posted'] = pd.to_datetime(shares_time_series['Date Posted'])
        shares_time_series = shares_time_series.sort_values(by='Date Posted')
        shares_time_series = shares_time_series.set_index('Date Posted')
        shares_time_series = shares_time_series.resample('D').sum()
        shares_time_series = shares_time_series.fillna(0)
        shares_time_series = shares_time_series.reset_index()
        shares_time_series['Date Posted'] = shares_time_series['Date Posted'].dt.strftime('%Y-%m-%d')
        shares_time_series = shares_time_series.to_dict('records')
        self.shares_time_series = shares_time_series
        return self.shares_time_series
    
    def get_videos_time_series(self):
        #get the videos time series
        videos_time_series = self.excelVideosData[['Date Posted', 'Link to TikTok']]
        videos_time_series = videos_time_series.set_index('Date Posted')
        videos_time_series = videos_time_series.groupby('Date Posted')['Link to TikTok'].count()
        videos_time_series = videos_time_series.to_frame()
        videos_time_series = videos_time_series.reset_index()
        videos_time_series['Date Posted'] = pd.to_datetime(videos_time_series['Date Posted'])
        videos_time_series = videos_time_series.sort_values(by='Date Posted')
        videos_time_series = videos_time_series.set_index('Date Posted')
        videos_time_series = videos_time_series.resample('D').sum()
        videos_time_series = videos_time_series.fillna(0)
        videos_time_series = videos_time_series.reset_index()
        videos_time_series['Date Posted'] = videos_time_series['Date Posted'].dt.strftime('%Y-%m-%d')
        videos_time_series = videos_time_series.to_dict('records')
        self.videos_time_series = videos_time_series
        #change Link to TikTok column name to videos 
        self.videos_time_series = pd.DataFrame(self.videos_time_series)
        self.videos_time_series = self.videos_time_series.rename(columns={'Link to TikTok': 'Videos'})
        self.videos_time_series = self.videos_time_series.to_dict('records')



        return self.videos_time_series

      





    
def main():
    profile = Profile(excelProfileData, excelVideosData)
    #print(profile.averages)

main()