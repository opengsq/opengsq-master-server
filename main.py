from threading import Thread
import time
import schedule

from MasterServer import MasterServer

from BeamMP import BeamMP
from Factorio import Factorio
from Palworld import Palworld
from Scum import Scum

threads: dict[str, Thread] = {}


def run_threaded(master_server: MasterServer):
    if master_server.key not in threads or not threads[master_server.key].is_alive():
        threads[master_server.key] = Thread(target=master_server.run)
        threads[master_server.key].start()


schedule.every(5).minutes.do(run_threaded, BeamMP())
schedule.every(5).minutes.do(run_threaded, Factorio())
schedule.every(5).minutes.do(run_threaded, Palworld())
schedule.every(5).minutes.do(run_threaded, Palworld())
schedule.every(5).minutes.do(run_threaded, Scum())

for job in schedule.get_jobs():
    print(f"Job: {job}, Next run: {job.next_run}, Period: {job.period}")

while 1:
    schedule.run_pending()
    time.sleep(1)
