import requests
import os
import re

def scrape_subreddit_images(subreddit_name, sort_type="hot", output_dir="reddit_images", limit=50):
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
            # Check for direct image links or Reddit-hosted images
            img_url = None
            if post_data.get('post_hint') == 'image' and 'url' in post_data:
                img_url = post_data['url']
            elif 'preview' in post_data and 'images' in post_data['preview']:
                img_url = post_data['preview']['images'][0]['source']['url']
                img_url = img_url.replace('&amp;', '&')
            if img_url and re.search(r'\.(jpg|jpeg|png|webp)$', img_url, re.IGNORECASE):
                try:
                    img_data = requests.get(img_url, headers=headers).content
                    ext = os.path.splitext(img_url)[1].split('?')[0]
                    filename = f"image_{count}{ext}"
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
                    print(f"Downloaded: {filename}")
                    count += 1
                    if count >= limit:
                        break
                except Exception as e:
                    print(f"Failed to download {img_url}: {e}")
        after = data.get('data', {}).get('after')
        if not after:
            break
    print(f"Total images downloaded: {count}")

if __name__ == "__main__":
    subreddit = input("Enter subreddit: ")
    sort = input("Enter sort type (hot, new, top, best, rising): ") or "hot"
    output = input("Enter output directory: ") or "reddit_images"
    scrape_subreddit_images(subreddit, sort_type=sort, output_dir=output)
