from threading import Thread
import time
import schedule

from protocols import MasterServer, BeamMP, Factorio, Palworld, Scum

threads: dict[str, Thread] = {}


def run_threaded(master_server: MasterServer):
    if master_server.key not in threads or not threads[master_server.key].is_alive():
        threads[master_server.key] = Thread(target=master_server.run)
        threads[master_server.key].start()


schedule.every(5).minutes.do(run_threaded, BeamMP()).run()
schedule.every(5).minutes.do(run_threaded, Factorio()).run()
schedule.every(5).minutes.do(run_threaded, Palworld()).run()
schedule.every(5).minutes.do(run_threaded, Scum()).run()

for job in schedule.get_jobs():
    print(f"Job: {job}, Next run: {job.next_run}, Period: {job.period}")

while 1:
    schedule.run_pending()
    time.sleep(1)
