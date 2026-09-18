"""
Instagram Media & Video Scraper for Anshita Makeover (@anshitamakeover21)
Scrapes real photos, videos, and reels directly from Instagram into temp/instagram_downloads/
and outputs temp/instagram_summary.json.

Usage:
    python scrape_instagram.py [--username anshitamakeover21] [--max-posts 12]
"""
import os
import sys
import json
import argparse
import urllib.request
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp" / "instagram_downloads"
TEMP_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_FILE = BASE_DIR / "temp" / "instagram_summary.json"

def download_file(url, target_path):
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp, open(target_path, 'wb') as f:
        f.write(resp.read())

def download_instagram_video(url, target_stem):
    try:
        import yt_dlp
        ydl_opts = {
            'outtmpl': str(TEMP_DIR / f"{target_stem}.%(ext)s"),
            'quiet': True,
            'no_warnings': True,
            'format': 'mp4/bestvideo+bestaudio/best',
            'socket_timeout': 18
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info)
            if os.path.exists(video_file):
                return os.path.basename(video_file), str(video_file)
    except Exception as e:
        print(f"    [-] Video stream download note: {e}")
    return None, None

def scrape_instagram_with_videos(username="anshitamakeover21", max_posts=12):
    print(f"[*] Connecting directly to Instagram (@{username})...")
    scraped_posts = []
    
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900}
            )
            page = context.new_page()
            url = f"https://www.instagram.com/{username}/"
            print(f"[*] Navigating to {url}...")
            
            try:
                page.goto(url, timeout=35000, wait_until="domcontentloaded")
            except Exception as e:
                print(f"[!] Navigation notice: {e}")
                
            page.wait_for_timeout(3500)
            
            # Dismiss cookies/modals
            for selector in ['button:has-text("Allow")', 'button:has-text("Decline")', 'button:has-text("Accept")', 'div[role="dialog"] button']:
                try:
                    btn = page.query_selector(selector)
                    if btn:
                        btn.click()
                        page.wait_for_timeout(800)
                except Exception:
                    pass

            page.mouse.wheel(0, 900)
            page.wait_for_timeout(2000)
            
            elements = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
            print(f"[+] Found {len(elements)} Instagram post/reel anchors on page.")
            
            seen_hrefs = set()
            for idx, el in enumerate(elements):
                if len(scraped_posts) >= max_posts:
                    break
                try:
                    href = el.get_attribute('href')
                    if not href or href in seen_hrefs:
                        continue
                    seen_hrefs.add(href)
                    
                    full_href = href if href.startswith('http') else f"https://www.instagram.com{href}"
                    shortcode = href.strip('/').split('/')[-1]
                    
                    img_el = el.query_selector('img')
                    img_src = img_el.get_attribute('src') if img_el else None
                    alt_text = img_el.get_attribute('alt') if img_el else ''
                    
                    is_reel = '/reel/' in href
                    
                    post_item = {
                        "shortcode": shortcode,
                        "type": "reel" if is_reel else "photo",
                        "instagram_url": full_href,
                        "caption": alt_text or f"Instagram look by @{username}",
                        "thumbnail_file": None,
                        "thumbnail_path": None,
                        "video_file": None,
                        "video_path": None
                    }
                    
                    # 1. Download image thumbnail
                    if img_src and img_src.startswith('http'):
                        img_filename = f"ig_{'reel' if is_reel else 'post'}_{shortcode}.jpg"
                        img_local_path = TEMP_DIR / img_filename
                        try:
                            download_file(img_src, img_local_path)
                            post_item["thumbnail_file"] = img_filename
                            post_item["thumbnail_path"] = str(img_local_path)
                            print(f"[{len(scraped_posts)+1}/{max_posts}] Photo cover: {img_filename}")
                        except Exception as e:
                            print(f"[-] Could not download photo: {e}")
                    
                    # 2. If it's a video or reel, download the .mp4 video stream
                    if is_reel:
                        print(f"    [*] Fetching MP4 video stream for reel {shortcode}...")
                        vid_name, vid_path = download_instagram_video(full_href, f"ig_video_{shortcode}")
                        if vid_name:
                            post_item["video_file"] = vid_name
                            post_item["video_path"] = vid_path
                            print(f"    [+] MP4 Video Saved: {vid_name}")
                    
                    scraped_posts.append(post_item)
                except Exception as e:
                    continue
            browser.close()
            
    except Exception as e:
        print(f"[!] Playwright scrape exception: {e}")

    summary = {
        "status": "success",
        "target_account": f"@{username}",
        "profile_url": f"https://www.instagram.com/{username}/",
        "total_scraped": len(scraped_posts),
        "output_directory": str(TEMP_DIR),
        "posts": scraped_posts
    }
    
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as sf:
        json.dump(summary, sf, indent=2, ensure_ascii=False)
        
    print(f"\n[+] Successfully saved {len(scraped_posts)} items into {TEMP_DIR}")
    print(f"[+] Review summary written to {SUMMARY_FILE}\n")
    print("--- Instagram Video & Photo Review ---")
    for idx, p in enumerate(scraped_posts):
        clean_cap = p['caption'][:55].encode('ascii', 'ignore').decode('ascii')
        v_info = f" | Video: {p['video_file']}" if p.get('video_file') else ""
        print(f"[{idx+1}] {p['type'].upper()} | {clean_cap}...{v_info} | {p['instagram_url']}")
    print("--------------------------------------\n")
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Instagram Media & Video Scraper for Anshita Makeover")
    parser.add_argument("--username", default="anshitamakeover21", help="Target Instagram handle")
    parser.add_argument("--max-posts", type=int, default=10, help="Max posts to scrape")
    args = parser.parse_args()
    
    scrape_instagram_with_videos(args.username, args.max_posts)
