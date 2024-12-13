import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import sqlite3
from db import insert_data,fetch_data_from_db,delete_data_from_db
import isodate

def search_youtube_data(api_key, channel_id):


    yt = build('youtube', 'v3', developerKey=api_key)
    req = yt.channels().list(
        part='snippet,statistics,contentDetails',
        id=channel_id
    )
    channels =[]
    playlists =[]
    resp = req.execute()
    print(resp)
    item = resp['items'][0]
    channel_name = item['snippet']['title']
    channel_views = item['statistics']['viewCount']
    channel_description = item['snippet']['description']
    channel_status = 'Active'
    subscriber_count = item['statistics']['subscriberCount']
    video_count = item['statistics']['videoCount']
    playlist_Id = item['contentDetails']['relatedPlaylists']['uploads']
    playlist_name = item['snippet']['title']

    req = yt.search().list(
        part='snippet,id',
        channelId=channel_id,
        maxResults=11
    )
    resp = req.execute()
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
            item = resp['items'][0]
            video_likes = item['statistics'].get('likeCount', 0)
            video_dislikes = item['statistics'].get('dislikesCount', 0)
            video_comment_count = item['statistics'].get('commentCount', 0)
            video_views = item['statistics'].get('viewCount', 0)
            duration = item['contentDetails'].get('duration', 0)
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
            'channel_views': channel_views,
            'channel_description': channel_description,
            'channel_status': channel_status,
            'subscriber_count': subscriber_count,
            'video_count': video_count,
            'playlist_Id': playlist_Id

    })

    playlists.append({
            'channel_id': channel_id,
            'playlist_Id': playlist_Id,
            'playlist_name' : playlist_name

    })   

    df1 = pd.DataFrame(channels)
    df2 = pd.DataFrame(videos)
    df3 = pd.DataFrame(comments)
    df4 = pd.DataFrame(playlists)
    return (df1,df2,df3,df4)

def main():

    tab1, tab2, tab3 = st.tabs(["Data Harvesting", "Query Records", "Database"])
    if 'df1' not in st.session_state:
        st.session_state.df1 = None
    if 'df2' not in st.session_state:
        st.session_state.df2 = None
    if 'df3' not in st.session_state:
        st.session_state.df3 = None
    if 'df4' not in st.session_state:
        st.session_state.df4 = None

    with tab1:
        flag=0
       
        st.markdown(":streamlit:")
    
        st.title("Data Harvesting")
        apikey = st.text_input("Enter Api Key")
        
        cols = st.columns(5)
        st.title("Channels")
        Channels = [
            "Select",
            "Parithabangal", 
            "TECH BOSS", 
            "TAMIL TECH", 
            "TECH THALAIVA", 
            "TECHSHAN", 
            "TECHDREAMS", 
            "THIS IS TECH TODAY",
            "CNN",
            "Vikkals",
            "Trakin Tech Tamil"
        ]

        selected_option = st.selectbox("Select an option", Channels)
        Channel_id = [
                None,
                "UCueYcgdqos0_PzNOq81zAFg", 
                "UCnKhQkCUS1oCEvjuTfU4xIw", 
                "UC20sXo8ReewkzNKBFgzVCPA", 
                "UCwZiV2eywcB2XAcD1-6UCrQ",
                "UCe_-TsRz3GH8UVjN0ApzXJQ", 
                "UCzq1xxLmhvFfYUzKM4M8OyA",
                "UCEAMLkMKtq6YhmaZdUT1ywA",
                "UCupvZG-5ko_eiXAupbDfxWw",
                "UC60c1RHrJ-4ta2GZYOM9Mcg",
                "UCmJlSkSkgdXama3GSUgMC4g"
        ]
        
        selected_index = Channels.index(selected_option)
        
        channelid = Channel_id[selected_index]
        with cols[0]:
            if st.button("Look up"):
                (st.session_state.df1,st.session_state.df2,st.session_state.df3,st.session_state.df4) = search_youtube_data(apikey, channelid)
     
        if st.session_state.df1 is not None:
            st.write(st.session_state.df1)
        with cols[1]:  
            if st.button("Store to Sqlite"):
                if st.session_state.df1 is not None and st.session_state.df2 is not None and st.session_state.df3 is not None:
                    try:
                        insert_data(st.session_state.df1, 'channel')
                        insert_data(st.session_state.df2, 'video')
                        insert_data(st.session_state.df3, 'comment')
                        insert_data(st.session_state.df4, 'playlist')
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
            "1) What are the names of all the videos and their corresponding channels?",
            "2) Which channels have the most number of videos, and how many videos do they have?",
            "3) What are the top 10 most viewed videos and their respective channels?",
            "4) How many comments were made on each video, and what are their corresponding video names?",
            "5) Which videos have the highest number of likes, and what are their corresponding channel names?",
            "6) What is the total number of likes for each video, and what are their corresponding video names?",
            "7) What is the total number of views for each channel, and what are their corresponding channel names?",
            "8) What are the names of all the channels that have published videos in the year 2022?",
            "9) What is the average duration of all videos in each channel, and what are their corresponding channel names?",
            "10) Which videos have the highest number of comments, and what are their corresponding channel names?"
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
        
        selected_index = options.index(selected_option)
        
        query = queries[selected_index]

        if query is not None:
            results = fetch_data_from_db(query)
            cols = st.columns(1)
            with cols[0]:
                st.write(results)
    
    with tab3:
        st.title("Database")
        cols = st.columns(5)
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
            if st.button("Playlist DB"):
                res = fetch_data_from_db("SELECT * FROM playlist")
        with cols[4]:
            if st.button("Delete DB"):
                res = delete_data_from_db("delete from channel")
                res = delete_data_from_db("delete from video")
                res = delete_data_from_db("delete from comment")
                res = delete_data_from_db("delete from playlist")
        if res is not None:
            st.write(res)
        else:
            st.warning("No data!")
                
        

if __name__ == "__main__":
    main()