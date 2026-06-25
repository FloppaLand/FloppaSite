import asyncio
from flask import send_file, send_from_directory
from mcstatus import JavaServer
from app.utils import UserRole, get_skin_patch
from werkzeug.utils import secure_filename, safe_join
from PIL import Image
from io import BytesIO
import sqlalchemy as sa
from app import app, db
from app.models import Server, User
import os
import random


@app.route('/api/head/<string:username>')
def head(username):
  img = Image.open(safe_join(*get_skin_patch(username))).convert("RGBA")
  first_layer = img.crop((8, 8, 16, 16))
  second_layer = img.crop((40, 8, 48, 16))
  first_layer.paste(second_layer, (0, 0), second_layer)
  image_io = BytesIO()
  first_layer.save(image_io, 'PNG')
  image_io.seek(0)
  return send_file(image_io, mimetype="image/png", as_attachment=False, download_name='%s.png' % username)

@app.route('/api/skin/<string:username>')
def get_skin(username):
  username = secure_filename(username)
  path, name = get_skin_patch(username)
  return send_from_directory(path, name, as_attachment=False)



async def ping_server(ip: str) -> None:
    try:
        status = await (await JavaServer.async_lookup(ip)).async_status()
    except Exception:
        return

    print(f"{ip} - {status.latency}ms") 

async def ping_ips(ips: list[str]) -> None:
    to_process: list[str] = []

    for ip in ips:
        if len(to_process) <= 10:
            to_process.append(ip)
            continue

        await asyncio.wait({asyncio.create_task(ping_server(ip_to_ping)) for ip_to_ping in to_process})
        to_process = []

@app.route('/api/server_status')
def server_status():
  servers_data = db.session.execute(sa.select(Server)).scalars().all()

  servers = []
  for server_data in servers_data:
    server = JavaServer.lookup(server_data.ip)
    status = server.status()
    if status:
       servers.append({
        "online": True,
        "name": server_data.name,
        "description": server_data.desc,
        "ip": server_data.ip,
        "version": server_data.version,
        "modloader": server_data.modloader,
        "online_players": status.players.online,
        "max_players": status.players.max,
        "latency": status.latency,
        "server_version": status.version.name
      })
    else:
      servers.append({
       "name": server_data.name,
        "description": server_data.desc,
        "ip": server_data.ip,
        "version": server_data.version,
        "modloader": server_data.modloader
       })
    
  return {
     "servers": servers
  }

@app.route('/api/give_admin/<string:username>')
def give_admin(username):
    # This is a temporary route for testing purposes. Remove it in production
    # grant admin role to current user (for testing purposes)

    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user:
        user.role = UserRole.ADMIN
        db.session.commit()
        return f"User {username} is now an admin!"
    else:
        return f"User {username} not found!", 404