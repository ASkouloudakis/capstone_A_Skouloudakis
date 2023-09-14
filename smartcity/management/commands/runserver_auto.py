from django.core.management.commands.runserver import Command as RunServerCommand
import webbrowser
import threading
import time

class Command(RunServerCommand):
    help = 'Runs the server and opens a web browser automatically.'

    def handle(self, *args, **options):
        # Use a separate thread to open the web browser after a delay.
        # This allows the server to start up before the browser tries to access it.
        def open_browser():
            time.sleep(1)
            webbrowser.open('http://127.0.0.1:8000/smartcity/')

        threading.Thread(target=open_browser).start()

        # Call the original runserver command
        super().handle(*args, **options)
