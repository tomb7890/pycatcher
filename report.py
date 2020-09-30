from io import StringIO
from lib import sort_reverse_cronologically, configsections, set_sub_from_config, full_path_to_index_file
from string import Template
import index
from subscription import Subscription
import xml.etree.ElementTree 

def doreport(args, fs, outputfilename ):
    text = make_report_text(args, fs)
    write_report_file(outputfilename, text)

def make_report_text(args, fs):
    '''
    Collect all episodes from all subscriptions and sort them
    in reverse chronological order,  make an html report.
    '''
    episodes = []
    cp, sections = configsections()
    
    for section in sections:
        s = Subscription()
        set_sub_from_config(s, cp, section)

        db = index.Index(full_path_to_index_file(s))
        db.load()

        if fs.path_exists(s.rssfile):
            try:
                eps = s.parse_rss_file()
                for e in eps:
                    if e.guid in db.table:
                        filename = db.table[e.guid]
                        if fs.path_exists(filename):
                            e.subscription_title = section
                            e.subscription_image = s.subscription_image
                            episodes.append(e)

            except xml.etree.ElementTree.ParseError as e:
                print("Error with sub %s: %s" % (s.title, e))
                

    if len(episodes) > 0 :
        sort_reverse_cronologically(episodes)
        return make_report_from_episodes(episodes)
    else:
        return None

def write_report_file(filename, text):
    if text is not None:
        with open(filename, 'w') as f:
            f.write(text)
            f.close()

def episode_href(episode):
    return episode.guid

def make_report_from_episodes(episodes):
    templatetext = open('templates/main.html', 'r').read()
    tpl = Template(templatetext)
    header = open('templates/header.html', 'r').read()
    buffer = StringIO()
    for e in episodes:
        write_row_to_container(buffer, e)
    for e in episodes:
        write_description_to_container(buffer, e)
    return tpl.substitute(bootstrap=header, body=buffer.getvalue())

def write_description_to_container(f, ep):
    templatetext = open('templates/panel.html', 'r').read()
    tpl = Template(templatetext)
    f.write(tpl.substitute(id=episode_href(ep), heading=ep.title, body=ep.description))

def write_row_to_container(f, ep):
    image = ep.subscription_image
    if hasattr(ep, 'image'):
        image = ep.image
        
    templatetext = open('templates/row.html', 'r').read()
    tpl = Template(templatetext)
    f.write(tpl.substitute(image=image, sub_title=ep.subscription_title, href=episode_href(ep), 
            ep_title=ep.title, pubdate=ep.pubDate))
            
 
  
