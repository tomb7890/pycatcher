from subscription import Subscription

def test_setting_of_subscription_image():
    s = Subscription()
    s.rssfile = "test/data/BeatYourGenes/100120.rss"
    # s.set_sub_from_config(s, cp, section)

    reference_image = 'https://dasg7xwmldix6.cloudfront.net/hostpics/ec9c5e62-41d4-446e-86d9-2eb37226f16a_logo_jpg.jpg'

    eps = s.parse_rss_file()
    for e in eps:
        assert s.subscription_image == reference_image


    
            

            
