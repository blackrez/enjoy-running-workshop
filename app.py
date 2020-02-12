import falcon
from falcon_multipart.middleware import MultipartMiddleware
from mapbox import StaticStyle
import fiona, json
from shapely.geometry import shape, mapping
from shapely.ops import linemerge

from logging import basicConfig, getLogger

from tempfile import NamedTemporaryFile

import uuid
import os

logger = getLogger(__name__)

class Resource(object):

    def on_post(self, req, resp):

        name = req.get_param('name')
        gps_trace = req.get_param('gpx')
        print(req.headers)
        # Read image as binary
        raw = gps_trace.file.read()
        # Retrieve filename
        #filename = image.filename

        tmp_file = NamedTemporaryFile("wb")

        tmp_file.write(raw)
        tmp_file.seek(0)

        
        layer = fiona.open(tmp_file.name, layer='tracks')
        geom = layer[0]
        tracks = shape(geom['geometry'])
        centroid = tracks.centroid
        lines = linemerge(tracks)
        tracks_final = mapping(tracks.simplify(0.002))

        print(len(json.dumps(tracks_final, separators=(',', ':'))))
        service = StaticStyle(access_token=f'{os.getenv("TOKEN_MAPBOX")}')
        response = service.image(username='mapbox', style_id='outdoors-v10', zoom=12, lon=centroid.x, lat=centroid.y, features=tracks_final, pitch=55.0, bearing=75.0)
        filename = uuid.uuid4().hex
        with open(f'/tmp/img/{filename}.png', 'wb') as output:
            output.write(response.content)
        logger.info(f'file write in {filename}')
        resp.body = f'<html><head><meta http-equiv="refresh" content="0; url=/{filename}.png"></head><body></body></html>'
        resp.status = falcon.HTTP_302
        resp.set_header('Location', f'/img/{filename}.png')


# falcon.API instances are callable WSGI apps

app = falcon.API(middleware=[MultipartMiddleware()] )
app.add_static_route('/img/', "/tmp/img/")
app.add_static_route('/html/', f'{os.getcwd()}/html/')

trace = Resource()

# things will handle post requests to the '/post_path' URL path
app.add_route('/trace', trace)

