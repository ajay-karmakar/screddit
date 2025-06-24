import requests
import os
import re

def scrape_subreddit_videos(subreddit_name, sort_type="new", output_dir="reddit_videos", limit=50):
    url = f"https://www.reddit.com/r/{subreddit_name}/{sort_type}.json"
    headers = {'User-Agent': 'Mozilla/5.0'}
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    after = None
    while count < limit:
        params = {'limit': 100}
        if after:
            params['after'] = after
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            break
        data = response.json()
        posts = data.get('data', {}).get('children', [])
        if not posts:
            break
        for post in posts:
            post_data = post.get('data', {})
            video_url = None
            # Reddit-hosted video
            if post_data.get('is_video') and 'media' in post_data and post_data['media'] and 'reddit_video' in post_data['media']:
                video_url = post_data['media']['reddit_video'].get('fallback_url')
            # Animated GIFs (hosted on Reddit or external)
            elif 'url' in post_data and re.search(r'\.(gif|mp4|webm)$', post_data['url'], re.IGNORECASE):
                video_url = post_data['url']
            # Gfycat or Redgifs links (optional, can be expanded)
            if video_url and re.search(r'\.(mp4|webm|gif)$', video_url, re.IGNORECASE):
                try:
                    vid_data = requests.get(video_url, headers=headers).content
                    ext = os.path.splitext(video_url)[1].split('?')[0]
                    filename = f"video_{count}{ext}"
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(vid_data)
                    print(f"Downloaded: {filename}")
                    count += 1
                    if count >= limit:
                        break
                except Exception as e:
                    print(f"Failed to download {video_url}: {e}")
        after = data.get('data', {}).get('after')
        if not after:
            break
    print(f"Total videos/gifs downloaded: {count}")

if __name__ == "__main__":
    subreddit = input("Enter subreddit: ")
    sort = input("Enter sort type (hot, new, top, best, rising): ") or "new"
    output = input("Enter output directory: ") or "reddit_videos"
    scrape_subreddit_videos(subreddit, sort_type=sort, output_dir=output)
