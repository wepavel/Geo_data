from sentinelsat.sentinel import SentinelAPI
import geopandas as gpd


class PictureModel:
    """."""

    def __init__(self, date: str, name: str, uuid: str, prev: str, download: str):
        """."""
        self._date = date
        self._name = name
        self._uuid = uuid
        self._prev = prev
        self._download = download

    def to_dict(self) -> dict:
        return {
            'date': self._username,
            'name': self._email,
            'uuid': self._user_id,
            'preview_url': self._prev,
            'download_url': self._download
        }

class PictureFabric:
    """."""

    def __init__(self):
        """."""
        user = 'wepaul'
        password = 'Sporopedu123'
        self.api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')


    def get_pictures(self, **kwargs: object) -> list[PictureModel]:


        # boundary = gpd.read_file(Json_dir)

        boundary = gpd.GeoDataFrame.from_features(kwargs["features"])
        footprint = None
        for i in boundary['geometry']:
            footprint = i

        #
        products = self.api.query(footprint,
                                  date=('20220109', '20220710'),
                                  platformname='Sentinel-2',
                                  processinglevel='Level-2A',
                                  cloudcoverpercentage=(0, 20))
        print(products)


    def create_picture(self, **kwargs) -> PictureModel:
        pass


