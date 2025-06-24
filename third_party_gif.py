import requests
import os
import re
import json
import urllib3
from urllib.parse import urlparse

# Suppress insecure request warnings when we disable SSL verification as a last resort
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extract_gif_url(url):
    video_id = None
    
    # Extract the ID from various redgif URL formats
    if "redgifs.com" in url or "gifdeliverynetwork.com" in url:
        path = urlparse(url).path
        # Extract ID from paths like /watch/SomethingHere or /SomethingHere or /ifr/SomethingHere
        match = re.search(r'/watch/([^/]+)$|/([^/]+)$|/ifr/([^/]+)$', path)
        if match:
            video_id = match.group(1) or match.group(2) or match.group(3)
            print(f"Extracted video ID: {video_id}")
    
    if not video_id:
        print(f"Failed to extract video ID from: {url}")
        return None
    
    # First, get authentication token
    token = get_gifs_token()
    if not token:
        print("Failed to get authentication token for Redgifs API")
        # Try alternative direct methods
    else:
        print(f"Successfully obtained Redgifs auth token")
        
        # Get API information for the video
        api_url = f"https://api.redgifs.com/v2/gifs/{video_id}"
        print(f"Requesting API URL: {api_url}")
        
        # Modern user agent and additional headers required by Redgifs API
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Referer': 'https://www.redgifs.com/',
            'Accept': 'application/json',
            'Origin': 'https://www.redgifs.com',
            'Authorization': f'Bearer {token}'
        }
        
        try:
            response = requests.get(api_url, headers=headers)
            print(f"API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                # Extract the HD URL if available, otherwise use the SD URL
                gif_data = data.get('gif', {})
                urls = gif_data.get('urls', {})
                
                # Try different URL formats that might be available
                video_url = urls.get('hd') or urls.get('sd') or urls.get('mp4') or urls.get('mobile')
                
                if video_url:
                    print(f"Successfully extracted video URL: {video_url}")
                    return video_url
                else:
                    print(f"No video URL found in API response. Available keys: {urls.keys() if urls else 'No URLs found'}")
            else:
                print(f"API request failed with status {response.status_code}")
                # Try to print the error response
                try:
                    print(f"Error response: {response.text[:200]}")
                except:
                    pass
                    
        except Exception as e:
            print(f"Error extracting Redgif URL: {e}")
    
    # If the API method failed, try alternative methods
    
    # Try to scrape the webpage directly
    try:
        print(f"Trying to scrape the webpage: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Look for HD video URL in the HTML content
            # Pattern examples: "https://thumbs.redgifs.com/something.mp4" or similar
            video_patterns = [
                r'(https://\w+\.redgifs\.com/\w+\.mp4)',
                r'(https://\w+\.redgifs\.com/\w+-mobile\.mp4)',
                r'source src="(https://[^"]+\.mp4)"',
                r'"contentUrl": "(https://[^"]+\.mp4)"'
            ]
            
            for pattern in video_patterns:
                matches = re.findall(pattern, html_content)
                if matches:
                    print(f"Found video URL in HTML: {matches[0]}")
                    return matches[0]
                    
            print("No video URL found in HTML content")
        else:
            print(f"Failed to fetch webpage, status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error scraping webpage: {e}")
    
    # Try several potential direct URL formats
    direct_url_formats = [
        f"https://thumbs.redgifs.com/{video_id}.mp4",
        f"https://thumbs1.redgifs.com/{video_id}.mp4",
        f"https://thumbs2.redgifs.com/{video_id}.mp4", 
        f"https://thumbs3.redgifs.com/{video_id}.mp4",
        f"https://thumbs4.redgifs.com/{video_id}.mp4",
        f"https://thumbs5.redgifs.com/{video_id}.mp4",
        f"https://thumbs.redgifs.com/{video_id}-mobile.mp4"
    ]
    
    for direct_url in direct_url_formats:
        try:
            print(f"Trying direct URL: {direct_url}")
            head_resp = requests.head(direct_url, timeout=5, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            })
            if head_resp.status_code == 200:
                print(f"Direct URL worked: {direct_url}")
                return direct_url
        except Exception as e:
            print(f"Error checking direct URL {direct_url}: {e}")
    
    return None

def get_gifs_token():
    try:
        # First try to get the temporary token from the main page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        # Get the main page to extract any available tokens or authentication details
        response = requests.get("https://www.redgifs.com/", headers=headers)
        
        if response.status_code == 200:
            # Look for the token in the JavaScript code
            html_content = response.text
            
            # Try different patterns to find the token
            token_patterns = [
                r'accessToken:"([^"]+)"',
                r'token:"([^"]+)"',
                r'"token":"([^"]+)"'
            ]
            
            for pattern in token_patterns:
                token_match = re.search(pattern, html_content)
                if token_match:
                    token = token_match.group(1)
                    return token
        
        # If the above didn't work, try the OAuth endpoint to get a token
        print("Trying to get temporary OAuth token")
        oauth_url = "https://api.redgifs.com/v2/auth/temporary"
        resp = requests.get(oauth_url, headers=headers)
        
        if resp.status_code == 200:
            data = resp.json()
            token = data.get('token')
            if token:
                return token
                
        print(f"Failed to get Redgifs authentication token, status: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"Error getting Redgifs token: {e}")
        return None



def scrape_gif_videos(subreddit_name, sort_type="hot", output_dir="redgif_videos", limit=50):
    url = f"https://www.reddit.com/r/{subreddit_name}/{sort_type}.json"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    after = None
    
    while count < limit:
        params = {'limit': 500}
        if after:
            params['after'] = after
        
        try:
            print(f"Fetching Reddit page: {url} with params {params}")
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                print(f"Failed to fetch page: {response.status_code}")
                break
                
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            if not posts:
                print("No more posts found.")
                break
            
            print(f"Found {len(posts)} posts to process")    
            for post in posts:
                post_data = post.get('data', {})
                permalink = post_data.get('permalink')
                post_url = post_data.get('url')
                
                if not post_url:
                    continue
                
                video_url = None
                  # Check if it's a Redgif link
                if "redgifs.com" in post_url or "gifdeliverynetwork.com" in post_url:
                    print(f"Found Redgif link: {post_url}")
                    video_url = extract_gif_url(post_url)
                    if not video_url:
                        print("Failed to extract Redgif video URL")
                
                # Try to check for embedded Redgif links in selftext
                elif 'selftext' in post_data and post_data['selftext']:
                    selftext = post_data['selftext']
                    # Look for Redgif links in the text
                    redgif_match = re.search(r'https?://(?:www\.)?redgifs\.com/\S+', selftext)
                    
                    if redgif_match:
                        redgif_url = redgif_match.group(0)
                        print(f"Found Redgif link in selftext: {redgif_url}")
                        video_url = extract_gif_url(redgif_url)
                
                if video_url:
                    max_retries = 3
                    retry_count = 0
                    
                    while retry_count < max_retries:
                        try:
                            print(f"Downloading video from: {video_url} (Attempt {retry_count + 1}/{max_retries})")
                            # Set additional headers for the download request
                            download_headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                                'Referer': post_url,
                                'Accept': 'video/webm,video/mp4,video/*;q=0.9,*/*;q=0.8',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'Connection': 'keep-alive',
                                'Range': 'bytes=0-'  # Request the full file
                            }
                            
                            # First try with SSL verification
                            try:
                                video_response = requests.get(video_url, headers=download_headers, stream=True, timeout=30)
                            except requests.exceptions.SSLError:
                                print("SSL verification failed, trying without verification (not recommended but might work)")
                                video_response = requests.get(video_url, headers=download_headers, stream=True, timeout=30, verify=False)
                            
                            # Check if the response was successful
                            if video_response.status_code not in [200, 206]:  # 200 OK or 206 Partial Content
                                print(f"Failed to download, status code: {video_response.status_code}")
                                print(f"Response headers: {video_response.headers}")
                                retry_count += 1
                                continue
                                
                            # Check if we got content
                            content_length = int(video_response.headers.get('Content-Length', 0))
                            if content_length == 0:
                                print("Warning: Content-Length is 0, will try to download anyway")
                                
                            print(f"Content length: {content_length} bytes")
                            
                            # Get file extension from URL or content-type or default to .mp4
                            ext = os.path.splitext(video_url)[1]
                            if not ext or len(ext) > 5:  # If no extension or suspicious extension
                                content_type = video_response.headers.get('Content-Type', '')
                                if 'video/mp4' in content_type:
                                    ext = '.mp4'
                                elif 'video/webm' in content_type:
                                    ext = '.webm'
                                else:
                                    ext = '.mp4'  # Default
                            
                            # Remove query parameters from extension
                            ext = ext.split('?')[0]
                                
                            # Create filename with post title if available, otherwise use counter
                            if post_data.get('title'):
                                # Sanitize the title for use in filename
                                safe_title = re.sub(r'[\\/*?:"<>|]', "", post_data['title'])
                                safe_title = safe_title[:50]  # Limit title length
                                filename = f"{safe_title}_{count}{ext}"
                            else:
                                filename = f"video_{count}{ext}"
                                
                            filepath = os.path.join(output_dir, filename)
                            
                            # Download with progress indicator
                            downloaded = 0
                            with open(filepath, 'wb') as f:
                                for chunk in video_response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                                        downloaded += len(chunk)
                                        # Show progress every ~10%
                                        if content_length > 0 and downloaded % (max(content_length // 10, 1)) < 8192:
                                            percent = (downloaded / content_length) * 100
                                            print(f"Download progress: {percent:.1f}%")
                                        elif downloaded % 1048576 == 0:  # Show progress every 1MB if content_length is unknown
                                            print(f"Downloaded {downloaded/1048576:.1f} MB")
                            
                            # Verify the download completed successfully
                            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                                print(f"Downloaded: {filename} ({os.path.getsize(filepath)} bytes)")
                                count += 1
                                break  # Success, exit retry loop
                            else:
                                print(f"Download appears to have failed: file size is {os.path.getsize(filepath) if os.path.exists(filepath) else 'file not found'}")
                                retry_count += 1
                                
                        except requests.exceptions.Timeout:
                            print(f"Timeout error downloading {video_url}. Attempt {retry_count + 1}/{max_retries}")
                            retry_count += 1
                        except requests.exceptions.RequestException as e:
                            print(f"Network error downloading {video_url}: {e}. Attempt {retry_count + 1}/{max_retries}")
                            retry_count += 1
                        except Exception as e:
                            print(f"Failed to download {video_url}: {e}. Attempt {retry_count + 1}/{max_retries}")
                            retry_count += 1
                    
                    # Check if we reached the download limit        
                    if count >= limit:
                        print(f"Reached download limit of {limit}")
                        break
              # Get the 'after' parameter for the next page
            after = data.get('data', {}).get('after')
            if not after:
                print("No more pages available.")
                break
                
        except Exception as e:
            print(f"Error processing page: {e}")
            break
            
    print(f"Total Redgif videos downloaded: {count}")

if __name__ == "__main__":
    subreddit = input("Enter subreddit: ")
    sort = input("Enter sort type (hot, new, top, best, rising): ") or "hot"
    output = input("Enter output directory: ") or "redgif_videos"
    limit = int(input("Enter download limit: ") or "50")
    scrape_gif_videos(subreddit, sort_type=sort, output_dir=output, limit=limit)