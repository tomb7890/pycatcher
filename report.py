from io import StringIO
from lib import sort_rev_chron, configsections, set_sub_from_config, full_path_to_index_file
import index
from subscription import Subscription

def doreport(args, fs, outputfilename ):
    text = make_report_text(args, fs)
    write_report_file(outputfilename, text)

def make_report_text(args, fs):
    '''
    Collect all episodes from all subscriptions and sort them
    in reverse chronological order,  make an html report.
    '''
    alleps = []
    cp, sections = configsections()
    
    for section in sections:
        s = Subscription()
        set_sub_from_config(s, cp, section)

        db = index.Index(full_path_to_index_file(s))
        db.load()

        if fs.path_exists(s.rssfile):
            eps = s.parse_rss_file()

            for e in eps:
                if e.guid in db.table:
                    filename = db.table[e.guid]
                    if fs.path_exists(filename):
                        e.subscription_title = section 
                        alleps.append(e)

    if len(alleps) > 0 :
        sort_rev_chron(alleps)
        return make_report_from_eps(alleps)
    else:
        return None

def write_report_file(filename, text):
    if text is not None:
        with open(filename, 'w') as f:
            f.write(text)
            f.close()

def make_report_from_eps(alleps):
    report = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"></head> <body>    _BODY </body></html>'
    f = StringIO()
    for e in alleps:
        write_row_to_container(f, e)

        
    report = report.replace("_BODY", "<container>%s</container>" % f.getvalue())
    return report

def write_row_to_container(f, ep):
    # f.write("<H2>%s</H2>\n" % ep.subscription_title)
    # f.write("<H4>%s</H4>\n" % ep.title)
    # f.write("<DIV>%s</DIV>\n" % ep.pubDate)

    template = """
    <div class="row">
    <div class="col">
      <img src="https://ssl-static.libsyn.com/p/assets/8/2/4/e/824ee7f0ca827522/TheRealityCheck_1400X1400.jpg" 
width="100" height="100" 
    class="img-thumbnail" 
alt="" 
 />
    </div>

    <div class="col">
    %s
    </div>

    <div class="col">
    %s
    </div>

    <div class="col">
    %s
    </div>

    </div>

""" % ( ep.subscription_title, ep.title, ep.pubDate )

    f.write(template) 
    # if ep.description:
    #     desc = ep.description
    #     f.write("<DIV>%s</DIV>\n" % desc)
