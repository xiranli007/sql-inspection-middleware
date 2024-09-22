
import logging
from django.db import connection
# from pygments import highlight
# from pygments.formatters import TerminalFormatter
from pygments.formatters import NullFormatter
from pygments.lexers import SqlLexer
from sqlparse import format
from django.conf import settings
from decimal import Decimal
import time

# logger configuration
logging.basicConfig(
    filename='sql_middleware.log',
    filemode='a', 
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# define the new middleware
def new_middleware(get_response):
    
    # Threhold settings:
    SLOW_QUERY_THRESHOLD = 0.5  # in seconds
    DUPLICATE_THRESHOLD = 5     # Number of duplicate queries allowed
    N_PLUS_ONE_THRESHOLD = 10   # Max number of similar queries before flagging N+1 issue
    EXPENSIVE_JOIN_THRESHOLD = 4 # Max number of joins before flagging it as expensive

    
    def middleware(request):
        # the middleware will be fired up twice, only after it get a client request before, it hits and url and trigger a view
        # the other time is to get the response from the view and send back to the client 
        # before view
        response = get_response(request)
        # after view
        if settings.DEBUG:
            num_of_query= len(connection.queries)
            check_duplicate = set()
            total_exe_time = Decimal(0)
            duplicate_count = 0
            slow_query_count = 0
            n_plus_one_count = 0
            expensive_join_count = 0
            query_occurrences = {}
            for query in connection.queries: 
                total_exe_time += Decimal(query["time"])
                # slow query detection
                if Decimal(query["time"]) > SLOW_QUERY_THRESHOLD:
                    slow_query_count += 1
                    logger.debug(f"Slow query detected ({query['time']}s):")
                    sql_formatted = format(str(query["sql"]), reindent=True)
                    logger.debug(sql_formatted)
                # deplicate query detection
                if query['sql'] in check_duplicate:
                    duplicate_count += 1
                else:
                    check_duplicate.add(query['sql'])
                # N + 1 problem detection
                query_signature = query['sql'].split("WHERE")[0].strip()
                query_occurrences[query_signature] = query_occurrences.get(query_signature, 0) + 1
                
                # Detect expensive joins by counting JOIN occurrences
                num_joins = query['sql'].count('JOIN')
                if num_joins > EXPENSIVE_JOIN_THRESHOLD:
                    expensive_join_count += 1
                    logger.debug(f"Expensive JOIN detected: {num_joins} JOINs in the query")
                    sql_formatted = format(str(query["sql"]), reindent=True)
                    logger.debug(sql_formatted)
            
            # Check for potential N+1 problem
            for query_signature, count in query_occurrences.items():
                if count > N_PLUS_ONE_THRESHOLD:
                    n_plus_one_count += 1
                    logger.debug(f"Possible N+1 problem detected: Query executed {count} times.")
                    logger.debug(f"Query signature: {query_signature}")

            # Log SQL stats
            logger.info("==========")
            logger.info("SQL Stats")
            logger.info(f"{num_of_query} Total Queries")
            logger.info(f"Total execution time: {total_exe_time:.2f} seconds")
            logger.info(f"{duplicate_count} Duplicate Queries Detected")
            logger.info(f"{slow_query_count} Slow Queries Detected")
            logger.info(f"{n_plus_one_count} Potential N+1 Issues Detected")
            logger.info(f"{expensive_join_count} Expensive JOIN Queries Detected")
            logger.info("==========")
        
        return response
    
    return middleware