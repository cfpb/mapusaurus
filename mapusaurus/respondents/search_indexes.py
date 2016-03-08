from haystack import indexes

from respondents.models import Institution


class InstitutionIndex(indexes.SearchIndex, indexes.Indexable):
    """Search Index associated with an institution. Allows for searching by
    name or lender id"""
    text = indexes.CharField(document=True, model_attr='name')
    text_auto = indexes.EdgeNgramField(model_attr='name')
    respondent_id = indexes.CharField()
    lender_id = indexes.CharField()
    assets = indexes.IntegerField(model_attr='assets')
    num_loans = indexes.IntegerField(model_attr='num_loans')
    year = indexes.IntegerField(model_attr='year')

    def get_model(self):
        return Institution

    def index_queryset(self, using=None):
        """To account for the somewhat complicated count query, we need to add
        an "extra" annotation"""
        subquery_tail = """
            FROM hmda_hmdarecord
            WHERE hmda_hmdarecord.institution_id
                    = respondents_institution.institution_id"""
        return self.get_model().objects.extra(
            select={"num_loans": "SELECT COUNT(*) " + subquery_tail},
            where=["SELECT COUNT(*) > 0 " + subquery_tail])

    def read_queryset(self, using=None):
        """A more efficient query than the index query -- makes use of select
        related and does not include the num_loans calculation."""
        return self.get_model().objects.select_related('zip_code', 'agency')

    def prepare_respondent_id(self, institution):
        return str(institution.respondent_id)

    def prepare_lender_id(self, institution):
        return str(institution.institution_id)
