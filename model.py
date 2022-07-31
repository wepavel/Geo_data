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
        pictures = []

        # uuid, title.safe, granuleidentifier, datastripidentifier




        # for i in range(2, 5):
        #     path = []
        #     path.append(cur_uuid)
        #     path.append(ident)
        #     path.append(f"{parts2[3]}_{parts1[5]}_{parts3[7]}_{parts2[7]}")
        #     path.append(f"{parts1[5]}_{parts1[2]}_B0{i}_10m.jp2")


        for picture in products:

            ident = products[picture]['identifier']
            granule = products[picture]['granuleidentifier']
            datastrip = products[picture]['datastripidentifier']

            parts1 = ident.split('_')
            parts2 = datastrip.split('_')
            parts2[7] = parts2[7].replace(parts2[7][0], '')
            parts3 = granule.split('_')


            preview = f'192.168.2.137:1060/preview/{picture}'
            download = f"/download/{picture}/{ident}/{parts2[3]}_{parts1[5]}_{parts3[7]}_{parts2[7]}/\
            {parts1[5]}_{parts1[2]}_B00_10m.jp2"


            # result = [products[picture]['generationdate'], products[picture]['title'],
            #           picture, preview, download]
            pictures.append(
                PictureModel(date=products[picture]['generationdate'], name=products[picture]['title'],
                             uuid=picture, prev=preview, download=download)
            )
        return pictures





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