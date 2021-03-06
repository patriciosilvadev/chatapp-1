from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random

#prod_websocket_urlpattern = "path('friends/<int:id>/msg', consumers.ChatConsumer.as_asgi()),"

REPO_URL = 'https://github.com/chioffor/chatapp.git'


def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database', 'static', 'virtualenv', 'chatapp'):
        run(f'mkdir -p {site_folder}/{subfolder}')


def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run(f'cd {source_folder} && git fetch')
    else:
        run(f'git clone {REPO_URL} {source_folder}')
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run(f'cd {source_folder} && git reset --hard {current_commit}')

# def _update_chats_routing(source_folder, pattern):
#     routing_path = source_folder + '/chats/routing.py'
#     sed(routing_path,
#         'websocket_urlpatterns = .+$',
#         f'websocket_urlpatterns = [{pattern}]'
#     )

def _update_chats_template_chat_message_html(source_folder):
    # chat_message_path = source_folder + '/chats/templates/chat_message.html'
    # sed(chat_message_path,
    #     )
    pass

def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/chatapp/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path,
        'ALLOWED_HOSTS = .+$',
        f'ALLOWED_HOSTS = ["167.71.51.129", "{site_name}", "www.chatsapp.site"]'
    )
    secret_key_file = source_folder + '/chatapp/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, f'SECRET_KEY = "{key}"')
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run(f'python3 -m venv {virtualenv_folder}')
    run(f'{virtualenv_folder}/bin/pip install -r {source_folder}/requirements.txt')


def _update_static_files(source_folder):
    run(
        f'cd {source_folder}'
        ' && ../virtualenv/bin/python manage.py collectstatic --noinput'
    )

def _update_database(source_folder):
    run(
        f'cd {source_folder}'
        ' && ../virtualenv/bin/python manage.py migrate --noinput'
    )

def deploy():
    site_folder = f'/home/{env.user}/sites/{env.host}'
    source_folder = site_folder + '/chatapp'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    #_update_chats_routing(source_folder, prod_websocket_urlpattern)
    #_update_chats_template_chat_message_html()
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)

