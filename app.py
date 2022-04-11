from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import requests
import urllib.request, urllib.parse, urllib.error
import json
import re
from bs4 import BeautifulSoup

app = Flask(__name__)
bootstrap = Bootstrap() 

api_key = { 'search engine': 'AIzaSyCVt_jtzuIwoh2NeXZMd_VUAfTJmHHyxzE',
        #   'search engine': 'AIzaSyCW0_VmQHhO_MzNWVV1JgyR_3KoMiYXfK8',
        #    'search engine': 'AIzaSyDhRjh-4mQc-m3RW_QLyoSCQrTP9RwCVA8',
           'YouTube': 'AIzaSyDhRjh-4mQc-m3RW_QLyoSCQrTP9RwCVA8'
        #    'YouTube':  'AIzaSyDP80OpDrE2HuzMtX5oLkI0npQfVVRnSQ8'
        }
address = {'search engine': 'https://www.googleapis.com/customsearch/v1?cx=275a1fa53bb7ae074',
           'YouTube': 'https://www.googleapis.com/youtube/v3/search?part=snippet&q='}


#KKbox get Token
def get_access_token():
    url = "https://account.kkbox.com/oauth2/token" 
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "account.kkbox.com"
    }

    data = {
        "grant_type": "client_credentials",
        "client_id": "6bfbe0a126b8c7710408b5a91b1c687e",
        "client_secret": "965ceb7b4990c7ad52e2adbd5f1ff8b8"
        # "client_id": "86bb18373fe156b39718d04143291511",
        # "client_secret": "d25f09316e1c900d4f9fece0004c3aec"
    }
    access_token = requests.post(url, headers=headers, data=data)
    return access_token.json()["access_token"]


#KKbox get list
def get_charts():

    access_token = get_access_token() 
   
    url = "https://api.kkbox.com/v1.1/charts"
    
    headers = {
        "accept": "application/json",
        "authorization": "Bearer " + access_token 
    }
    
    params = {
        "territory": "TW"   
    }
    response = requests.get(url, headers=headers, params=params)
    result = response.json()["data"]
    return result

#KKbox get songs in the list
def get_charts_tracks(chart_id):
    
    access_token = get_access_token() 
   
    url = "https://api.kkbox.com/v1.1/charts/" + chart_id + "/tracks"
    
    headers = {
        "accept": "application/json",
        "authorization": "Bearer " + access_token
    }
    
    params = {
        "territory": "TW"  
    }
    response = requests.get(url, headers=headers, params=params)
    result = response.json()["data"]
    songs = list()
    for item in result:
        songs.append(item["name"])

    return songs


@app.route('/', methods=['POST','GET'])
def index():
    
    if request.method=='POST':
        if request.values['send'] == ' Search the song ':
            song = request.values['song']
            if song == '':
                return render_template('result.html', warning = False , lyrics_not_found = False, video_not_found = True, lyrics = [], lyrics_title = '')
            #change the space in the song into '_'
            song = song.replace(" ","_")
            song = song.replace("-","_")
            try:
                find = requests.get(address['YouTube'] + song + '&key=' + api_key['YouTube'] + '&type=video&maxResults=10')
            except:
                return render_template('result.html', warning = True)
    
            jsonFind = json.loads(find.text)

            video_id = list()
            video_title = list()
            video_description = list()
            video_link = list()

            for i in range(10):
                video_link.append('https://www.yout.com/watch?v='+jsonFind['items'][i]['id']['videoId'])
                video_id.append('https://www.youtube.com/embed/'+jsonFind['items'][i]['id']['videoId'])
                video_title.append(jsonFind['items'][i]['snippet']['title'])
                video_description.append(jsonFind['items'][i]['snippet']['description'])
            
            try:
                ffind = requests.get( address['search engine'] + '&key=' + api_key['search engine'] + '&q=' + song + '&siteSearch=kkbox.com/tw/tc/')
            except:
                return render_template('result.html', video_id = video_id, video_title = video_title, video_description = video_description, video_link= video_link ,lyric_not_found = True)
            
            jsonfFind = json.loads(ffind.text)
            lyrics = urllib.request.urlopen(jsonfFind['items'][0]['link'])

            #use beautiful soup to get the lyrics
            soup = BeautifulSoup( lyrics , "html.parser" )
            tags = soup.find_all( "p" , class_="lyrics" )
            lyricsOutput = list()
            for tag in tags:
                new = tag.decode().split('<')
                for thing in new:
                    if re.search( r'^p', thing) == None:
                        lyricsOutput.append(thing.split('>'))

            lyrics_title = soup.find_all("h1" ,class_="section-title")
            filter_title = re.search( r'\">(.+)<' , lyrics_title[0].decode()).group(1)

            
            return render_template('result.html', warning = False, video_id = video_id, video_title = video_title, video_link= video_link, video_description = video_description, lyrics_not_found = False, lyrics = lyricsOutput, lyrics_title = filter_title)
    return render_template('result.html', warning = False , lyrics_not_found = False, video_not_found = True, lyrics = [], lyrics_title = '')

