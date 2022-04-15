from moviepy.video.tools.drawing import color_gradient
from PIL import Image
from moviepy.editor import *
import locale
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import moviepy.editor as mpy
from moviepy.editor import *
from csv import DictReader
import requests
import time
import os
import datetime
from datetime import date
import pickle
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

#holy shit lol, thats a lot of importing lol

#===========================================- Vars -==========================================#

body = {
    "client_id": "x",
    "client_secret": "x",
    "grant_type": "client_credentials"
}

today_num = date.today().weekday()
day_colors = [ 
                [[250, 108, 255], [180, 225, 235]], # sunday    | 0
                [[0, 109, 255], [178, 0, 255]],     # saturday  | 1
                [[255, 194, 0], [255, 80, 0]],      # friday    | 2
                [[140, 255, 0], [255, 235, 0]],     # thursday  | 3
                [[255, 120, 0], [255, 0, 250]],     # wednesday | 4
                [[0, 145, 255], [0, 255, 13]],      # tuesday   | 5
                [[0, 255, 230], [246, 255, 0]]      # monday    | 6                   
            ]

total_mintues = 0
scraped_list = []
mydate = datetime.datetime.now()

video_number = 1

#========================================- Functions -=======================================#

def get_valid_credentials(token_name):
    credentials = None
    if os.path.exists(token_name + ".pickle"):
        print("Loading Credentials From File...")
        with open(token_name + ".pickle", "rb") as token:
            credentials = pickle.load(token)
            
    time.sleep(1)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing Access Token...")
            credentials.refresh(Request())
        else:
            print("Fetching New Tokens...")
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                scopes=["https://www.googleapis.com/auth/youtube"]
            )
            flow.run_local_server(port=8080, prompt="consent", authorization_prompt_message="")
            credentials = flow.credentials

            # Save the credentials for the next run
            with open(token_name + ".pickle", "wb") as f:
                print("Saving Credentials for Future Use...")
                pickle.dump(credentials, f)

    return credentials

def get_twitch_api(link):   
    o_auth = requests.post("https://id.twitch.tv/oauth2/token", body).json()["access_token"]       
    time.sleep(1)                                                                            
    api_headers = {"Authorization": "Bearer " + o_auth, "Client-ID": body["client_id"]}
    api_json = requests.get(link, headers = api_headers).json()
    return api_json["data"][0]

def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)

info_fade = 0.4
info_time = 6

def compile_clips(clips_tbl, image_l, scraped_l, save_title):  
    comp_clips = []
    
    #intro
    intro_clip = mpy.VideoFileClip("intro_" + str(today_num) + ".mp4").volumex(0.8)
    intro_clip = intro_clip.subclip(0.08, intro_clip.duration - 0.08)
    comp_clips.append(intro_clip)
    
    clip_i = 0
    open_vids = []
    for i in range(0, len(clips_tbl)):
        print("Opened " + clips_tbl[i])
        open_vids.append(mpy.VideoFileClip(clips_tbl[i]))
        
    for open_video in open_vids:
        video = open_video.subclip(0.1, open_video.duration - 0.1).resize(width=1920,height=1080)
        
        title = scraped_l[clip_i]["title"]
        tlen = clamp(len(title) * 30, 5, 760)

        #======================================- Views and Streamer -======================================#
        views = scraped_l[clip_i]["views"]
        locale.setlocale(locale.LC_ALL, 'en_US')
        view_str = str("{:,}".format(views)) + " views"
        vlen = len(view_str) * 22

        todays_color = day_colors[today_num]
        
        gradv = color_gradient(size=(vlen, 70), p1=(0,0), p2=(vlen,0), col1=todays_color[0], col2=todays_color[1], shape='linear')
        gradmaskv = ImageClip(gradv, transparent=True).set_duration(info_time).set_start((0, 0)).crossfadein(info_fade).crossfadeout(info_fade)
        gradmaskv = gradmaskv.set_position((0.014, 0.82), relative=True)
              
        grad2v = color_gradient(size=(vlen - 20, 50), p1=(0,0), p2=(600,0), col1=[43, 43, 43], col2=[43, 43, 43], shape='linear')
        gradmask2v = ImageClip(grad2v, transparent=True).set_duration(info_time).set_start((0, 0)).crossfadein(info_fade).crossfadeout(info_fade)
        gradmask2v = gradmask2v.set_position((0.019, 0.83), relative=True)
        
        vtxt = mpy.TextClip(str(view_str), size=(vlen - 25, 50), color="white", font="Berlin-Sans-FB", align='West')
        vtxt = vtxt.set_position((0.024, 0.83), relative=True).set_start((0, 0))
        vtxt = vtxt.set_duration(info_time).crossfadein(info_fade).crossfadeout(info_fade)
              
        #========================================- Image and Title -=======================================#

        grad = color_gradient(size=(170 + tlen, 140), p1=(0,0), p2=((170 + tlen) / 2,0), col1=todays_color[0], col2=todays_color[1], shape='linear')
        gradmask = ImageClip(grad, transparent=True).set_duration(info_time).set_start((0, 0)).crossfadein(info_fade).crossfadeout(info_fade)
        gradmask = gradmask.set_position((0.014, 0.70), relative=True)
          
        grad2 = color_gradient(size=(tlen + 15, 121), p1=(0,0), p2=(600,0), col1=[43, 43, 43], col2=[43, 43, 43], shape='linear')
        gradmask2 = ImageClip(grad2, transparent=True).set_duration(info_time).set_start((0, 0)).crossfadein(info_fade).crossfadeout(info_fade)
        gradmask2 = gradmask2.set_position((0.089, 0.71), relative=True)
        
        logo = mpy.ImageClip(image_l[clip_i]).set_duration(info_time).resize(height=120).set_position((0.019, 0.71), relative=True)
        logo = logo.crossfadein(info_fade).crossfadeout(info_fade)
        
        txt = mpy.TextClip(title, size=(tlen, 135), color="white", font="Berlin-Sans-FB", align='West')
        txt = txt.set_position((0.094, 0.70), relative=True).set_start((0, 0))
        txt = txt.set_duration(info_time).crossfadein(info_fade).crossfadeout(info_fade)
        
        video = mpy.CompositeVideoClip([video, gradmaskv, gradmask2v, vtxt, gradmask, gradmask2, logo, txt])
        
        print("Apended clip " + str(post_i))
        
        comp_clips.append(video) 
        
        clip_i += 1
          
    comp_clips.append(mpy.VideoFileClip("outro.mp4"))
          
    comp_video = mpy.concatenate_videoclips(comp_clips, method='compose')

    print("Writing to file as mp4")
    
    # save file
    comp_video.write_videofile(
        save_title, 
        threads = 4, 
        fps = 60,
        codec = "libx264",
        preset = "slow",
        ffmpeg_params = ["-crf", "18"]
    )
    
    comp_video.close()
    for cvid in open_vids:
        cvid.close();
    
    print("!COMPLETE!")

