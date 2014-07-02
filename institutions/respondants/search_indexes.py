from haystack import indexes

from respondants.models import Institution


class InstitutionIndex(indexes.SearchIndex, indexes.Indexable):
    """Search Index associated with an institution. Allows for searching by
    name or lender id"""
    text = indexes.CharField(document=True, model_attr='name')
    text_auto = indexes.EdgeNgramField(model_attr='name')
    lender_id = indexes.CharField()

    def get_model(self):
        return Institution

    def prepare_lender_id(self, institution):
        return str(institution.agency_id) + institution.ffiec_id
