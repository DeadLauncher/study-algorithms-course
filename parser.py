import requests
import json
from bs4 import BeautifulSoup

def space_remove(string):
    """
    Function removes odd spaces and control characters from string
    :param string: source string
    :type string: str
    :return: new string
    :rtype: str
    """
    if string[0] == " ":
        string = string[1:]
    if string[-1] == " ":
        string = string[:-2]
    string = string.replace('\r','')
    return string

def make_dict(l):
    """
    Function makes a dictionary with list indexes as keys and list objects as values
    :param l: source list
    :type l: list
    :return: formed dictionary
    :rtype: dict
    """
    return {str(l.index(v)+1):v for v in l}

output = 'serials.json'

if __name__ == "__main__":
    #lists of parsing objects
    serials = []
    seasons = []
    episodes = []
    genres = []
    authors = []
    actors = []
    statuses = []
    channels = []
    #get parsing pages quantity
    print('Number of pages:',end=' ')
    count = int(input())
    print('Parsing...')
    #common cycle for parsing of every serial
    for i in range(1,count+1):
        #get serial html page code
        html1 = requests.get("https://www.toramp.com/schedule.php?id="+str(i))
        html1 = html1.text
        #make soup from html page
        soup1 = BeautifulSoup(html1,'lxml')
        #check if the page is empty
        soup2 = soup1.find('span', {'itemprop': 'name'})
        if soup2 == None:
            continue
        #get info from header
        new_serial = {}
        new_serial['id']= len(serials)+1
        new_serial['title'] = soup2.text
        new_serial['original'] = soup1.find('span', {'itemprop': 'alternativeHeadline'}).text
        #get genres list
        soup2 = BeautifulSoup(str(soup1.find('div',{'class':'second-part-info'})),'lxml')
        content = soup2.div.contents
        new_serial['genres_ids'] = []
        #fill in genres of serial
        for k in range(1,len(content)):
            if content[k].name == None:
                new_serial['timing'] = content[k].replace(' - ','').strip()
            elif content[k].name == 'a':
                if content[k].text not in genres:
                    genres.append(content[k].text)
                new_serial['genres_ids'].append(genres.index(content[k].text)+1)
        #get serial description
        new_serial['desc'] = soup1.find('p',{'class':'body_large summary'}).text
        #get additional info
        soup2 = BeautifulSoup(str(soup1.find('div',{'class':'content-widget-1'})),'lxml')
        content = soup2.div.contents
        new_serial['authors_ids'] = []
        new_serial['actors_ids'] = []
        #get link for more info and check it for existance
        soup2 = BeautifulSoup(str(soup2.find('a')),'lxml')
        if soup2.a != None:
            #make soup from page with more info
            html2 = requests.get("https://www.toramp.com/"+soup2.a.attrs['href'])
            soup3 = BeautifulSoup(html2.text,'lxml')
            #get tags with authors and actors as list
            blocks = soup3.findAll('div',{'class':'block_list'},'lxml')
            #fill in authors
            arr = space_remove(BeautifulSoup(str(blocks[1]),'lxml').text).split('\n')
            for j in arr:
                j = j.strip()
                if j not in authors:
                    authors.append(j)
                new_serial['authors_ids'].append(authors.index(j)+1)
            arr = space_remove(BeautifulSoup(str(blocks[2]),'lxml').text).split('\n')
            #fill in actors
            for j in arr:
                j = j.strip()
                if j not in actors:
                    actors.append(j)
                new_serial['actors_ids'].append(actors.index(j)+1)
        #get and fill in channels
        new_serial['channels_ids'] = []
        for ch in content[9].text.split(','):
            ch = ch.strip()
            if ch not in channels:
                channels.append(ch)
            new_serial['channels_ids'].append(channels.index(ch)+1)   
        #get and fill in satuses
        if content[5].text not in statuses:
            statuses.append(content[5].text)
        new_serial['status_id'] = statuses.index(content[5].text)+1
        #get rating
        new_serial['rating'] = BeautifulSoup(str(soup1.find('meta',{'itemprop':'ratingValue'})),'lxml').meta['content']
        #get image url
        soup2 = BeautifulSoup(str(soup1.find('td',{'id':'img_basic'})),'lxml')
        new_serial['thumb'] = soup2.td.img.attrs['src']
        #add serial into list of parsed serials
        serials.append(new_serial)
        #get and parse seasons
        soup2 = BeautifulSoup(str(''.join(list(map(str,soup1.findAll('div',{'id':'full-season'}))))),'lxml')
        s = soup2.div
        while True:
            new_season = {}
            new_season['id'] = len(seasons)+1
            #get main info
            new_season['serial_id'] = len(serials)
            new_season['title'] = s.h2.text.strip()
            seasons.append(new_season)
            #get and parse episodes
            for n in s.findAll('tr'):
                new_episode = {}
                new_episode['id'] = len(episodes)+1
                #get main info
                new_episode['season_id'] = len(seasons)
                new_episode['number'] = n.a.span.text.strip()
                new_episode['title'] = n.td.nextSibling.b.text.strip()
                #check if orginal name exists
                if n.td.nextSibling.span == None:
                    new_episode['original'] = ''
                else:
                    new_episode['original'] = n.td.nextSibling.span.text.strip()
                new_episode['published'] = n.td.nextSibling.nextSibling.nextSibling.span.text.strip()
                episodes.append(new_episode)
            s = s.nextSibling
            #check the end of seasons
            if s == None:
                break
        #print parsing progress
        print(i,'/',count)
    print('Parsed!')
    #save parsed data into json file
    with open(output, "w",encoding='utf-8') as file:
        file.write(json.dumps({'genres':make_dict(genres),'authors':make_dict(authors),'actors':make_dict(actors),'statuses':make_dict(statuses),'channels':make_dict(channels),'serials':serials,'seasons':seasons,'episodes':episodes},indent=4, ensure_ascii=False))
    print(output,'was successfully written.')