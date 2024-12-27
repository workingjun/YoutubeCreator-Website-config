import re
from scripts.youtube.utils import is_short_video, transform_datetime

class YouTubeResponseHandler:
    @staticmethod
    def parse_response(api_name, response):
        """API 이름에 따라 응답 처리"""
        parsers = {
            "channels.list": YouTubeResponseHandler._parse_channel_information,
            "videos.list": YouTubeResponseHandler._parse_video_statistics,
            "commentThreads.list": YouTubeResponseHandler._parse_comments,
            "search.list": YouTubeResponseHandler._parse_channel_id_by_name,
            "search.Idlist": YouTubeResponseHandler._parse_video_Ids
        }

        parser = parsers.get(api_name)
        if not parser:
            raise ValueError(f"Unsupported API: {api_name}")

        return parser(response)
    
    @staticmethod
    def _parse_channel_id_by_name(response):
        """채널 이름으로 채널 ID를 가져오는 함수"""
        if response['items']:
            # 검색 결과에서 채널 ID와 이름 추출
            channel_info = response['items'][0]
            channel_id = channel_info['id']['channelId']
            return channel_id
        else:
            return None

    @staticmethod
    def _parse_channel_information(response):
        """채널 정보 응답 처리"""
        channel_info = response["items"][0]
        return {
            "title": channel_info["snippet"]["title"],
            "channel_id": channel_info["id"],
            "description": channel_info["snippet"]["description"],
            "subscriber_count": int(channel_info["statistics"]["subscriberCount"]),
            "video_count": int(channel_info["statistics"]["videoCount"]),
            "views_count": int(channel_info["statistics"]["viewCount"]),
        }

    @staticmethod
    def _parse_comments(response, video_id):
        try:
            # 댓글 정리
            comments_data = []
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                text = comment['textDisplay']  # 댓글 텍스트
                like_count = comment['likeCount']  # 좋아요 수
                author = comment['authorDisplayName']  # 작성자 이름
                  # HTML 태그 제거
                comments_data.append({"author":author,"text":text_clean,"like_count":like_count})  # 작성자 추가
            return comments_data
        except:
            return None
        
    @staticmethod
    def _parse_comments(response):
        """댓글 응답 처리"""
        comments = []
        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": snippet["authorDisplayName"],
                "text": re.sub(r'<.*?>', '', snippet["textDisplay"]),
                "like_count": snippet["likeCount"],
                "publish_time": snippet["publishedAt"],
            })
        return comments

        
    @staticmethod
    def _parse_video_statistics(response):
        """비디오 통계 응답 처리"""
        for item in response["items"]:
            duration = item["contentDetails"]["duration"]
            publish_time = transform_datetime(item['snippet']['publishedAt'])  # 업로드 날짜 추가
            is_short = is_short_video(duration)
            return {
                "video_id": item["id"],
                "title": item["snippet"]["title"],
                "view_count": int(item["statistics"].get("viewCount", 0)),
                "like_count": int(item["statistics"].get("likeCount", 0)),
                "comment_count": int(item["statistics"].get("commentCount", 0)),
                "publish_time": publish_time,
                "is_shorts": is_short
            }
    
    @staticmethod
    def _parse_video_Ids(response):
        video_data = []
        for item in response['items']:
            if item['id']['kind'] == "youtube#video":
                video_id = item['id']['videoId']
                published_time = transform_datetime(item['snippet']['publishedAt']) 
                video_data.append({
                    "video_id": video_id,
                    "published_time": published_time
                })
        return video_data


