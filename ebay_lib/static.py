from . import func
from chalice import Chalice, Response
def main_css():
    template = get_template('main.css')
    return Response(
        body = template.render(
        ),
        status_code = 200,
        headers = {
            "Content-Type": "text/css"
        }
    )

def reset_css():

    template = get_template('reset.css')
    return Response(
        body = template.render(
        ),
        status_code = 200,
        headers = {
            "Content-Type": "text/css"
        }
    )

def get_template(template):
    env = func.get_env()
    return env.get_template(template)


def sitemap():
    template = get_template('sitemap.xml')
    return Response(

        body = template.render(
            queries = ["DJI","Drones","Mavic", "DJI Maciv PRO","Spark" ,"Parrot","Hubsan","GoPro"]
        ),
        status_code = 200,
        headers = {
            "Content-Type": "text/xml"
        }
    )

def favicon():
    return Response(body="no", status_code=404, headers={'Content-Type':'text/html'})