@app.route('/list_0')
def list_0():
    List = get_charts_tracks(get_charts()[0]['id'])
    list_title = '綜合新歌即時榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_1')
def list_1():
    List = get_charts_tracks(get_charts()[1]['id'])
    list_title = '華語單曲日榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_2')
def list_2():
    List = get_charts_tracks(get_charts()[2]['id'])
    list_title = '西洋單曲日榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_3')
def list_3():
    List = get_charts_tracks(get_charts()[3]['id'])
    list_title = '韓語單曲日榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_4')
def list_4():
    List = get_charts_tracks(get_charts()[4]['id'])
    list_title = '日語單曲日榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_5')
def list_5():
    List = get_charts_tracks(get_charts()[5]['id'])
    list_title = '台語單曲日榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_6')
def list_6():
    List = get_charts_tracks(get_charts()[6]['id'])
    list_title = '粵語單曲日榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_7')
def list_7():
    List = get_charts_tracks(get_charts()[7]['id'])
    list_title = '華語新歌日榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_8')
def list_8():
    List = get_charts_tracks(get_charts()[8]['id'])
    list_title = '西洋新歌日榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_9')
def list_9():
    List = get_charts_tracks(get_charts()[9]['id'])
    list_title = '韓語新歌日榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_10')
def list_10():
    List = get_charts_tracks(get_charts()[10]['id'])
    list_title = '日語新歌日榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_11')
def list_11():
    List = get_charts_tracks(get_charts()[11]['id'])
    list_title = '台語新歌日榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_12')
def list_12():
    List = get_charts_tracks(get_charts()[12]['id'])
    list_title = '粵語新歌日榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_13')
def list_13():
    List = get_charts_tracks(get_charts()[13]['id'])
    list_title = '電子單曲週榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_14')
def list_14():
    List = get_charts_tracks(get_charts()[14]['id'])
    list_title = '嘻哈單曲週榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_15')
def list_15():
    List = get_charts_tracks(get_charts()[15]['id'])
    list_title = 'R＆B單曲週榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_16')
def list_16():
    List = get_charts_tracks(get_charts()[16]['id'])
    list_title = '爵士單曲週榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_17')
def list_17():
    List = get_charts_tracks(get_charts()[17]['id'])
    list_title = '搖滾單曲週榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_18')
def list_18():
    List = get_charts_tracks(get_charts()[18]['id'])
    list_title = '獨立/另類單曲週榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_19')
def list_19():
    List = get_charts_tracks(get_charts()[19]['id'])
    list_title = '原聲帶單曲週榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_20')
def list_20():
    List = get_charts_tracks(get_charts()[20]['id'])
    list_title = '靈魂樂單曲週榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_21')
def list_21():
    List = get_charts_tracks(get_charts()[21]['id'])
    list_title = '鄉村單曲週榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_22')
def list_22():
    List = get_charts_tracks(get_charts()[22]['id'])
    list_title = '雷鬼單曲週榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_23')
def list_23():
    List = get_charts_tracks(get_charts()[23]['id'])
    list_title = '有聲書 / 相聲單曲週榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_24')
def list_24():
    List = get_charts_tracks(get_charts()[24]['id'])
    list_title = '英美金曲榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_25')
def list_25():
    List = get_charts_tracks(get_charts()[25]['id'])
    list_title = '錢櫃國語點播榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_26')
def list_26():
    List = get_charts_tracks(get_charts()[26]['id'])
    list_title = '錢櫃台語點播榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_27')
def list_27():
    List = get_charts_tracks(get_charts()[27]['id'])
    list_title = '錢櫃國語新歌榜'
    return render_template('list.html', List= List, list_title = list_title)

@app.route('/list_28')
def list_28():
    List = get_charts_tracks(get_charts()[28]['id'])
    list_title = '錢櫃台語新歌榜'
    return render_template('list.html', List= List, list_title = list_title)


if __name__ == '__main__':
    app.run(debug=True, port= 8512)