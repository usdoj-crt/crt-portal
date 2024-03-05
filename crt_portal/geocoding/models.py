from django.db import models


class State(models.Model):
    """This model is used to store the state data from the US Census Bureau's TIGER/Line shapefiles

    The fields are explicitly not renamed from their census bureau names to make it easier to migrate the format in the future.

    See https://census.gov/cgi-bin/geo/shapefiles/index.php for more information.
    """

    LOAD_FROM = 'states.csv'

    name = models.CharField(max_length=255)
    statefp = models.IntegerField()
    stusps = models.CharField(max_length=2)
    intptlat = models.FloatField()
    intptlon = models.FloatField()

    def __str__(self):
        return self.name


class County(models.Model):
    """This model is used to store the county data from the US Census Bureau's TIGER/Line shapefiles

    The fields are explicitly not renamed from their census bureau names to make it easier to migrate the format in the future.

    See https://census.gov/cgi-bin/geo/shapefiles/index.php for more information.
    """

    LOAD_FROM = 'counties.csv'

    name = models.CharField(max_length=255)
    statefp = models.IntegerField()
    intptlat = models.FloatField()
    intptlon = models.FloatField()

    def __str__(self):
        return self.name


LOADABLE = [State, County]
