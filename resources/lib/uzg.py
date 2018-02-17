'''
    resources.lib.uzg
    ~~~~~~~~~~~~~~~~~

    An XBMC addon for watching SchoolTV(NTR)
   
    :license: GPLv3, see LICENSE.txt for more details.

    SchoolTV (NTR) = Made by Bas Magre (Opvolger)    
    based on: https://github.com/jbeluch/plugin.video.documentary.net

'''
import urllib2 ,re ,time ,json #, xbmc
from datetime import datetime

class Uzg:
        #
        # Init
        #
        def __init__( self):
            self.overzichtcacheleeftijd = {}
            self.leeftijden = { 0: '0-4',
                                1: '5-6',
                                2: '7-8',
                                3: '9-12',
                                4: '13-15',
                                5: '16-18'}
        
        def __leeftijd(self, sort, ageCategoryint):  
            leeftijdstring = self.leeftijden[ageCategoryint]
            # http://m.schooltv.nl/api/v1/leeftijdscategorieen/0-4/afleveringen.json?size=100&sort=Nieuwste
            req = urllib2.Request('http://m.schooltv.nl/api/v1/leeftijdscategorieen/' + leeftijdstring + '/afleveringen.json?size=100&sort=' + sort)
            req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:25.0) Gecko/20100101 Firefox/25.0')
            response = urllib2.urlopen(req)
            link=response.read()
            response.close()
            json_data = json.loads(link)
            uzgitemlist = list()
            #print json_data
            for result in json_data['results']:
                print result
                uzgitem = { 'label': result['title'] + ' ' + result['subtitle'], 'whatson_id': result['mid'], 'thumbnail': result['image'], 'duration': result['duration'] }
                uzgitemlist.append(uzgitem)                
            #self.overzichtcacheleeftijd = sorted(uzgitemlist, key=lambda x: x['label'], reverse=False)
            self.overzichtcacheleeftijd[ageCategoryint] = uzgitemlist

        def __get_data_from_url(self, url):
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:25.0) Gecko/20100101 Firefox/25.0')
            response = urllib2.urlopen(req)
            data=response.read()
            response.close()
            return data    
            
        def get_play_url(self, whatson_id):
            data = self.__get_data_from_url('http://e.omroep.nl/metadata/' + whatson_id)
            vooreraf = str(data.split("parseMetadata(")[1])
            achteraf = str(vooreraf.split("})\n")[0]) + "}"
            print achteraf
            json_data = json.loads(achteraf)
            #xbmc.log('json_data: %s' % json_data, xbmc.LOGNOTICE)
            print json_data['medium']
            if json_data['medium'] != 'tv':
                url_play = json_data['streams'][0]['url']
            else:
                #token aanvragen
                ## http://ida.omroep.nl/npoplayer/i.js?s=http%3A%2F%2Fwww.schooltv.nl%2Fvideo%2Fhoe-blijven-strijkkralen-aan-elkaar-vastplakken-de-kralen-smelten-een-beetje-als-ze-verwarmd-word%2F%23q%3Dstrijkijzer
                data = self.__get_data_from_url('http://ida.omroep.nl/npoplayer/i.js?s=http%3A%2F%2Fwww.schooltv.nl%2Fvideo%2Fhoe-blijven-strijkkralen-aan-elkaar-vastplakken-de-kralen-smelten-een-beetje-als-ze-verwarmd-word%2F%23q%3Dstrijkijzer')
                token = re.compile('.token\s*=\s*"(.*?)"', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
                #print token
                ##video lokatie aanvragen
                ##h264_bb,h264_sb,h264_std,wmv_bb,wmv_sb,wvc1_std
                urlgemaakt = 'http://ida.omroep.nl/odi/?prid='+whatson_id+'&puboptions=h264_bb,h264_sb,h264_std,wmv_bb,wmv_sb,wvc1_std&adaptive=yes&part=1&token='+self.__get_newtoken(token)
                #xbmc.log('HANDLE: %s' % urlgemaakt, xbmc.LOGNOTICE)
                data = self.__get_data_from_url(urlgemaakt)
                #print data
                json_data = json.loads(data)
                ##video file terug geven vanaf json antwoord
                #xbmc.log('HANDLE: %s' % json_data, xbmc.LOGNOTICE)
                streamdataurl = json_data['streams'][0]
                streamurl = str(streamdataurl.split("?")[0]) + '?'
                print streamurl
                #xbmc.log('streamurl: %s' % streamurl, xbmc.LOGNOTICE)
                data = self.__get_data_from_url(streamurl)
                json_data = json.loads(data)
                #xbmc.log('json_data: %s' % json_data, xbmc.LOGNOTICE)
                url_play = json_data['url']
            print url_play
            return url_play
            
        def __get_newtoken(self, token):
            # site change, token invalid, needs to be reordered. Thanks to rieter for figuring this out very quickly.
            first = -1
            last = -1
            for i in range(5, len(token) - 5, 1):	
                if token[i].isdigit():
                    if first < 0:
                        first = i                
                    elif last < 0:
                        last = i                
                        break

            newtoken = list(token)
            if first < 0 or last < 0:
                first = 12
                last = 13
            newtoken[first] = token[last]
            newtoken[last] = token[first]
            newtoken = ''.join(newtoken)    
            return newtoken            

        def get_leeftijd(self, leeftijdint):
            if leeftijdint in self.overzichtcacheleeftijd:
                return self.overzichtcacheleeftijd[leeftijdint]
            else:
                self.__leeftijd('Nieuwste', leeftijdint)
            return self.overzichtcacheleeftijd[leeftijdint]                       

        def get_overzicht(self):            
            overzichtlist = list()            
            overzichtlist.append({ 'label': 'leeftijden', 'type': 'leeftijden', 'functie': 'leeftijdkeuze' })
            #overzichtlist.append({ 'label': 'categorieen', 'type': 'categorieen', 'functie': 'categoriekeuze' })
            #overzichtlist.append({ 'label': 'programmas', 'type': 'programmas', 'functie': 'programmakeuze' })
            return overzichtlist
            
        def get_leeftijden(self):            
            overzichtlist = list()
            for index, (key, value) in enumerate(self.leeftijden.items()):
                overzichtlist.append({ 'label': 'leeftijd '+ value, 'leeftijdint': key })
            return overzichtlist            
    
        def __build_item(self, post):    
            ##item op tijd gesorteerd zodat ze op volgorde staan.
            if (len(post['label']) == 0):
                titelnaam = post['serienaam']
            else:
                titelnaam = post['label']

            item = {
                'label': '(' + post['TimeStamp'].split('T')[1] + ') - ' + titelnaam,
                'date': post['date'],
                'thumbnail': post['thumbnail'],
                'whatson_id': post['whatson_id'],
            }
            return item

        def __stringnaardatumnaarstring(self, datumstring):
            b = datetime(*(time.strptime(datumstring.split('T')[0], "%Y-%m-%d")[0:6]))
            return b.strftime("%d-%m-%Y")
