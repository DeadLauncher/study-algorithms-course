import requests
import json
from bs4 import BeautifulSoup
def space_remove(string):
    if string[0] == " ":
        string = string[1:]
    return string

def make_dict(l):
    return {str(l.index(v)+1):v for v in l}

output = 'serials.json'

if __name__ == "__main__":
    serials = []
    seasons = []
    episodes = []
    genres = []
    authors = ['Нет данных']
    actors = ['Нет данных']
    statuses = []
    channels = []
    print('Number of pages: ')
    count = int(input())
    print('Parsing...')
    for i in range(1,count+1):
        request = requests.get("https://www.toramp.com/schedule.php?id="+str(i))
        request = request.text
        soup = BeautifulSoup(request,'lxml')
        header = soup.find('h1', {'class': 'title-basic'})
        if header == None:
            i -= 1
            continue
        new_serial = {}
        new_serial['id']= len(serials)+1
        new_serial['tittle'] = soup.find('span', {'itemprop': 'name'}).text
        new_serial['original'] = soup.find('span', {'itemprop': 'alternativeHeadline'}).text
        header = BeautifulSoup(str(soup.find('div',{'class':'second-part-info'})),'lxml')
        content = header.div.contents
        new_serial['genres_ids'] = []
        for k in range(1,len(content)):
            if content[k].name == None:
                new_serial['timing'] = content[k].replace(' - ','').strip()
            elif content[k].name == 'a':
                if content[k].text not in genres:
                    genres.append(content[k].text.strip())
                new_serial['genres_ids'].append(genres.index(content[k].text)+1)
        new_serial['desc'] = soup.find('p',{'class':'body_large summary'}).text
        header = BeautifulSoup(str(soup.find('div',{'class':'content-widget-1'})),'lxml')
        content = header.div.contents
        info2 = BeautifulSoup(str(header.find('a')),'lxml')
        if info2.a == None:
            new_serial['authors_ids'] = [1]
            new_serial['actors_ids'] = [1]
        else:
            new_serial['authors_ids'] = []
            new_serial['actors_ids'] = []
            html2 = requests.get("https://www.toramp.com/"+info2.a.attrs['href'])
            soup1 = BeautifulSoup(html2.text,'lxml')
            blocks = soup1.findAll('div',{'class':'block_list'},'lxml')
            arr = space_remove(BeautifulSoup(str(blocks[1]),'lxml').text).split('\n')
            for j in arr:
                if j not in authors:
                    authors.append(j)
                new_serial['authors_ids'].append(authors.index(j)+1)
            arr = space_remove(BeautifulSoup(str(blocks[2]),'lxml').text).split('\n')
            for j in arr:
                if j not in actors:
                    actors.append(j)
                new_serial['actors_ids'].append(actors.index(j)+1)
        new_serial['channel_id'] = content[9].text
        if content[9].text not in channels:
            channels.append(content[9].text)
        new_serial['channel_id'] = channels.index(content[9].text)+1
        if content[5].text not in statuses:
            statuses.append(content[5].text)
        new_serial['status_id'] = statuses.index(content[5].text)+1
        new_serial['rating'] = BeautifulSoup(str(soup.find('meta',{'itemprop':'ratingValue'})),'lxml').meta['content']
        header = BeautifulSoup(str(soup.find('td',{'id':'img_basic'})),'lxml')
        new_serial['thumb'] = header.td.img.attrs['src']
        
        serials.append(new_serial)

        header = BeautifulSoup(str(''.join(list(map(str,soup.findAll('div',{'id':'full-season'}))))),'lxml')
        s = header.div
        while True:
            new_season = {}
            new_season['id'] = len(seasons)+1
            new_season['serial_id'] = len(serials)
            new_season['tittle'] = s.h2.text.strip()
            seasons.append(new_season)
            for n in s.findAll('tr'):
                new_episode = {}
                new_episode['id'] = len(episodes)+1
                new_episode['season_id'] = len(seasons)
                new_episode['number'] = n.a.span.text
                new_episode['tittle'] = n.td.nextSibling.b.text
                if n.td.nextSibling.span == None:
                    new_episode['original'] = ''
                else:
                    new_episode['original'] = n.td.nextSibling.span.text
                new_episode['published'] = n.td.nextSibling.nextSibling.nextSibling.span.text
                episodes.append(new_episode)
            s = s.nextSibling
            if s == None:
                break
        print(i,'/',count)
    print('Parsed!')
    with open(output, "w",encoding='utf-8') as file:
        file.write(json.dumps({'genres':make_dict(genres),'authors':make_dict(authors),'actors':make_dict(actors),'statuses':make_dict(statuses),'channels':make_dict(channels),'serials':serials,'seasons':seasons,'episodes':episodes},indent=4, ensure_ascii=False))
    print(output,'was successfully written.')


        
