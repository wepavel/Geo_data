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
            'date': self._date,
            'name': self._name,
            'uuid': self._uuid,
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


        # print(kwargs['features'][0]['properties']['date'])
        date = kwargs['features'][0]['properties']['date']
        clouds = kwargs['features'][0]['properties']['cloud']
        products = self.api.query(footprint,
                                  date=(date[0], date[1]),
                                  platformname='Sentinel-2',
                                  processinglevel='Level-2A',
                                  cloudcoverpercentage=(clouds[0], clouds[1]))
        for picture in products:
            preview = f'192.168.2.137:1060/preview/{picture}'
            result = {picture: [preview, products[picture]['generationdate']]}
        print(result)


    def create_picture(self, **kwargs) -> PictureModel:
        pass

    # def in_polygon(request):
    #     if request.method == 'POST':
    #         data = json.loads(request.body)
    #         in_polygon = False
    #
    #         # Main algorithms
    #         x = data['point'][0]
    #         y = data['point'][1]
    #         for i in range(len(data['polygon'])):
    #             xp = data['polygon'][i][0]
    #             yp = data['polygon'][i][1]
    #             xp_prev = data['polygon'][i - 1][0]
    #             yp_prev = data['polygon'][i - 1][1]
    #             if (((yp <= y and y < yp_prev) or (yp_prev <= y and y < yp)) and (
    #                     x > (xp_prev - xp) * (y - yp) / (yp_prev - yp) + xp)):
    #                 in_polygon = not in_polygon