import subscription


def test_episodes_known_to_not_have_data():
    print("Hello World  ")

    s = subscription.Subscription()
    s.rssfile = "test/data/BeatYourGenes/100120.rss"

    reference_image = "https://dasg7xwmldix6.cloudfront.net/hostpics/ec9c5e62-41d4-446e-86d9-2eb37226f16a_logo_jpg.jpg"
    
    eps = s.parse_rss_file()
    for e in eps[0:4]:
        assert s.subscription_image == reference_image
        assert e.image is None

def test_episodes_known_to_have_data():

    s = subscription.Subscription()
    filename = 'test/data/TheAgendawithStevePaikinVideo/012820.rss'
    episodes = s.parse_rss_file(filename)

    i = 235
    title = 'Marc Bennetts: Developing Dissidence'
    thumbnail = 'http://podcasts.tvo.org/theagenda/images/2179798_320x240_1.jpg'

    e = episodes[i]

    assert title == episodes[i].title
    assert hasattr(e, 'image')
    assert e.image == thumbnail
    
