import parser
from main import scan 

def test_scan():
    filename = 'test/data/TheAgendawithStevePaikinVideo/012820.rss'
    userstring = 'finance'
    items = scan(filename, userstring)
    assert len(items) == 3

    last = items[len(items)-1]
    assert str(last['text']).startswith('Ontario\'s 16-month-old government announced its first budget last spring ')
    assert last['guid'] == 'http://podcasts.tvo.org/theagenda/video/2587210_11911071710.mp4'

    filename = 'test/data/IntelligenceSquared.xml'
    items = scan(filename, userstring)
    assert len(items) == 4
    assert str(items[2]['text']).endswith('psychologist.  For information regarding your data privacy, visit acast.com/privacy') 

def test_nominal_functionality():
    p = parser.Parser()
    episodes = p.items('test/data/IntelligenceSquared.xml')
    assert len(episodes) == 360
    assert episodes[len(episodes)-1].title == 'Intelligence Squared Presents the Elders'

def test_itunes_image_as_thumbnail():
    p = parser.Parser()
    filename = 'test/data/TheRichRollPodcast/093020.rss'
    episodes = p.items(filename)

    i = 1
    title = 'We Are Water: Erin Brockovich On Pollutants, Politics & People Power'
    thumbnail = 'https://assets.pippa.io/shows/5de6c1c9bd860fd53f965e25/1600582842894-ecd8d04b237e5a36cec72490622faf59.jpeg'
    assert title == episodes[i].title
    assert thumbnail == episodes[i].image 

def test_yahoo_style_image_as_thumbnail():
    p = parser.Parser()
    filename = 'test/data/TheAgendawithStevePaikinVideo/012820.rss'
    episodes = p.items(filename)

    i = 235
    title = 'Marc Bennetts: Developing Dissidence'
    thumbnail = 'http://podcasts.tvo.org/theagenda/images/2179798_320x240_1.jpg'

    assert title == episodes[i].title
    assert episodes[i].image == thumbnail
    
def test_channel_image():
    p = parser.Parser()

    filename = 'test/data/GlobalNewsPodcast/093020.rss' 
    image = 'http://ichef.bbci.co.uk/images/ic/3000x3000/p05z434b.jpg'
    assert image == p.channel_image(filename)

    filename = "test/data/BeatYourGenes/100120.rss"
    image = 'https://dasg7xwmldix6.cloudfront.net/hostpics/ec9c5e62-41d4-446e-86d9-2eb37226f16a_logo_jpg.jpg'
    assert image == p.channel_image(filename)
    
    
    
