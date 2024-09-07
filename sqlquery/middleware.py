
from django.db import connection
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import SqlLexer
from sqlparse import format
from django.conf import settings
from decimal import Decimal


def new_middleware(get_response):
    
    def middleware(request):
        # the middleware will be fired up twice, only after it get a client request before, it hits and url and trigger a view
        # the other time is to get the response from the view and send back to the client 
        # before view
        response = get_response(request)
        # after view
        if settings.DEBUG:
            num_of_query= len(connection.queries)
            check_duplicate = set()
            total_exe_time = Decimal()
            for query in connection.queries: 
                total_exe_time += Decimal(query["time"])
                check_duplicate.add(query['sql'])
                sqlformated = format(str(query["sql"]), reindent=True)
                print(highlight(sqlformated, SqlLexer(), TerminalFormatter()))
        print("==========")
        print("SQL stats]")
        print(f"{num_of_query} Total Queries")
        print(f"Total execution time:{total_exe_time}")
        print(f"{num_of_query - len(check_duplicate)} Total duplicates")
        print("==========")
        
        return response
    
    return middleware