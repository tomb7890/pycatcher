from error import BadUserInputError
from podcasts import decorate_results, search_for_podcast_and_decorate_results


def downloaded_episodes(subscription, fs):
    episodes = subscription.episodes()
    de = []
    for e in episodes:
        if subscription.database.find(e.guid):
            filename = subscription.database.get(e)
            if fs.path_exists(filename):
                de.append(e)
    return de


def search_for_podcast(args):
    return search_for_podcast_and_decorate_results(args.search)


def subscribe_to_podcast(args, registry, api):
    results = None
    try:
        searchterm = args.subscribe[0]
        results = api.search(searchterm)
        index = int(args.subscribe[1]) - 1
        feedurl = api.feed_url(index)
        collectionname = api.collection_name(index)
        registry.register(feedurl, collectionname)
    except ValueError:
        message = (
            f"{args.subscribe[1]} is not a valid integer. "
            + "Please try again from this list: \n"
            + decorate_results(results)
        )
        raise BadUserInputError(message)

    except IndexError:
        message = (
            f"{args.subscribe[1]} is not in the correct range. "
            + "Please try again from this list: \n"
            + decorate_results(results)
        )
        raise BadUserInputError(message)


def list_episodes(fs, args, subs):
    try:
        s = args.listepisodes
        si = int(s) - 1
        subscription = subs[si]
        episodes = downloaded_episodes(subscription, fs)
        return list_elements(episodes)

    except ValueError:
        message = (
            f"{s} is not a valid integer. "
            + "Please try again from this list: \n"
            + str(list_subscriptions(subs))
        )
        raise BadUserInputError(message)

    except IndexError:
        message = (
            f"{s} is not in the correct range. "
            + "Please try again from this list: \n"
            + str(list_subscriptions(subs))
        )
        raise BadUserInputError(message)


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
        si = int(s) - 1
        subscription = subs[si]
        subscription.database.load()
        episodes = downloaded_episodes(subscription, fs)

        e = args.play[1]
        ei = int(e) - 1
        episode = episodes[ei]
        fullpath = subscription.database.get(episode)
        player.play(fullpath)

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
                + _list_episodes(subscription, fs)
            )

        raise BadUserInputError(message)

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
                + _list_episodes(subscription, fs)
            )

        raise BadUserInputError(message)


def _list_episodes(subscription, fs):
    episodes = downloaded_episodes(subscription, fs)
    return list_elements(episodes)
