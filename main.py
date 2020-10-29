from parser import Parser
from lxml.html import document_fromstring
from result import Result


def downloaded_episodes(subscription, fs):
    episodes = subscription.episodes()
    de = []
    for e in episodes:
        if subscription.database.find(e.guid):
            filename = subscription.database.get(e)
            if fs.path_exists(filename):
                de.append(e)
    return de


def scan(filename, userstring):
    p = Parser()

    ## TODO wrap this in try/catch!
    episodes = p.items(filename)
    items = []
    for e in episodes:
        if userstring in (e.description):
            html = e.description
            doc = document_fromstring(html)
            i = {}
            i["guid"] = e.guid
            i["text"] = doc.text_content()
            items.append(i)
    return items


def list_episodes(subscription, fs):
    episodes = downloaded_episodes(subscription, fs)
    return list_elements(episodes)


def list_subscriptions(subscriptions):
    return list_elements(subscriptions)


def list_elements(elements):
    items = []
    n = 0
    for e in elements:
        n = n + 1
        items.append(f">>> {n}. {e.title}")
    formatted_text = "\n".join(items)
    return formatted_text


def play_episode(fs, player, args, subs):
    episodes = None
    try:
        s = args.play[0]
        si = int(s) - 1  # This might raise Value error
        subscription = subs[si]  # this might raise index error
        subscription.database.load()
        episodes = downloaded_episodes(subscription, fs)

        e = args.play[1]
        ei = int(e) - 1  # This might raise Value Error
        episode = episodes[ei]  # this might raise  Index Eror
        fullpath = subscription.database.get(episode)
        player.play(fullpath)
        return Result.ok()

    except IndexError:
        if episodes is None:
            message = (
                f"{si} is not in the correct range. "
                + "Please try again from this list: \n"
                + list_subscriptions(subs)
            )
        else:
            message = (
                f"{ei} is not in the correct range. "
                + "Please try again from this list: \n"
                + list_episodes(subscription, fs)
            )

        return Result.fail(message)

    except ValueError:
        if episodes is None:
            message = (
                f"{s} is not in a valid integer."
                + "Please try again from this list: \n"
                + list_subscriptions(subs)
            )
        else:
            message = (
                f"{e} is not a valid integer. "
                + "Please try again from this list: \n"
                + list_episodes(subscription, fs)
            )

        return Result.fail(message)
