from haystack import indexes

from geo.models import Geo


class MetroIndex(indexes.SearchIndex, indexes.Indexable):
    """Search Index associated with Metropolitan Statistical Areas"""
    text = indexes.CharField(document=True, model_attr='name')
    text_auto = indexes.EdgeNgramField(model_attr='name')
    geo_type = indexes.IntegerField(model_attr='geo_type')
    year = indexes.IntegerField(model_attr='year')

    def get_model(self):
        return Geo

    def index_queryset(self, using=None):
        """Limiting this search to Metros"""
        return self.get_model().objects.filter(geo_type=Geo.METRO_TYPE)
