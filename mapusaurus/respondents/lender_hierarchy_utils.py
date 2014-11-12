from respondents.models import LenderHierarchy
from django.db import connection
def get_related_lenders(lender_id):
    import pdb; pdb.setTrace();
    agency = lender_id[0]
    respondent_id = lender_id[1:11]
    cursor = connection.cursor()
    query = """SELECT CONCAT(A.agency_id, A.respondent_id) AS lender_id FROM respondents_lenderhierarchy AS A, (SELECT organization_id FROM respondents_lenderhierarchy WHERE agency_id = %s AND respondent_id = %s) AS B WHERE A.organization_id = B.organization_id """
    params = [agency, respondent_id]
    cursor.execute(query, params)
    result = cursor.fetchall()
    
# query db using agency code and respondent ID
    def query_db(self, agcode, respid):
        query = "SELECT A.org, A.agency, A.respondent_id \
                 FROM respondent2org AS A, \
                 (SELECT org \
                 FROM respondent2org \
                 WHERE agency = {0} AND respondent_id = \'{1}\') AS B \
                 WHERE A.org = B.org".format(agcode, respid)

        self.cursor.execute(query)
        for row in self.cursor.fetchall():
            yield row