def get_cookies_values(file):
    print("Getting cached cookies")
    with open(file, encoding="utf-8-sig") as f:
        dict_reader = DictReader(f)
        list_of_dicts = list(dict_reader)
    return list_of_dicts

def scrape_post(post_div): 
    print("Scraping...")
    time.sleep(1)
    link_pos = post_div.find_element_by_class_name("_10wC0aXnrUKfdJ4Ssz-o14")
    link = link_pos.find_element_by_tag_name("a").get_attribute("href")
    reddit_title = post_div.find_element_by_class_name("_eYtD2XCVieq6emjKBH3m").text
    if link.find("twitch.tv") != -1:
        clip_end = len(link) if link.rfind("?") == -1 else link.rfind("?")
        clip_id  = link[link.rfind("/") + 1:clip_end]
        
        first_frame = post_div.find_elements_by_tag_name("iframe")
        if len(first_frame) > 0:
            driver.switch_to.frame(first_frame[0])       
            driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
            driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
            
            video = driver.find_element_by_tag_name("video").get_attribute("src")
            
            driver.switch_to.default_content()
            
            return {"id" : clip_id, "video" : video, "title" : reddit_title}
        
    return {"id" : "", "video" : "", "title" : ""}

#=======================================- Driver Setup -======================================#

# Supress annoying warnings
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors-spki-list")
options.add_argument("--ignore-ssl-errors")
options.add_argument("log-level=3")

# Webdriver stuff
driver = webdriver.Chrome(chrome_options=options)
driver.get("https://www.reddit.com/r/LivestreamFail/top/")

cookies = get_cookies_values("cookies.csv")
for i in cookies:
    driver.add_cookie(i)
    
driver.refresh()
        
# Wait for load
time.sleep(7)

# Init main elemnts (body and post list)
main_body = driver.find_element_by_tag_name("body")
main_list = driver.find_element_by_class_name("rpBJOHq2PR60pnwJlUyP0")

# Load page, thus getting more loaded posts
main_body.send_keys(Keys.PAGE_DOWN)
time.sleep(0.7)  

main_body.send_keys(Keys.PAGE_UP)
time.sleep(0.7)
    
#=======================================- Scraping Reddit -======================================#
        
