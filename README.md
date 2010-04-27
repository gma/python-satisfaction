python-satisfaction
===================

This is a Python wrapper around the [getsatisfaction API](http://getsatisfaction.com/developers/ "Developer Documentation"). It's at an early stage of development, but is already useful for retrieving messages.

An example is probably the best way to give you a feel for progress. Let's investigate Twitter...

    >>> import satisfaction
    >>> company = satisfaction.Company('twitter')
    >>> for product in company.products:
    ...     print '%s (%s topics)' % (product.title, product.topic_count)
    ... 
    Poptweets (0 topics)
    Su.pr (331 topics)
    Shopify Tweeter (1 topics)
    Show Last Tweet (0 topics)
    Brizzly (1157 topics)
    Home/Office Security (282 topics)
    twitter account (1 topics)
    Quoqu.com: What are you trading? (2 topics)
    Portal (1 topics)
    TWIToshirt (5 topics)
    TweetTrak (14 topics)
    API (899 topics)
    Search (1559 topics)
    twitpol (3 topics)
    Twittercal (4 topics)
    twitter.com (3730 topics)
    Dipity.com (287 topics)
    Twitter (21195 topics)
    I want Sandy (1575 topics)
    Twitter on Mobile Web (1528 topics)

There are quite a few products in getsatisfaction that are associated with Twitter (though they are not all Twitter's products; Get Satisfaction allows a product to be associated with multiple companies). Note that `company.products` is an iterable, not a list.

If we were to retrieve all 899 topics relating to the API product we'd need to request lots of pages from the getsatisfaction REST API (up to 30 topics are retrieved per HTTP request). However, because `product.topics` is an iterable that loads the topics on demand, we can query the API efficiently, making no more HTTP requests than we need.

For example, if we're only interested in the first 4 topics we can use the `enumerate()` built-in function to break out of the loop at the right moment. This example will only request the first page of topics relating to the Twitter API:

    >>> api = satisfaction.Product('twitter_api')
    >>> for i, topic in enumerate(api.topics):
    ...     if i == 4: break
    ...     print '%s...' % topic.title[0:40]
    ... 
    Problems with Norwegian characters ÆØÅ in search...
    Twitter's Facebook App is Completely Broken...
    Username Clashes With Twitter API Product...
    I cant change my background - too many tweets for last 36 ho...

Note that we instantiated the `api` object by passing its identifier ('twitter_api') into a new instance of the `Product` class. We could just as easily have used the existing `product` object from the previous example, but I wanted to demonstrate how to reference a product by combining the brand and product name into a lower case string.

A more flexible alternative to the `enumerate()` function is the `itertools.islice()` function:

    >>> import itertools
    >>> for topic in itertools.islice(api.topics, 0, 2):
    ...     print '%s (%s replies)' % (topic.content[0:30], topic.reply_count)
    ...
    It is impossible to make searc (5 replies)
    It seams like the API connecti (11 replies)

If you really want to go ahead and load all the topics, you can convert the iterable into a list (e.g. `list(product.topics)`), but be aware that this issues as many requests to the API as are required to grab all the topics, and Get Satisfaction might not like you very much if you do this kind of thing for sustained periods.

You can get at a topic's replies in a similar manner:

    >>> for topic in itertools.islice(api.topics, 0, 2):
    ...     print 'Topic: %s...' % topic.title[0:50]
    ...     for reply in topic.replies:
    ...         print '  +->  %s...' % reply.content[0:40]
    ...     print
    ... 
    Topic: Problems with Norwegian characters ÆØÅ in search...
      +->  Yep, searches and hash tags with "Å" see...
      +->  A and Å are NOT interchangeable. Two dis...
      +->  Å ja, absolutt. I meant in the twitter s...
      +->  The clickability of hashtags also gets c...
      +->  I use the hashtag #Kjøttfri (Meat free),...
    
    Topic: Twitter's Facebook App is Completely Broken...
      +->  Please repair this, Twitter!...
      +->  Please Fix Twitter or Facebook. This is ...
      +->  yes....please fix this....i work from a ...
      +->  Me 2.....
      +->  Twitter - issues happen, but you can't j...
      +->  This doesn't appear to be affecting othe...
      +->  I received this today... so they're at l...
      +->  Trying to add the official Twitter Faceb...
      +->  It's incredible how long it's taking the...
      +->  As of today, 4/26--still not fixed. fyi....
      +->  Good job twitter. Starting to go the way...

To Do
-----

There's plenty of meta data revealed by the Get Satisfaction API that python-satisfaction doesn't know how to access (e.g. dates, relationships between people and the messages they've written, etc.), and adding support for that information is at the top of the list.

I'll be adding what I need and no more though, so if you feel the need for some extra info, get stuck in and fork the project.

You can also create messages with the Get Satisfaction API, and it might be quite nice to add support for that too. It's not high on my priority list right now, but I'd happily accept pull requests with patches (but see the next section on how to contribute).

Contributing
------------

If you're interested in helping out, fully tested improvements will be gratefully accepted. Extra points will be awarded if you:

1. Chat with me first about any additions/modifications that you're considering making to the API. If we both agree on the direction the API should take then the effort required to merge your changes will be reduced for both of us.
2. Write your code test first.
3. Add yourself to the AUTHORS file.
4. Commit your changes to a fork of my repository, then send me a pull request.
