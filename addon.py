'''
    Uitzendinggemist(NPO)
    ~~~~~~~

    An XBMC addon for watching uzg 
    :license: GPLv3, see LICENSE.txt for more details.
    
    based on: https://github.com/jbeluch/plugin.video.documentary.net
    Uitzendinggemist(NPO) / uzg = Made by Bas Magre (Opvolger)
    
'''
from xbmcswift2 import Plugin, SortMethod
import resources.lib.uzg
import time
import xbmcplugin

PLUGIN_NAME = 'schooltv'
PLUGIN_ID = 'plugin.video.schooltv'
plugin = Plugin(PLUGIN_NAME, PLUGIN_ID, __file__)

uzg = resources.lib.uzg.Uzg()

@plugin.route('/')
def index():    
    items = [{
        'path': plugin.url_for(item['functie'], type=item['type']),
        'label': item['label']        
    } for item in uzg.get_overzicht()]       
    return items
    
@plugin.route('/leeftijdkeuze')
def leeftijdkeuze():
    items = [{
        'path': plugin.url_for('show_leeftijd', leeftijdint=item['leeftijdint']),
        'label': item['label']        
    } for item in uzg.get_leeftijden()]    
    return items    

@plugin.route('/leeftijdkeuze/<leeftijdint>/')
def show_leeftijd(leeftijdint):
    items = [{
        'path': plugin.url_for('play_lecture', whatson_id=item['whatson_id']),        
        'label': item['label'],
        'is_playable': True,
        'info': {
                   "title": item['label'],
                   "duration": item['duration']
                },
        'thumbnail': item['thumbnail'],
    } for item in uzg.get_leeftijd(int(float(leeftijdint)))]    
    return items

@plugin.route('/type/show/<whatson_id>/')
def play_lecture(whatson_id):
	plugin.set_resolved_url(uzg.get_play_url(whatson_id))

if __name__ == '__main__':
    plugin.run()
