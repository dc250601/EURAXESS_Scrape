import util
from config import Config
import argparse
import pandas as pd

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Job Listings Scraper")

    parser.add_argument('--MicroDelay', type=int, default=1, help='Delay for micro waits')
    parser.add_argument('--ShortDelay', type=int, default=2, help='Delay for short waits')
    parser.add_argument('--LongDelay', type=int, default=10, help='Delay for long waits')

    parser.add_argument('--output', type=str, default='job_listings.csv', help='Output CSV file name')
    
    args = parser.parse_args()

    config = Config()
    config.MICRO_DELAY = args.MicroDelay
    config.SHORT_DELAY = args.ShortDelay
    config.LONG_DELAY = args.LongDelay

    driver, wait = util.setup_driver_and_page(config)

    # Tune the filter as per requirement
    #----------------------------------------------------------------------------------------------------------
    research_fields = ["Computer science","Computer science other","Computer technology",
                    "Physics","Physics other","Applied physics","Astrophysics","Computational physics"]
    Academic_levels = ["Research Support Positions","PhD Positions","Other Positions"]
    
    util.add_filters(config, driver, wait, "Research Field", research_fields)
    util.add_filters(config, driver, wait, "Academic Level", Academic_levels)
    #----------------------------------------------------------------------------------------------------------
    data = util.get_job_data(config, driver, wait)

    print("Saving data to CSV...")
    print("Closing the driver...")
    driver.quit()

    df = pd.DataFrame(data)
    df["JOB ID"] = list(map(lambda x: int(x.split("/")[-1]),list(df["Link"])))
    df.to_csv(args.output, index=False)

