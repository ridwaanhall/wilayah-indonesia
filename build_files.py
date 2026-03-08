import os
import subprocess


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wilayah_indonesia.settings')
    subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], check=True)


if __name__ == '__main__':
    main()
