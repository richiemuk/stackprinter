from google.appengine.api import memcache
from app.config.constant import *
from app.core.APIdownloader import StackExchangeDownloader
from app.core.APIdownloader import UnsupportedServiceError
import app.lib.sopy as sopy
import logging, web

class Question:
    """
    Return a Json formatted question's title
    """
    def GET(self):
        web.header('Content-type', 'application/json')
        try:
            question_id = web.input()['question']
            service = web.input()['service']
            title = memcache.get("%s%s" % (str(question_id), service))
            if title is  None:
                se_downloader = StackExchangeDownloader(service)
                title = se_downloader.get_question_title(question_id)
                memcache.add("%s%s" % (str(question_id), service), title)
            return '{"title":"%s"}' % title.replace('"','\\"')
        except Exception :
            return '{"title":"%s"}' % NOT_FOUND_ERROR
            
class Tags:
    """
    Return tags for auto completion
    """
    def GET(self):
        web.header('Content-type', 'text/plain')
        try:
            tag_filter = web.input()['q']
            service = web.input()['service']
            tags = memcache.get("%s|%s" % (tag_filter, service))
            if tags is  None:
                se_downloader = StackExchangeDownloader(service)
                tags = se_downloader.get_tags(tag_filter)
                memcache.add("%s|%s" % (tag_filter, service), tags)
            return tags
        except Exception, exception:
            return ""
            
class Quicklook:
    """
    Quicklook question
    """
    def GET(self):
        try:
            render = web.render
            question_id = web.input()['question']
            service = web.input()['service']
            
            se_downloader = StackExchangeDownloader(service)
            question = se_downloader.get_question_quicklook(question_id)

            if not question:
                return render.oops(NOT_FOUND_ERROR)
            return render.quicklook(service, question)
        except (sopy.ApiRequestError, UnsupportedServiceError), exception:
            logging.error(exception)
            return render.oops(exception.message)
        except Exception, exception:
            logging.error(exception)
            return render.oops(GENERIC_ERROR)