from threading import Thread
import time
import schedule

from protocols import MasterServer

threads: dict[str, Thread] = {}


def run_threaded(master_server: MasterServer):
    if master_server.key not in threads or not threads[master_server.key].is_alive():
        threads[master_server.key] = Thread(target=master_server.run)
        threads[master_server.key].start()


for Protocol in MasterServer.__subclasses__():
    protocol = Protocol()

    # Creates an index on protocol collection.
    protocol.create_index()

    # Create a schedule task
    schedule.every(5).minutes.do(run_threaded, protocol).run()

for job in schedule.get_jobs():
    print(f"Job: {job}, Next run: {job.next_run}, Period: {job.period}")

while 1:
    schedule.run_pending()
    time.sleep(1)
