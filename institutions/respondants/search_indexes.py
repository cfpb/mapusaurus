from haystack import indexes

from respondants.models import Institution


class InstitutionIndex(indexes.SearchIndex, indexes.Indexable):
    """Search Index associated with an institution. Allows for searching by
    name or lender id"""
    text = indexes.CharField(document=True, model_attr='name')
    text_auto = indexes.EdgeNgramField(model_attr='name')
    lender_id = indexes.CharField()
    assets = indexes.IntegerField(model_attr='assets')
    num_loans = indexes.IntegerField(model_attr='num_loans')

    def get_model(self):
        return Institution

    def index_queryset(self, using=None):
        """To account for the somewhat complicated count query, we need to add
        an "extra" annotation"""
        subquery_tail = """
            FROM hmda_hmdarecord
            WHERE hmda_hmdarecord.lender
                    = CAST(respondants_institution.agency_id AS VARCHAR(1))
                      || respondants_institution.ffiec_id"""
        return self.get_model().objects.extra(
            select={"num_loans": "SELECT COUNT(*) " + subquery_tail},
            where=["SELECT COUNT(*) > 0 " + subquery_tail])

    def prepare_lender_id(self, institution):
        return str(institution.agency_id) + institution.ffiec_id
