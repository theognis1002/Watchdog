import time


def main():
    from panel.utils import Watchdog
    from panel.models import WatchdogMetaDetails
    from django.conf import settings

    end_time = time.time() + 60 * 9
    while time.time() < end_time:
        print("Running...")
        watchdog = Watchdog()
        watchdog.run()

        meta_details = WatchdogMetaDetails.objects.get(site__pk=1)
        latest_runtime = meta_details.last_watchdog_runtime

        if time.time() + latest_runtime > end_time:
            break

        if latest_runtime < settings.SCRAPER_DELAY:
            delay = settings.SCRAPER_DELAY - latest_runtime
            print(f"Sleeping for {delay} seconds...")
            time.sleep(delay)

    print("Script finished.")


if __name__ == "__main__":
    import os

    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "watchdog.settings")

    django.setup()
    main()
