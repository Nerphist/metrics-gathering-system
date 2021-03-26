from alembic import config, command

from db import SQLALCHEMY_DATABASE_URL


def update_db(url):
    conf = config.Config('alembic.ini')
    conf.set_section_option('alembic', 'sqlalchemy.url', url)
    command.upgrade(conf, 'head')


if __name__ == '__main__':
    update_db(SQLALCHEMY_DATABASE_URL)
