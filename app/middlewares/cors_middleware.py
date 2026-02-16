import os
from app.config.config import DOMAIN_URLS
import falcon

class CORSMiddleware:
    def __init__(self):
        self.allowed_origins = [url.strip() for url in DOMAIN_URLS if url]

    def process_request(self, req, resp):
        if req.method == "OPTIONS":
            resp.status = falcon.HTTP_200
            resp.complete = True

    def process_response(self, req, resp, resource, req_succeeded):
        origin = req.get_header("Origin")

        if origin and origin in self.allowed_origins:
            resp.set_header("Access-Control-Allow-Origin", origin)

        resp.set_header(
            "Access-Control-Allow-Headers",
            "Authorization, Content-Type"
        )
        resp.set_header(
            "Access-Control-Allow-Methods",
            "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        resp.set_header("Access-Control-Allow-Credentials", "true")
