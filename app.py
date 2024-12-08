import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import sqlite3
import pandas as pd 
from db import insert_data,fetch_data_from_db,delete_data_from_db
import isodate

def search_youtube_data(api_key, channel_id):
    yt = build('youtube', 'v3', developerKey=api_key)
    req = yt.channels().list(
        part='snippet,statistics',
        id=channel_id
    )
    channels =[]
    resp = req.execute()
    print(resp)
    item = resp['items'][0]
    channel_name = item['snippet']['title']
    # channel_type = item['snippet']['type']
    channel_views = item['statistics']['viewCount']
    channel_description = item['snippet']['description']
    channel_status = 'Active'
    subscriber_count = item['statistics']['subscriberCount']
    video_count = item['statistics']['videoCount']
    
    req = yt.search().list(
        part='snippet,id',
        channelId=channel_id,
        maxResults=10
    )
    resp = req.execute()
    #print(resp)
    videos = []
    for item in resp['items']:
        if item['id']['kind'] == 'youtube#video':
            video_id = item['id']['videoId']
            video_title = item['snippet']['title']
            video_description = item['snippet']['description']
            video_upload_date = item['snippet']['publishedAt']
            
      
            req = yt.videos().list(
                part='statistics,contentDetails',
                id=video_id
            )
            resp = req.execute()
            print(resp)
            video_dislikes = 0
            video_likes = resp['items'][0]['statistics'].get('likeCount', 0)
            video_dislikes = resp['items'][0]['statistics'].get('dislikeCount', 0)
            video_comment_count = resp['items'][0]['statistics'].get('commentCount', 0)
            video_views = resp['items'][0]['statistics'].get('viewCount', 0)
            duration = resp['items'][0]['contentDetails'].get('duration', 0)
            request = yt.commentThreads().list(
                part='snippet', 

                videoId=video_id,
                maxResults=10
            )
            response = request.execute()

            comments = []
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textOriginal']
                author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                published_at = item['snippet']['topLevelComment']['snippet']['publishedAt']

                comment_id = item['id']

                comments.append({
                    'comment_id': comment_id,
                    'video_id': video_id,
                    'comment_text': comment,
                    'comment_author': author,
                    'comment_published_date': published_at
                })
            videos.append({
                'video_id': video_id,
                'channel_id': channel_id,
                'video_title': video_title,
                'video_description': video_description,
                'video_upload_date': video_upload_date,
                'video_comment_count': video_comment_count,
                'video_views': video_views,
                'video_likes': video_likes,
                'video_dislikes': video_dislikes,
                'duration': isodate.parse_duration(duration).total_seconds()
            })
    channels.append({
            'channel_id': channel_id,
            'channel_name': channel_name,
            # 'channel_type': channel_type,
            'channel_views': channel_views,
            'channel_description': channel_description,
            'channel_status': channel_status,
            'subscriber_count': subscriber_count,
            'video_count': video_count

    })   

    df1 = pd.DataFrame(channels)
    df2 = pd.DataFrame(videos)
    df3 = pd.DataFrame(comments)
    return (df1,df2,df3)