# Prefind hrefs to later compare with clip id"s
divs = main_list.find_elements_by_tag_name("div")
print("TOTAL AMOUNT OF DIVS : " + str(len(divs)))
for div in divs:
    if div.get_attribute("data-testid") == "post-container":
        post_id = div.get_attribute("id")
        nsfw = len(div.find_elements_by_class_name("_1wzhGvvafQFOWAyA157okr")) > 0      
        
        if div.is_displayed() and div.is_enabled():
            time.sleep(1)
            driver.execute_script("arguments[0].scrollIntoView();", div)
            scraped = {"id" : "", "video" : ""}
            
            # Have to click on post and redirect driver to get nsfw video     
            if nsfw: 
                div.click()
                time.sleep(2)
                new_front = driver.find_elements_by_class_name("subredditvars-r-livestreamfail")
                post_div = new_front[2].find_element_by_id(post_id)
                scraped = scrape_post(post_div)
                time.sleep(2)
                driver.back()
            else:
                scraped = scrape_post(div)
                
            if scraped["video"] != "" and scraped["id"] != "":
                clip_info = get_twitch_api("https://api.twitch.tv/helix/clips/?id=" + scraped["id"])

                this_clip = {}
                this_clip["id"] = scraped["id"]
                this_clip["url"] = clip_info["url"]
                this_clip["video"] = scraped["video"]
                this_clip["streamer"] = clip_info["broadcaster_name"]
                this_clip["streamer_id"] = clip_info["broadcaster_id"]
                this_clip["title"] = scraped["title"]
                this_clip["views"] = clip_info["view_count"]
                this_clip["duration"] = clip_info["duration"]
                
                total_mintues += int(clip_info["duration"])
                
                print("Scraped Clip : " + clip_info["title"] + " from " + clip_info["broadcaster_name"])

                scraped_list.append(this_clip)
                
driver.quit()
        
print("TOTAL SCRAPED : " + str(len(scraped_list)))
print("TOTAL MINS : " + str(total_mintues / 60))

post_i = 1
video_list = []
image_list = []
tags = ["livestream fails", "twitch clips", "livestreamfails", "livestreamfail", "lsf", "top kek", "topkek", "r/lsf", "r/livestreamfail", "r/livestreamfail"]
title = "❎ Top of Livestream Fails #" + str(video_number) + " ❌ ("
desc = "\nI do not own any of these clips.\n\n Streamers that were featured in this video : \n----------------------------------------------------------\n-"

for post in scraped_list:     
    time.sleep(1)
    print("Downloading png : " + str(post_i) + "/" + str(len(scraped_list)))
    png_name = "clip_" + str(post_i) + ".png"
    streamer_data = get_twitch_api("https://api.twitch.tv/helix/users?id=" + post["streamer_id"])
    png_req = requests.get(streamer_data["profile_image_url"], allow_redirects = True)
    open(png_name, "wb").write(png_req.content)
    
    # we do a little pasting
    formatter = {"PNG": "RGBA", "JPEG": "RGB"}
    img = Image.open(png_name)
    rgbimg = Image.new(formatter.get(img.format, 'RGB'), img.size)
    rgbimg.paste(img)
    rgbimg.save(png_name, format=img.format)
            
    image_list.append(png_name)
    
    time.sleep(1)
    print("Downloading mp4 : " + str(post_i) + "/" + str(len(scraped_list)))
    video_name = "clip_" + str(post_i) + ".mp4"
    video = requests.get(post["video"], allow_redirects = False)   
    open(video_name, "wb").write(video.content)
    video_list.append(video_name)
    
    desc += "https://www.twitch.tv/" + streamer_data["login"] + "\n" + post["url"] + "\n\n"
    tags.append(post["streamer"])
    tags.append(post["streamer"] + " twitch")
    tags.append(post["streamer"] + " clip")
    
    if post_i < 5:
        if not post["streamer"] in title:
            title += post["streamer"]
        if post_i == 4:
            title += ")"
        else:
            title += ", "
            
    post_i += 1
desc = title + "\n" + desc

print(title)
print(desc)
print(tags)

video_file_title = "twitch_clips_" + mydate.strftime("%B") + ".mp4"
compile_clips(video_list, image_list, scraped_list, video_file_title)

print("VIDEO COMPLETE!")

time.sleep(1)

print("Trash the collection: ")

for nvideo in video_list:
    time.sleep(2)
    if os.path.exists(nvideo):
        os.remove(nvideo)
        print("Removed : " + nvideo)
    else:
        print(nvideo + " does not exist") 
      
for image in image_list:
    time.sleep(2)
    if os.path.exists(image):
        os.remove(image)
        print("Removed : " + image)
    else:
        print(image + " does not exist") 
          
print("Done on our side...")
time.sleep(3)
print("YOUTUBE!")

# no end screen cards, super stupid
youtube = build("youtube", "v3", credentials=get_valid_credentials("clip_bot_token"))
request_body = {
    "snippet": {
        "category": "23",
        "title": title,
        "description": desc,
        "tags": tags,
    },
    "status": {
        "privacyStatus": "private",
        "selfDeclaredMadeForKids": False, 
    },
    "notifySubscribers": True
}
mediaFile = MediaFileUpload(video_file_title)
response_upload = youtube.videos().insert(
    part="snippet,status",
    body=request_body,
    media_body=mediaFile
)
response_upload.execute()

print("UPLOADING TO YOUTBE!!!!! ez clap")
