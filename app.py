"""
Entry point for the Landbot discord bot.
"""

from google.cloud import secretmanager
import google_crc32c
from aiohttp import web

import os
import asyncio

from landbot import LandBot


def fetch_google_secret(
    project_id: str, secret_id: str, version_id: str = "latest"
) -> str:
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """
    
    client = secretmanager.SecretManagerServiceClient()

    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    response = client.access_secret_version(request={"name": name})

    # Verify checksum
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        from sys import stderr
        stderr.write("Data corruption detected.\n")
        return response


    payload = response.payload.data.decode("UTF-8")
    return payload


async def start_bot(token):
    print("Starting bot...")
    client = LandBot.create()
    await client.start(token)


async def start_server(host, port):
    """
    Create a web server because Google Cloud wants us to
    have constant connectvity on the provided port.
    """

    print(f"Starting web server on http://{host}:{port} to keep the bot alive...")
    app = web.Application()
    
    async def handle(request):
        return web.Response(text="Hello, Discord!", status=200)
    
    app.router.add_get('/', handle)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()


async def main():
    from dotenv import load_dotenv
    load_dotenv()
    
    secret_name = "DISCORD_TOKEN"
    project_id = "938558679912"
    token = os.getenv(f"{secret_name}") or fetch_google_secret(project_id, secret_name)

    if not token:
        from sys import stderr
        stderr.write(f"${secret_name} environment variable / Google secret not set!\n")
        exit(1)

    host = "0.0.0.0"
    port = os.environ.get("PORT", 8080)

    # start side-by-side the bot and the web server
    await asyncio.gather(start_bot(token), start_server(host, port))


if __name__ == "__main__":
    asyncio.run(main())