def main():
   # global df1, df2, df3
    #st.set_page_config(layout="wide")
    tab1, tab2, tab3 = st.tabs(["Youtube Search Channels", "Query Records", "Table Data"])
    if 'df1' not in st.session_state:
        st.session_state.df1 = None
    if 'df2' not in st.session_state:
        st.session_state.df2 = None
    if 'df3' not in st.session_state:
        st.session_state.df3 = None
    
    with tab1:
        flag=0
        st.title("Youtube Search Channels")
        #apikey = st.text_input("Enter Api Key")
        channelid = st.text_input("Enter Channel Id")
        
        cols = st.columns(6)
        
        with cols[0]:
            if st.button("Search"):
                (st.session_state.df1,st.session_state.df2,st.session_state.df3) = search_youtube_data('AIzaSyBRqgoPkqCvMQfGF4iYNda9T8jFDyI98F4', channelid)
                #st.write(st.session_state.df2)
                #st.write(st.session_state.df3)
        if st.session_state.df1 is not None:
            st.write(st.session_state.df1)
        with cols[1]:  
            if st.button("Save to DB"):
                if st.session_state.df1 is not None and st.session_state.df2 is not None and st.session_state.df3 is not None:
                    try:
                        insert_data(st.session_state.df1, 'channel')
                        insert_data(st.session_state.df2, 'video')
                        insert_data(st.session_state.df3, 'comment')
                        flag=1
                    except sqlite3.IntegrityError as e:
                        st.warning("Channel is already present")
                else:
                    st.warning("Data is not available. Please search data")
        if flag:
            st.success("Data is successfully added!")
                       

    with tab2:
        st.title("Query Records")
        options = [
            "Select",
            "What are the names of all the videos and their corresponding channels?",
            "Which channels have the most number of videos, and how many videos do they have?",
            "What are the top 10 most viewed videos and their respective channels?",
            "How many comments were made on each video, and what are their corresponding video names?",
            "Which videos have the highest number of likes, and what are their corresponding channel names?",
            "What is the total number of likes for each video, and what are their corresponding video names?",
            "What is the total number of views for each channel, and what are their corresponding channel names?",
            "What are the names of all the channels that have published videos in the year 2022?",
            "What is the average duration of all videos in each channel, and what are their corresponding channel names?",
            "Which videos have the highest number of comments, and what are their corresponding channel names?"
        ]

        selected_option = st.selectbox("Select an option", options)

        queries = [
                None,
                "SELECT v.video_title, c.channel_name FROM video v JOIN channel c ON v.channel_id = c.channel_id;",
                "SELECT c.channel_name, COUNT(v.video_id) AS video_count FROM channel c JOIN video v ON c.channel_id = v.channel_id GROUP BY c.channel_name ORDER BY video_count DESC;",
                "SELECT v.video_title, c.channel_name, v.video_views FROM video v JOIN channel c ON v.channel_id = c.channel_id ORDER BY v.video_views DESC LIMIT 10;",
                "SELECT v.video_title, v.video_comment_count AS comment_count FROM video v;",
                "SELECT v.video_title, c.channel_name, v.video_likes FROM video v JOIN channel c ON v.channel_id = c.channel_id ORDER BY v.video_likes DESC LIMIT 10;",
                "SELECT v.video_title, SUM(v.video_likes) AS total_likes FROM video v GROUP BY v.video_title;",
                "SELECT c.channel_name, SUM(v.video_views) AS total_views FROM channel c JOIN video v ON c.channel_id = v.channel_id GROUP BY c.channel_name;",
                "SELECT c.channel_name FROM channel c JOIN video v ON c.channel_id = v.channel_id WHERE v.video_upload_date BETWEEN '2022-01-01' AND '2022-12-31';",
                "SELECT c.channel_name, AVG(v.duration) AS avg_duration FROM channel c JOIN video v ON c.channel_id = v.channel_id GROUP BY c.channel_name;",
                "SELECT v.video_title, c.channel_name, COUNT(cm.comment_id) AS comment_count FROM video v JOIN channel c ON v.channel_id = c.channel_id JOIN comment cm ON v.video_id = cm.video_id GROUP BY v.video_title ORDER BY comment_count DESC;"
        ]

        st.write(selected_option)
        
        selected_index = options.index(selected_option)
        
        query = queries[selected_index]

        if query is not None:
            results = fetch_data_from_db(query)
            cols = st.columns(1)
            with cols[0]:
                st.write(results)
    
    with tab3:
        st.title("Table Data")
        cols = st.columns(4)
        res = None
        with cols[0]:
            if st.button("Channels DB"):
                res = fetch_data_from_db("SELECT * FROM channel")
        with cols[1]:
            if st.button("Videos DB"):
                res = fetch_data_from_db("SELECT * FROM video")
        with cols[2]:
            if st.button("Comments DB"):
                res = fetch_data_from_db("SELECT * FROM comment")
        with cols[3]:
            if st.button("Delete Tables"):
                res = delete_data_from_db("delete from channel")
                res = delete_data_from_db("delete from video")
                res = delete_data_from_db("delete from comment")
        if res is not None:
            st.write(res)
        else:
            st.warning("No data!")
                
        

if __name__ == "__main__":
    main()