from respondents.models import LenderHierarchy
from django.db import connection
from collections import defaultdict

def get_related_respondents(lender_id):
    agency = lender_id[0]
    respondent_id = lender_id[1:11]
    family = defaultdict(list)
    for org, respondent in query_db_for_respondents(agency, respondent_id):
        family[org].append(respondent)
    return family.values()

# query db using agency code and respondent ID
def query_db_for_respondents(agcode, respid):
    cursor = connection.cursor()
    query = """SELECT A.organization_id, A.respondent_id FROM respondents_lenderhierarchy AS A, (SELECT organization_id FROM respondents_lenderhierarchy WHERE agency_id = %s AND respondent_id = %s) AS B WHERE A.organization_id = B.organization_id """
    params = [agcode, respid]
    cursor.execute(query, params)
    for row in cursor.fetchall():
        yield row

def get_related_lenders(lender_id):
    agency = lender_id[0]
    respondent_id = lender_id[1:11]
    family = defaultdict(list)
    for org, lender in query_db(agency, respondent_id):
        family[org].append(lender)
    return family.values()

# query db using agency code and respondent ID
def query_db(agcode, respid):
    cursor = connection.cursor()
    query = """SELECT A.organization_id, CONCAT(A.agency_id, A.respondent_id) as lender_id FROM respondents_lenderhierarchy AS A, (SELECT organization_id FROM respondents_lenderhierarchy WHERE agency_id = %s AND respondent_id = %s) AS B WHERE A.organization_id = B.organization_id """
    params = [agcode, respid]
    cursor.execute(query, params)
    for row in cursor.fetchall():
        yield row
